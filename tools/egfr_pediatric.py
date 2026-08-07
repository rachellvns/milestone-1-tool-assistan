# This is intended for 1-25 year olds with mild-to-moderate CKD
# Source: https://www.niddk.nih.gov/research-funding/research-programs/kidney-clinical-research-epidemiology/laboratory/glomerular-filtration-rate-equations/children-adolescents-young-adults#ckid-u25 
# This is not interchangeable with adult CKD-EPI 2021 eGFR values
# Use egfr.py (CKD-EPI 2021) for patients over 25.

from pydantic import BaseModel, Field
from typing import Literal

class EgfrPediatricInput(BaseModel):
    creatinine_mgdl: float = Field(gt=0, description="Serum creatinine in mg/dL")
    height_cm: float = Field(gt=0, description="Height in cm")
    age: float = Field(ge=1, le=25, description="Age in years (1-25; decimals allowed)")
    sex: Literal["male", "female"]
    
def kappa(age: float, sex: str) -> float:
    if sex == "female":
        if age < 12:
            return 36.1 * (1.008 ** (age-12))
        elif age < 18:
            return 36.1 * (1.023 ** (age-12))
        return 41.4
    else:
        if age < 12: 
            return 39.0 * (1.008 ** (age-12))
        elif age < 18:
            return 39.0 * (1.045 ** (age-12))
        return 50.8
    
def classify_stage(egfr: float) -> str:
    if egfr >= 90:
        return "G1 (Normal or high)"
    elif egfr >= 60:
        return "G2 (Mildly decreased)"
    elif egfr >= 45:
        return "G3a (Mild-moderate decrease)"
    elif egfr >= 30:
        return "G4 (Severely decreased)"
    return "G5 (Kidney failure)"

def run(args: dict) -> str:
    try:
        a = EgfrPediatricInput.model_validate(args)
        height_m = a.height_cm/100
        k = kappa(a.age, a.sex)
        
        egfr = k * (height_m / a.creatinine_mgdl)
        egfr = round(egfr,1)
        stage = classify_stage(egfr)
        
        return (f"eGFR: {egfr} mL/min/1.73m^2 | CKD Stage: {stage}"
                f"(CKiD U25 creatinine equation, ages 1-25)")
    except Exception as e:
        return f"ERROR: pediatric eGFR calculation failed: {e}"