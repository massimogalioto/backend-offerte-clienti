from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from estrai_dati_cte import estrai_dati_cte

router = APIRouter()

class CTETextRequest(BaseModel):
    testo: str

@router.post("/analizza-cte")
def analizza_cte(data: CTETextRequest):
    if not data.testo.strip():
        raise HTTPException(status_code=400, detail="Testo CTE mancante")

    risultato = estrai_dati_cte(data.testo)
    return risultato
