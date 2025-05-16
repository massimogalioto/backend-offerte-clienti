import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
from tempfile import NamedTemporaryFile
from estrai_dati_bolletta import estrai_dati_bolletta
from confronto import confronta_offerte

router = APIRouter()

# 📄 Estrazione testo da CTE
@router.post("/upload-cte")
async def upload_cte_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Il file deve essere un PDF")

    try:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(await file.read())
            temp_path = temp.name

        reader = PdfReader(temp_path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        os.remove(temp_path)

        if not text.strip():
            raise HTTPException(status_code=422, detail="Non è stato possibile estrarre testo dal PDF")

        return JSONResponse({
            "filename": file.filename,
            "contenuto_testo": text[:5000]
        })

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
            contents = await file.read()
            temp_file.write(contents)
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
            "consumo_kwh", "mesi", "spesa_materia_energia",
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
            "kwh_totali": dati["consumo_kwh"],
            "mesi_bolletta": dati["mesi"],
            "spesa_materia_energia": dati["spesa_materia_energia"],
            "tipo_fornitura": dati["tipo_fornitura"],
            "tipologia_cliente": dati["tipologia_cliente"],
            "data_riferimento": "2025-04-01"  # temporanea
        }

        offerte = confronta_offerte(confronto_input)

        return {
            "bolletta": dati,
            "offerte": offerte
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
