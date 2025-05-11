from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from confronto import confronta_offerte

app = FastAPI()

class BollettaInput(BaseModel):
    consumo_kwh: float
    tipo_fornitura: str  # "Luce" o "Gas"
    data_riferimento: str  # formato "YYYY-MM-DD"

@app.post("/confronta")
def confronta_bolletta(bolletta: BollettaInput):
    try:
        risultato = confronta_offerte(bolletta)
        return {"offerte": risultato}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))