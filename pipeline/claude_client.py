import re
import json
import anthropic
from .prompt import SYSTEM_PROMPT, build_user_prompt

client = anthropic.Anthropic()


def _strip_markdown(text: str) -> str:
    """
    Bóc ```json ... ``` hoặc ``` ... ``` nếu model vô tình bọc vào.
    """
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    return match.group(1) if match else text.strip()


def analyze_review(review_content: str) -> dict | None:
    """
    Gọi Claude API phân tích một review.

    Returns:
        dict với key "categories" nếu thành công, None nếu lỗi.
    """
    try:
        response = client.messages.create(
            model      = "claude-sonnet-4-20250514",
            max_tokens = 1024,
            system     = SYSTEM_PROMPT,
            messages   = [{"role": "user", "content": build_user_prompt(review_content)}],
        )

        raw_text = response.content[0].text
        cleaned  = _strip_markdown(raw_text)
        result   = json.loads(cleaned)

        # Validate cấu trúc tối thiểu
        if "categories" not in result:
            print(f"[WARN] Response thiếu key 'categories': {cleaned[:200]}")
            return None

        return result

    except json.JSONDecodeError as e:
        print(f"[JSON parse error] {e}\nRaw: {raw_text[:300]}")
        return None
    except anthropic.APIStatusError as e:
        print(f"[API status error] {e.status_code}: {e.message}")
        return None
    except anthropic.APIConnectionError as e:
        print(f"[API connection error] {e}")
        return None
