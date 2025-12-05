import os
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_PATH = os.getenv("COMPLAINTS_DB_PATH", "/data/complaints.db")

app = FastAPI(title="Complaints Service")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# Ініціалізація БД
conn = get_connection()
conn.execute(
    """
CREATE TABLE IF NOT EXISTS complaints (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  text TEXT NOT NULL,
  icpc_code TEXT,
  icd_code TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""
)
conn.commit()
conn.close()


class ComplaintIn(BaseModel):
    user_id: str
    text: str
    icpc_code: Optional[str] = None
    icd_code: Optional[str] = None


class ComplaintOut(BaseModel):
    id: int
    user_id: str
    text: str
    icpc_code: Optional[str] = None
    icd_code: Optional[str] = None
    created_at: str


def row_to_dict(row: sqlite3.Row) -> dict:
    created_raw = row["created_at"]
    iso_created = created_raw
    # SQLite CURRENT_TIMESTAMP -> "YYYY-MM-DD HH:MM:SS"
    try:
        dt = datetime.strptime(created_raw, "%Y-%m-%d %H:%M:%S")
        iso_created = dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    except Exception:
        pass

    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "text": row["text"],
        "icpc_code": row["icpc_code"],
        "icd_code": row["icd_code"],
        "created_at": iso_created,
    }


@app.post("/internal/complaints", response_model=ComplaintOut)
def create_complaint(payload: ComplaintIn):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO complaints (user_id, text, icpc_code, icd_code) VALUES (?, ?, ?, ?)",
        (payload.user_id, payload.text, payload.icpc_code, payload.icd_code),
    )
    conn.commit()
    complaint_id = cur.lastrowid

    cur.execute(
        "SELECT id, user_id, text, icpc_code, icd_code, created_at FROM complaints WHERE id = ?",
        (complaint_id,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=500, detail="Failed to fetch created complaint")

    return row_to_dict(row)


@app.get("/internal/complaints", response_model=List[ComplaintOut])
def get_complaints(user_id: Optional[str] = None):
    conn = get_connection()
    cur = conn.cursor()

    if user_id:
        cur.execute(
            "SELECT id, user_id, text, icpc_code, icd_code, created_at "
            "FROM complaints WHERE user_id = ? ORDER BY created_at ASC",
            (user_id,),
        )
    else:
        cur.execute(
            "SELECT id, user_id, text, icpc_code, icd_code, created_at "
            "FROM complaints ORDER BY created_at ASC"
        )

    rows = cur.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]
