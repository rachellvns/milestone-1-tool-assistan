import httpx
from pydantic import BaseModel

RATE_URL = "https://api.frankfurter.dev/v1/latest?base={}&symbols={}"

class FxInput(BaseModel):
    base: str
    quote: str
    
def run(args: dict) -> str:
    try:
        a = FxInput.model_validate(args)
        r = httpx.get(RATE_URL.format(a.base, a.quote), timeout=8.0)
        r.raise_for_status()
        return str(r.json()["rate"])
    except Exception as e:
        return f"ERROR: fx lookup failed: {e}"