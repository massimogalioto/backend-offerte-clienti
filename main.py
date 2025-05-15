from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from confronto import confronta_offerte
from ai_mesi import chiedi_ai_mesi
import os

app = FastAPI(
    title="Servizio confronto bollette",
    description="API che confronta offerte luce/gas e calcola il numero di mesi da un intervallo testuale tramite AI.",
    version="1.0.0"
)

# CORS (in produzione metti il dominio del frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Es: ["https://madonie-front.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 Modelli dati
class BollettaInput(BaseModel):
    kwh_totali: float
    mesi_bolletta: int
    spesa_materia_energia: float
    tipo_fornitura: str  # "Luce" o "Gas"
    data_riferimento: str  # formato "YYYY-MM-DD"

class PeriodoRequest(BaseModel):
    periodo: str

# 🔐 Endpoint confronto con chiave API
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

# 🧠 Endpoint AI per calcolo mesi
@app.post("/calcola-mesi", summary="Calcola i mesi da un intervallo testuale")
def calcola_mesi(body: PeriodoRequest):
    mesi = chiedi_ai_mesi(body.periodo)
    if mesi is None:
        return {"error": "Impossibile determinare il numero di mesi"}
    return {"mesi": mesi}
