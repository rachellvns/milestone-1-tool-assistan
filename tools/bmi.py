from pydantic import BaseModel, Field

class BmiInput(BaseModel):
    weight_kg: float = Field(gt=0)
    height_cm: float = Field(gt=0)


def classify(bmi: float) -> tuple[str, str]:
    # returns (category, risk level) using the Asian BMI standard
    # this risk classification is based on Singapore Heart Foundation (https://www.myheart.org.sg/tools-resources/bmi-calculator/)
    if bmi < 18.5:
        return "Underweight", "Risk of nutritional deficiency disease and osteoporosis"
    elif bmi < 23.0:
        return "Normal", "Low risk (healthy range)"
    elif bmi < 27.5:
        return "Overweight", "Moderate risk"
    return "Obese", "High risk"

def run(args: dict) -> str:
    try:
        a = BmiInput.model_validate(args)
        height_m = a.height_cm / 100
        bmi = round(a.weight_kg / (height_m ** 2), 1)
        category, risk = classify(bmi)
        return f"BMI: {bmi} | Category: {category} | Risk: {risk} (Asian BMI standard)"
    except Exception as e:
        return f"ERROR: bmi calculation failed: {e}"