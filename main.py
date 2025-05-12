from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from confronto import confronta_offerte
import os
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
@app.get("/env")
def leggi_variabili():
    return {
        "AIRTABLE_API_KEY": os.getenv("AIRTABLE_API_KEY"),
        "AIRTABLE_BASE_ID": os.getenv("AIRTABLE_BASE_ID"),
        "OFFERTE": os.getenv("AIRTABLE_OFFERTE_TABLE"),
        "MERCATO": os.getenv("AIRTABLE_MERCATO_TABLE"),
    }        
