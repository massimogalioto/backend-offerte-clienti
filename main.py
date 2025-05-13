from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from confronto import confronta_offerte
from ai_mesi import chiedi_ai_mesi
import os

app = FastAPI()

# CORS: accetta richieste dal frontend (modifica il dominio se pubblichi su Vercel )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione: ["https://madonie-front.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modello dei dati in input
class BollettaInput(BaseModel):
    kwh_totali: float
    mesi_bolletta: int
    spesa_materia_energia: float
    tipo_fornitura: str  # "Luce" o "Gas"
    data_riferimento: str  # formato "YYYY-MM-DD"

# Endpoint protetto con chiave API
@app.post("/confronta")
def confronta_bolletta(bolletta: BollettaInput, x_api_key: str = Header(None)):
    secret_key = os.getenv("API_SECRET_KEY")

    if secret_key and x_api_key != secret_key:
        raise HTTPException(status_code=401, detail="Chiave API non valida")

    try:
        risultato = confronta_offerte(bolletta)
        return {"offerte": risultato}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
