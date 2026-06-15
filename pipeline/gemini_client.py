import re
import json
import os
import google.generativeai as genai
from .prompt import SYSTEM_PROMPT, build_user_prompt

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")


def _strip_markdown(text: str) -> str:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    return match.group(1) if match else text.strip()


def analyze_review(review_content: str) -> dict | None:
    try:
        prompt   = SYSTEM_PROMPT + "\n\n" + build_user_prompt(review_content)
        response = model.generate_content(prompt)
        cleaned  = _strip_markdown(response.text)
        result   = json.loads(cleaned)

        if "categories" not in result:
            print(f"[WARN] Response thiếu key 'categories'")
            return None

        return result

    except json.JSONDecodeError as e:
        print(f"[JSON parse error] {e}")
        return None
    except Exception as e:
        print(f"[Gemini error] {e}")
        return None
