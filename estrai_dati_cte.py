import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Prompt base
PROMPT_BASE = """
Estrai dal seguente testo della CTE (Condizioni Tecnico Economiche) i seguenti dati:
- Fornitore
- Nome offerta
- Tipologia tariffa: Fisso o Variabile
- Prezzo €/kWh (se Fisso)
- Spread €/kWh (se Variabile)
- Costo fisso mensile (in €)
- Validità offerta (se presente)
- Eventuali vincoli contrattuali rilevanti

Restituisci solo un oggetto JSON con le seguenti chiavi:
{
  "fornitore": "",
  "nome_offerta": "",
  "tariffa": "Fisso | Variabile",
  "prezzo_kwh": numero o null,
  "spread": numero o null,
  "costo_fisso": numero,
  "validita": "",
  "vincoli": ""
}

Testo CTE:
"""


def estrai_dati_cte(text: str) -> dict:
    prompt = PROMPT_BASE + text[:10000]  # limitiamo il testo per evitare superamento token

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        content = response.choices[0].message.content.strip()
        return eval(content) if content.startswith("{") else {"errore": "Formato non riconosciuto", "output": content}

    except Exception as e:
        return {"errore": str(e)}
