from pydantic import BaseModel

class CalcInput(BaseModel):
    expression: str
    
def run(args: dict) -> str:
    expr = CalcInput.model_validate(args).expression
    allowed = set("0123456789+-*/().")
    if not set(expr) <= allowed:
        return "ERROR: only basic arithmetic is allowed"
    try:
        return str(eval(expr, {"__builtins__" : {}}))
    except Exception as e:
        return f"ERROR: {e}"
