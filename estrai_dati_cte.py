import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def estrai_dati_offerta_cte(testo: str) -> dict:
    try:
        prompt = (
            "Estrai i dati principali dell'offerta luce o gas da questa CTE (Condizione Tecnico Economica) e restituiscili in formato JSON.\n\n"
            "Campi richiesti:\n"
            "- fornitore (es. Enel Energia)\n"
            "- nome_offerta (nome commerciale dell'offerta)\n"
            "- tipologia_cliente (Residenziale o Business)\n"
            "- tariffa (Fisso o Variabile)\n"
            "- prezzo_kwh (solo se tariffa Fisso, es. 0.145) oppure null\n"
            "- spread (solo se tariffa Variabile, es. 0.0135) oppure null\n"
            "- costo_fisso (se l'importo è maggiore di 30 euro probabilmente è in euro/anno quindi dividilo per 12)\n"
            "- validita (data in formato 'YYYY-MM-DD', oppure null se non disponibile)\n"
            "- vincoli (es. 'Durata minima 12 mesi') o null\n"
            "- tipo_fornitura (Luce o Gas)\n\n"
            "Testo da analizzare:\n"
            f"{testo[:7000]}"
        )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sei un assistente esperto in offerte luce e gas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=600
        )

        content = response.choices[0].message.content

        # Rimuove eventuali blocchi markdown tipo ```json
        json_text = re.sub(r"```json|```", "", content).strip()

        return json.loads(json_text)

    except Exception as e:
        return {
            "errore": "Formato non riconosciuto o parsing fallito",
            "output": content if 'content' in locals() else str(e)
        }
