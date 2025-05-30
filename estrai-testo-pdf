from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
from tempfile import NamedTemporaryFile
import os

router = APIRouter()

@router.post("/estrai-testo-pdf", summary="Estrai testo da un PDF", tags=["Utility"])
async def estrai_testo_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Il file deve essere un PDF")

    try:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            file.file.seek(0)
            temp.write(file.file.read())
            temp_path = temp.name

        reader = PdfReader(temp_path)
        testo = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        os.remove(temp_path)

        if not testo.strip():
            raise HTTPException(status_code=422, detail="Testo non estratto dal PDF")

        return JSONResponse({
            "filename": file.filename,
            "contenuto_testo": testo[:10000]  # Limite per evitare overflow
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")
