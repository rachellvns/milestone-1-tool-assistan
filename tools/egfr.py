# This calculation formula is based on the Glomerular Filtration Rate Estimation (eGFR) by CKD-EPI Equation with Creatinine, without Race (2021)

from pydantic import BaseModel, Field
from typing import Literal

class EgfrInput(BaseModel):
    creatinine_mgdl: float = Field(gt=0, description="Serum creatinine in mg/dL")
    age: int = Field(gt=25, le=120, description="Age in years; must be a plausible human age (1-120)")
    sex: Literal["male", "female"]
    
def classify_stage(egfr: float) -> str:
    if egfr >= 90:
        return "G1 (Normal or high)"
    elif egfr >= 60:
        return "G2 (Mildly decreased)"
    elif egfr >= 45:
        return "G3a (Mild-moderate decrease)"
    elif egfr >= 30:
        return "G3b (Moderate-severe decrease)"
    elif egfr >= 15:
        return "G3 (Severely decreased)"
    return "G5 (Kidney failure)"

def run(args: dict) -> str:
    try:
        a = EgfrInput.model_validate(args)
        # scr = serum creatinine
        scr = a.creatinine_mgdl
        
        if a.sex == "female":
            kappa, alpha, sex_factor = 0.7, -0.241, 1.012
        else:
            kappa, alpha, sex_factor = 0.9, -0.302, 1.0
            
        min_ratio = min(scr/kappa,1) ** alpha
        max_ratio = max(scr/kappa,1) ** -1.200
        
        egfr = 142 * min_ratio * max_ratio * (0.9938 ** a.age) * sex_factor
        egfr = round(egfr, 1)
        stage = classify_stage(egfr)
        return f"eGFR: {egfr} mL/min/1.73m^2 | CKD Stage: {stage} (CKD-EPI 2021)"
    except Exception as e:
        return f"ERROR: eGFR calculation failed: {e}"