import math
from pydantic import BaseModel, Field
from typing import Literal

class CvdInput(BaseModel):
    age: int = Field(ge=30, le=79)
    sex: Literal["male", "female"]
    total_cholesterol_mgdl: float = Field(gt=0)
    hdl_cholesterol_mgdl: float = Field(gt=0)
    systolic_bp_mmhg: float = Field(gt=0)
    on_bp_medication: bool
    is_smoker: bool
    has_diabetes: bool
    
# based on Framingham General CVD Risk (2008), Wilson/D'Agostino coefficients
# source: https://www.framinghamheartstudy.org/fhs-risk-functions/cardiovascular-disease-10-year-risk/ 
COEF = {
    "male":
        {
            "age": 3.06117, "tc": 1.12370, "hdl": -0.93263,
            "sbp_treated": 1.99881, "sbp_untreated": 1.93303,
            "smoker": 0.65451, "diabetes": 0.57367,
            "mean": 23.9802, "s0": 0.88936,
        },
    "female":
        {
            "age": 2.32888, "tc": 1.20904, "hdl": -0.70833,
            "sbp_treated": 2.82263, "sbp_untreated": 2.76157,
            "smoker": 0.52873, "diabetes": 0.69154,
            "mean": 26.1931, "s0": 0.95012,
        }
}

def classify_risk(pct: float) -> str:
    if pct < 10:
        return "Low risk"
    elif pct < 20:
        return "Intermediate risk"
    return "High risk"

def run(args: dict) -> str:
    try:
        a = CvdInput.model_validate(args)
        c = COEF[a.sex]
        
        ln_age = math.log(a.age)
        ln_tc = math.log(a.total_cholesterol_mgdl)
        ln_hdl = math.log(a.hdl_cholesterol_mgdl)
        ln_sbp = math.log(a.systolic_bp_mmhg)
        sbp_coef = c["sbp_treated"] if a.on_bp_medication else c["sbp_untreated"]
        
        L = (
            c["age"] * ln_age +
            c["tc"] * ln_tc +
            c["hdl"] * ln_hdl + 
            sbp_coef * ln_sbp + 
            c["smoker"] * (1 if a.is_smoker else 0) +
            c["diabetes"] * (1 if a.has_diabetes else 0)
        )
        
        risk_pct = (1-c["s0"] ** math.exp(L-c["mean"])) * 100
        risk_pct = round(max(0, min(risk_pct,100)), 1)
        category = classify_risk(risk_pct)
        
        return f"10-year CVD risk: {risk_pct}% | Category: {category}"
    except Exception as e:
        return f"ERROR: CVD risk calculation failed: {e}"