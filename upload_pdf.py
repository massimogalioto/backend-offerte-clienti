import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
from tempfile import NamedTemporaryFile

router = APIRouter()

@router.post("/upload-cte")
async def upload_cte_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Il file deve essere un PDF")

    try:
        # Salva temporaneamente il file
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(await file.read())
            temp_path = temp.name

        # Estrai testo dal PDF
        reader = PdfReader(temp_path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

        # Elimina il file temporaneo
        os.remove(temp_path)

        if not text.strip():
            raise HTTPException(status_code=422, detail="Non è stato possibile estrarre testo dal PDF")

        return JSONResponse({
            "filename": file.filename,
            "contenuto_testo": text[:5000]  # opzionalmente limitiamo preview
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'elaborazione: {str(e)}")
