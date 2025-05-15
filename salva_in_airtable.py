import os
from pyairtable import Table
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("OFFERTE")  # es. "Offerte"

def salva_offerta_in_airtable(dati: dict) -> dict:
    try:
        table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)

        # Adatta i nomi dei campi a quelli usati nella tabella Airtable
        record = {
            "Fornitore": dati.get("fornitore"),
            "Nome Offerta": dati.get("nome_offerta"),
            "Tariffa": dati.get("tariffa"),
            "Prezzo €/kWh": dati.get("prezzo_kwh"),
            "Spread": dati.get("spread"),
            "Costo fisso": dati.get("costo_fisso"),
            "Validità": dati.get("validita"),
            "Vincoli": dati.get("vincoli"),
        }

        return table.create(record)

    except Exception as e:
        return {"errore": str(e)}
