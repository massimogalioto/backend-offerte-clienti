import os
from pyairtable import Table
from dotenv import load_dotenv
from datetime import datetime
from urllib.parse import quote

load_dotenv()

API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TBL_OFFERTE = os.getenv("AIRTABLE_OFFERTE_TABLE")
TBL_MERCATO = os.getenv("AIRTABLE_MERCATO_TABLE")

def get_offerte(tipo_fornitura, tipologia_cliente):
    table = Table(API_KEY, BASE_ID, TBL_OFFERTE)
    formula = f"AND({{Tipo fornitura}} = '{tipo_fornitura}', {{Tipologia cliente}} = '{tipologia_cliente}')"
    return table.all(formula=formula)

#modificato (2025-06-03)
def get_prezzo_mercato(tipo_fornitura, data_str):
    table = Table(API_KEY, BASE_ID, TBL_MERCATO)
    target_date = datetime.strptime(data_str, "%Y-%m-%d")

    # Recupera tutti i record per tipo fornitura
    formula_fornitura = f"{{Tipo fornitura}} = '{tipo_fornitura}'"
    tutti_record = table.all(formula=formula_fornitura)

    # Filtra solo quelli con 'Mese' >= data richiesta
    record_validi = []
    for rec in tutti_record:
        fields = rec.get("fields", {})
        mese_str = fields.get("Mese")
        if mese_str:
            try:
                mese_dt = datetime.strptime(mese_str, "%Y-%m-%d")
                if mese_dt >= target_date:
                    prezzo = float(fields.get("Prezzo medio €/kWh", 0))
                    record_validi.append((mese_dt, prezzo))
            except:
                continue

    if not record_validi:
        raise Exception(f"Nessun prezzo trovato per {tipo_fornitura} con validità ≥ {data_str}")

    # Prende il più vicino nel futuro
    piu_vicino = min(record_validi, key=lambda x: x[0])
    return piu_vicino[1]

def salva_offerta(dati: dict) -> dict:
    try:
        table = Table(API_KEY, BASE_ID, TBL_OFFERTE)

        record = {
            "Fornitore": dati.get("fornitore"),
            "Nome offerta": dati.get("nome_offerta"),
            "Tipologia cliente": dati.get("tipologia_cliente"),
            "Tipo tariffa": dati.get("tariffa"),
            "Prezzo fisso €/kWh": dati.get("prezzo_kwh"),
            "Spread €/kWh": dati.get("spread"),
            "Costo fisso mensile": dati.get("costo_fisso"),
            "Data validità": dati.get("validita"),
            "Fonte CTE": dati.get("fonte_cte"),
            "Note": dati.get("vincoli"),
            "Tipo fornitura": dati.get("tipo_fornitura")
        }

        return table.create(record)

    except Exception as e:
        return {"errore": str(e)}
