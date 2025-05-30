import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
from tempfile import NamedTemporaryFile
from estrai_dati_bolletta import estrai_dati_bolletta # ✅ estrae dati bolletta
from estrai_dati_cte import estrai_dati_offerta_cte  # ✅ estrae dati cte
from confronto import confronta_offerte
from datetime import date

from pdf2image import convert_from_path #nuovo per lettura anche scansioni
from PIL import Image #nuovo per lettura anche scansioni
import pytesseract #nuovo per lettura anche scansioni

def data_oggi_iso():
    return date.today().isoformat()
def estrai_testo_con_ocr(pdf_path, lang='ita'):
    """
    Estrae testo da PDF scansionati (immagine) usando OCR (Tesseract).
    """
    try:
        immagini = convert_from_path(pdf_path)
        testo_ocr = ""
        for pagina in immagini:
            testo_ocr += pytesseract.image_to_string(pagina, lang=lang)
        return testo_ocr.strip()
    except Exception as e:
        return ""
router = APIRouter()

# 📄 Estrazione testo da CTE
@router.post("/upload-cte")
async def upload_cte_pdf(file: UploadFile = File(...), x_api_key: str = Header(None)):
    secret_key = os.getenv("API_SECRET_KEY")
    if secret_key and x_api_key != secret_key:
        raise HTTPException(status_code=401, detail="Chiave API non valida")
    
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Il file deve essere un PDF")

    try:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            #temp.write(await file.read())
            file.file.seek(0)  # torna all'inizio del file
            temp.write(file.file.read())
            temp_path = temp.name

        reader = PdfReader(temp_path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        os.remove(temp_path)

        if not text.strip():
            raise HTTPException(status_code=422, detail="Non è stato possibile estrarre testo dal PDF")

         # ✅ Analizza con OpenAI
        dati = estrai_dati_offerta_cte(text)

        return {
            "filename": file.filename,
            "output_ai": dati  # ✅ Dati strutturati da usare nel frontend
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'elaborazione: {str(e)}")


# 🧾 Estrazione + confronto da bolletta PDF
@router.post("/upload-bolletta")
async def upload_bolletta(file: UploadFile = File(...), x_api_key: str = Header(None)):
    secret_key = os.getenv("API_SECRET_KEY")
    if secret_key and x_api_key != secret_key:
        raise HTTPException(status_code=401, detail="Chiave API non valida")

    try:
        with NamedTemporaryFile(delete=False) as temp_file:
            file.file.seek(0)  # torna all'inizio del file
            temp_file.write(file.file.read())
            temp_path = temp_file.name

        reader = PdfReader(temp_path)
        testo = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        os.remove(temp_path)

        dati = estrai_dati_bolletta(testo)
        if "errore" in dati:
            return {
                "errore": "Estrazione fallita",
                "dettagli": dati.get("output")
            }

        # ✅ Verifica che tutti i campi necessari siano presenti
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
            "data_riferimento": data_oggi_iso() # la data odierna, la CTE per il confronto deve essere valida ad oggi
        }

        offerte = confronta_offerte(confronto_input)

        return {
            "bolletta": dati,
            "offerte": offerte
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
