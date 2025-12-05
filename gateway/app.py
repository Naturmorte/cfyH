import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

NLP_SERVICE_URL = os.getenv("NLP_SERVICE_URL", "http://nlp-service:8001")
COMPLAINTS_SERVICE_URL = os.getenv("COMPLAINTS_SERVICE_URL", "http://complaints-service:8002")

app = FastAPI(title="Health Diary API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ComplaintCreate(BaseModel):
    user_id: str
    text: str


class Complaint(BaseModel):
    id: int
    user_id: str
    text: str
    icpc_code: Optional[str] = None
    icd_code: Optional[str] = None
    created_at: str


class HealthIndicators(BaseModel):
    user_id: str
    total_complaints: int
    health_score: int
    last_complaint_date: Optional[str] = None


async def get_http_client():
    async with httpx.AsyncClient(timeout=5.0) as client:
        yield client


@app.post("/api/complaints", response_model=Complaint)
async def create_complaint(
    payload: ComplaintCreate,
    client: httpx.AsyncClient = Depends(get_http_client),
):
    # 1. NLP-класифікація
    try:
        nlp_resp = await client.post(
            f"{NLP_SERVICE_URL}/classify",
            json={"text": payload.text},
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="NLP service unavailable") from e

    if nlp_resp.status_code != 200:
        raise HTTPException(status_code=503, detail="NLP service error")

    nlp_data = nlp_resp.json()

    # 2. Збереження скарги в Complaints Service
    try:
        comp_resp = await client.post(
            f"{COMPLAINTS_SERVICE_URL}/internal/complaints",
            json={
                "user_id": payload.user_id,
                "text": payload.text,
                "icpc_code": nlp_data.get("icpc_code"),
                "icd_code": nlp_data.get("icd_code"),
            },
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="Complaints service unavailable") from e

    if comp_resp.status_code != 200:
        raise HTTPException(status_code=comp_resp.status_code, detail="Complaints service error")

    return comp_resp.json()


@app.get("/api/complaints", response_model=List[Complaint])
async def list_complaints(
    user_id: str,
    client: httpx.AsyncClient = Depends(get_http_client),
):
    try:
        resp = await client.get(
            f"{COMPLAINTS_SERVICE_URL}/internal/complaints",
            params={"user_id": user_id},
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="Complaints service unavailable") from e

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Complaints service error")

    return resp.json()


@app.get("/api/health-indicators", response_model=HealthIndicators)
async def health_indicators(
    user_id: str,
    client: httpx.AsyncClient = Depends(get_http_client),
):
    try:
        resp = await client.get(
            f"{COMPLAINTS_SERVICE_URL}/internal/complaints",
            params={"user_id": user_id},
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="Complaints service unavailable") from e

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Complaints service error")

    complaints = resp.json()

    total = len(complaints)
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)

    complaints_last30 = 0
    last_dt: Optional[datetime] = None
    last_date_str: Optional[str] = None

    for c in complaints:
        created_str = c.get("created_at")
        if not created_str:
            continue
        try:
            dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        except Exception:
            continue

        if last_dt is None or dt > last_dt:
            last_dt = dt
            last_date_str = dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

        if dt >= thirty_days_ago:
            complaints_last30 += 1

    health_score = max(0, 100 - complaints_last30)

    return {
        "user_id": user_id,
        "total_complaints": total,
        "health_score": health_score,
        "last_complaint_date": last_date_str,
    }
