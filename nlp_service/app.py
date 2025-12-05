from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="NLP Classification Service")


class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    icpc_code: Optional[str]
    icd_code: Optional[str]
    icpc_confidence: float
    icd_confidence: float


@app.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest):
    text = req.text.lower()

    # Дуже примітивний rule-based класифікатор
    rules = [
        (["голова", "головний біль", "мігрень"], "N01", "R51", 0.8, 0.8),
        (["кашель"], "R05", "R05", 0.8, 0.8),
        (["нудота", "блювота"], "D09", "R11", 0.7, 0.7),
        (["живіт", "абдомінальний біль", "біль в животі"], "D01", "R10", 0.7, 0.7),
        (["гарячка", "температура", "лихоманка"], "A03", "R50", 0.7, 0.7),
    ]

    for keywords, icpc, icd, icpc_conf, icd_conf in rules:
        if any(word in text for word in keywords):
            return {
                "icpc_code": icpc,
                "icd_code": icd,
                "icpc_confidence": icpc_conf,
                "icd_confidence": icd_conf,
            }

    # Якщо нічого не знайшли
    return {
        "icpc_code": "UNSPECIFIED",
        "icd_code": "UNSPECIFIED",
        "icpc_confidence": 0.0,
        "icd_confidence": 0.0,
    }
