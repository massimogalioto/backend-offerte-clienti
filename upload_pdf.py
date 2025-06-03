import os
import pytesseract  # 🧠 #nuova modifica (2025-05-30)
from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from PyPDF2 import PdfReader
from tempfile import NamedTemporaryFile
from PIL import Image  # 🧠 #nuova modifica (2025-05-30)
from pdf2image import convert_from_path  # 🧠 #nuova modifica (2025-05-30)
from estrai_dati_bolletta import estrai_dati_bolletta
from estrai_dati_cte import estrai_dati_offerta_cte
from confronto import confronta_offerte
from datetime import date

def data_oggi_iso():
    return date.today().isoformat()

router = APIRouter()

# 📄 Funzione OCR + estrazione testo #nuova modifica (2025-05-30)
def estrai_testo_pdf_con_ocr(percorso_pdf):
    testo = ""
    try:
        reader = PdfReader(percorso_pdf)
        testo = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    except:
        pass

    if not testo.strip():
        immagini = convert_from_path(percorso_pdf)
        for img in immagini:
            testo += pytesseract.image_to_string(img)

    return testo


# 📄 Endpoint CTE
@router.post("/upload-cte")
async def upload_cte_pdf(file: UploadFile = File(...), x_api_key: str = Header(None)):
    secret_key = os.getenv("API_SECRET_KEY")
    if secret_key and x_api_key != secret_key:
        raise HTTPException(status_code=401, detail="Chiave API non valida")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Il file deve essere un PDF")

    try:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            file.file.seek(0)
            temp.write(file.file.read())
            temp_path = temp.name

        testo = estrai_testo_pdf_con_ocr(temp_path)  # 🧠 #nuova modifica (2025-05-30)
        os.remove(temp_path)

        if not testo.strip():
            raise HTTPException(status_code=422, detail="Non è stato possibile estrarre testo dal PDF")

        dati = estrai_dati_offerta_cte(testo)

        return {
            "filename": file.filename,
            "output_ai": dati
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'elaborazione: {str(e)}")


# 🧾 Endpoint Bolletta
@router.post("/upload-bolletta")
async def upload_bolletta(file: UploadFile = File(...), x_api_key: str = Header(None)):
    secret_key = os.getenv("API_SECRET_KEY")
    if secret_key and x_api_key != secret_key:
        raise HTTPException(status_code=401, detail="Chiave API non valida")

    try:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            file.file.seek(0)
            temp_file.write(file.file.read())
            temp_path = temp_file.name

        testo = estrai_testo_pdf_con_ocr(temp_path)  # 🧠 #nuova modifica (2025-05-30)
        os.remove(temp_path)

        if not testo.strip():
            raise HTTPException(status_code=422, detail="Errore: PDF privo di testo estraibile")

        dati = estrai_dati_bolletta(testo)
        if "errore" in dati:
            return {
                "errore": "Estrazione fallita",
                "dettagli": dati.get("output")
            }

        campi_obbligatori = [
            "kwh_totali", "mesi_bolletta", "spesa_materia_energia",
            "tipo_fornitura", "tipologia_cliente"
        ]
        mancanti = [campo for campo in campi_obbligatori if campo not in dati or dati[campo] is None]

        if mancanti:
            return {
                "errore": "Campo mancante nella risposta AI",
                "mancanti": mancanti,
                "output_ai": dati
            }

        confronto_input = {
            "kwh_totali": dati["kwh_totali"],
            "mesi_bolletta": dati["mesi_bolletta"],
            "spesa_materia_energia": dati["spesa_materia_energia"],
            "tipo_fornitura": dati["tipo_fornitura"],
            "tipologia_cliente": dati["tipologia_cliente"],
            "data_riferimento": data_oggi_iso()
        }

        offerte = confronta_offerte(confronto_input)

        return {
            "bolletta": dati,
            "offerte": offerte
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
