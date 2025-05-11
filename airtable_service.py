import os
from pyairtable import Table
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TBL_OFFERTE = os.getenv("AIRTABLE_OFFERTE_TABLE")
TBL_MERCATO = os.getenv("AIRTABLE_MERCATO_TABLE")

def get_offerte(tipo_fornitura):
    table = Table(API_KEY, BASE_ID, TBL_OFFERTE)
    return table.all(formula=f"{{Tipo fornitura}} = '{tipo_fornitura}'")

def get_prezzo_mercato(tipo_fornitura, data_str):
    table = Table(API_KEY, BASE_ID, TBL_MERCATO)
    mese = datetime.strptime(data_str, "%Y-%m-%d").strftime("%Y-%m-01")
    records = table.all(formula=f"AND({{Tipo fornitura}} = '{tipo_fornitura}', {{Mese}} = '{mese}')")
    if not records:
        raise Exception(f"Nessun prezzo trovato per {tipo_fornitura} nel mese {mese}")
    return float(records[0]["fields"].get("Prezzo medio €/kWh", 0))