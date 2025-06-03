
# ✅ Base image con Python e Linux (slim ma compatibile)
FROM python:3.11-slim

# ✅ Imposta la directory di lavoro
WORKDIR /app

# ✅ Installa i pacchetti di sistema necessari
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ✅ Copia tutti i file del tuo progetto dentro l'immagine
COPY . .

# ✅ Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Esponi la porta dell’app FastAPI (default uvicorn)
EXPOSE 8000

# ✅ Comando per avviare l'app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
