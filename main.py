from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from confronto import confronta_offerte
from fastapi import Header
app = FastAPI()

# Nuova struttura input: basata sui dati reali della bolletta
class BollettaInput(BaseModel):
    kwh_totali: float                     # Energia totale della bolletta (es. 450 kWh)
    mesi_bolletta: int                    # Numero di mesi coperti dalla bolletta (es. 2)
    spesa_materia_energia: float          # Spesa totale per la voce "materia energia"
    tipo_fornitura: str                   # "Luce" o "Gas"
    data_riferimento: str                 # es. "2025-04-01"

@app.post("/confronta")
def confronta_bolletta(bolletta: BollettaInput, x_api_key: str = Header(None)):
    import os
    if x_api_key != os.getenv("API_SECRET_KEY"):
        raise HTTPException(status_code=401, detail="Chiave API non valida")

    try:
        risultato = confronta_offerte(bolletta)
        return {"offerte": risultato}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
