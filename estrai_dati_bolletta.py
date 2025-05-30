import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def estrai_dati_bolletta(testo: str) -> dict:
    try:
        prompt = (
            "Estrai i dati principali da una bolletta di energia elettrica o gas e restituiscili in formato JSON con i seguenti campi:\n\n"
            "- cliente (nome e cognome o ragione sociale)\n"
            "- indirizzo (completo del punto di fornitura)\n"
            "- pod (codice POD o PDR, se presente)\n"
            "- kwh_totali (consumo totale nel periodo, potrebbe essere scritto come KWH fatturati o consumi rilevati o quanto ho consumato solo numero intero ad esempio 1,2,3)\n"
            "- mesi_bolletta (cerca periodo di fatturazione e restituisci il numero dei mesi ad esempio gennaio-febbraio 2025 è uguale a 2 , marzo 2025 uguale a 1, 01/05/2025-30/06/2025 uguale a 2 non mettere altro testo)\n"
            "- spesa_materia_energia (costo totale della sola materia energia, restituisci solo il valore numerico con punto decimale)\n"
            "- tipo_fornitura ('Luce' o 'Gas')\n"
            "- tipologia_cliente  (restituisci Residenziale se è solito Domestico residente o domestico non residente, Business è altri usi)\n"
            "Rispondi solo con JSON valido, senza commenti o testo extra. Ecco il testo da analizzare:\n\n"
            f"{testo[:7000]}"
        )

        response = client.chat.completions.create(
            model="gpt-4-turbo",   #gpt-4-turbo # gpt-3.5-turbo-0125
            messages=[
                {"role": "system", "content": "Sei un assistente esperto in bollette di luce e gas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1700
        )

        content = response.choices[0].message.content

        # Rimuove eventuali blocchi markdown ```json
        json_text = re.sub(r"```json|```", "", content).strip()
        return json.loads(json_text)

    except Exception as e:
        return {
            "errore": "Formato non riconosciuto o parsing fallito",
            "output": content if 'content' in locals() else str(e)
        }
