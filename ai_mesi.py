import os
import openai
import re

openai.api_key = os.getenv("OPENAI_API_KEY")

def estrai_numero(content: str) -> int:
    match = re.search(r"\b(\d{1,2})\b", content)
    if match:
        return int(match.group(1))
    return None

def chiedi_ai_mesi(periodo: str) -> int:
    prompt = (
        f"Quanti mesi copre la seguente bolletta? "
        f"Rispondi solo con un numero intero. senza altre considerazioni, rispondi ad esempio solo con 2, 3 senza scrivere perfetto ok o cose simili\n\n"
        f"Periodo: \"{periodo}\""
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        content = response.choices[0].message["content"].strip()
        print("[RISPOSTA GPT]:", content)  # 🔍 Debug log
        mesi = estrai_numero(content)
        return max(1, mesi) if mesi is not None else None
    except Exception as e:
        print(f"[ERRORE chiedi_ai_mesi] {e}")
        return None
