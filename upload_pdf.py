from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from PyPDF2 import PdfReader
from tempfile import NamedTemporaryFile
from estrai_dati_bolletta import estrai_dati_bolletta
from confronto import confronta_offerte
import os

router = APIRouter()

@router.post("/upload-bolletta")
async def upload_bolletta(file: UploadFile = File(...), x_api_key: str = Header(None)):
    secret_key = os.getenv("API_SECRET_KEY")
    if secret_key and x_api_key != secret_key:
        raise HTTPException(status_code=401, detail="Chiave API non valida")

    try:
        # 📄 Salva temporaneamente il file PDF
        with NamedTemporaryFile(delete=False) as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_path = temp_file.name

        # 📖 Estrai testo dal PDF
        reader = PdfReader(temp_path)
        testo = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

        # 🤖 Estrai i dati strutturati con OpenAI
        dati = estrai_dati_bolletta(testo)

        if "errore" in dati:
            return {"errore": "Estrazione fallita", "dettagli": dati.get("output")}

        # ✅ Chiama confronto offerte con i dati estratti
        confronto_input = {
            "kwh_totali": dati["consumo_kwh"],
            "mesi_bolletta": dati["mesi"],
            "spesa_materia_energia": dati["spesa_materia_energia"],
            "tipo_fornitura": dati["tipo_fornitura"],
            "tipologia_cliente": dati["tipologia_cliente"],
            "data_riferimento": "2025-04-01"  # default, o potremmo inferirla in futuro
        }

        offerte = confronta_offerte(confronto_input)

        return {
            "bolletta": dati,
            "offerte": offerte
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
