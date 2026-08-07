import csv
import json
from pathlib import Path
from pydantic import BaseModel, field_validator

DATA_DIR = (Path(__file__).parent.parent / "data").resolve()
MAX_ROWS = 200

print("CURRENT FILE:", __file__)
print("DATA_DIR:", DATA_DIR)

class FileInput(BaseModel):
    path: str
    
    @field_validator("path")
    @classmethod
    def no_traversal(cls, v: str) -> str:
        if ".." in v or v.startswith("/") or v.startswith("~"):
            raise ValueError("path must be a plain relative filename, no traversal")
        return v
    
    
def run(args: dict) -> str:
    try:
        a = FileInput.model_validate(args)
        target = (DATA_DIR / a.path).resolve()
        
        # to ensure the resolved path is still inside DATA_DIR
        if DATA_DIR not in target.parents and target != DATA_DIR:
            return "ERROR: access outside data directory is not allowed"
        if not target.is_file():
            return f"ERROR: file not found: {a.path}"
        
        if target.suffix.lower() == ".csv":
            with open(target, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = []
                for i, row in enumerate(reader):
                    if i >= MAX_ROWS:
                        rows.append({"_note": f"truncated after {MAX_ROWS} rows"})
                        break
                    rows.append(row)
                return json.dumps(rows)
            
        text = target.read_text(encoding="utf-8")[:20000]
        return text
    except Exception as e:
        return f"ERROR: file read failed: {e}"