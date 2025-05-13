# ai_mesi.py

import os
import openai

# Assicurati di avere la variabile d'ambiente OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

def chiedi_ai_mesi(periodo: str) -> int:
    prompt = (
        f"Quanti mesi copre la seguente bolletta? "
        f"Rispondi solo con un numero intero:\n"
        f"\"{periodo}\""
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        contenuto = response.choices[0].message["content"].strip()
        mesi = int(contenuto)
        return max(1, mesi)
    except Exception as e:
        print(f"[ERRORE chiedi_ai_mesi] {e}")
        return None
