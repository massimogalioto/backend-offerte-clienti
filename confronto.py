from airtable_service import get_offerte, get_prezzo_mercato
from datetime import datetime

def confronta_offerte(bolletta):
    consumo = bolletta.consumo_kwh
    tipo = bolletta.tipo_fornitura
    data = bolletta.data_riferimento

    offerte = get_offerte(tipo)
    prezzo_mercato = get_prezzo_mercato(tipo, data)

    confronti = []

    for offerta in offerte:
        tipo_tariffa = offerta.get("fields", {}).get("Tipo tariffa")
        costo_fisso = offerta.get("fields", {}).get("Costo fisso mensile", 0)

        if tipo_tariffa == "Fisso":
            prezzo_kwh = offerta["fields"].get("Prezzo fisso €/kWh", 0)
        elif tipo_tariffa == "Variabile":
            spread = offerta["fields"].get("Spread €/kWh", 0)
            prezzo_kwh = prezzo_mercato + spread
        else:
            continue

        costo_totale = round(prezzo_kwh * consumo + costo_fisso, 2)

        confronti.append({
            "fornitore": offerta["fields"].get("Fornitore"),
            "nome_offerta": offerta["fields"].get("Nome offerta"),
            "tariffa": tipo_tariffa,
            "prezzo_kwh": round(prezzo_kwh, 4),
            "costo_fisso": costo_fisso,
            "totale_simulato": costo_totale
        })

    confronti.sort(key=lambda x: x["totale_simulato"])
    return confronti