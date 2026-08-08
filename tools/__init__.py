from . import calculator, fx, files, bmi, egfr, egfr_pediatric, cvd

REGISTRY = {
    "calculator": calculator.run,
    "get_fx_rate": fx.run,
    "read_data": files.run,
    "calculate_bmi": bmi.run,
    "calculate_egfr": egfr.run,
    "calculate_egfr_pediatric": egfr_pediatric.run,
    "calculate_cvd": cvd.run,
}

TOOLS = [

    {"name": "calculator",
     "description": "Evaluate an arithmetic expression exactly. "
     "Use for ANY math instead of computing yourself.",
     "input_schema": {"type": "object", "properties": {"expression": {"type": "string"}},
                       "required": ["expression"]}},

    {"name": "get_fx_rate",
     "description": "Get the current exchange rate between two currencies. "
     "Use for ANY currency conversion instead of estimating yourself.",
     "input_schema": {"type": "object", "properties": {
         "base": {"type": "string", "description": "3-letter currency code to convert from, e.g. USD"},
         "quote": {"type": "string", "description": "3-letter currency code to convert to, e.g. MYR"}},
         "required": ["base", "quote"]}},

    {"name": "read_data",
     "description": "Read and return the contents of a data file (e.g. CSV, JSON, TXT) from disk. "
     "Use to access file contents instead of guessing at them.",
     "input_schema": {"type": "object", "properties": {
         "path": {"type": "string", "description": "Path to the file to read"}},
         "required": ["path"]}},

    {"name": "calculate_bmi",
     "description": "Calculate Body Mass Index and classify it using the Asian BMI standard "
     "(cutoffs: 18.5 / 23.0 / 27.5). Use for ANY BMI calculation instead of estimating yourself.",
     "input_schema": {"type": "object", "properties": {
         "weight_kg": {"type": "number", "description": "Weight in kilograms"},
         "height_cm": {"type": "number", "description": "Height in centimeters"}},
         "required": ["weight_kg", "height_cm"]}},

    {"name": "calculate_egfr",
     "description": "Calculate estimated Glomerular Filtration Rate (kidney function) for "
     "patients OVER age 25, using the CKD-EPI 2021 race-free equation, and classify CKD "
     "stage. For ages 1-25, use calculate_egfr_pediatric instead. Use for ANY eGFR "
     "calculation instead of estimating yourself.",
     "input_schema": {"type": "object", "properties": {
         "creatinine_mgdl": {"type": "number", "description": "Serum creatinine in mg/dL"},
         "age": {"type": "integer", "description": "Age in years, must be over 25"},
         "sex": {"type": "string", "enum": ["male", "female"]}},
         "required": ["creatinine_mgdl", "age", "sex"]}},

    {"name": "calculate_egfr_pediatric",
     "description": "Calculate estimated Glomerular Filtration Rate (kidney function) for "
     "patients aged 1-25, using the CKiD U25 creatinine-based equation, and classify CKD "
     "stage. For patients over 25, use calculate_egfr instead. Use for ANY eGFR calculation "
     "in this age range instead of estimating yourself.",
     "input_schema": {"type": "object", "properties": {
         "creatinine_mgdl": {"type": "number", "description": "Serum creatinine in mg/dL"},
         "height_cm": {"type": "number", "description": "Height in centimeters"},
         "age": {"type": "number", "description": "Age in years (1-25), decimals allowed"},
         "sex": {"type": "string", "enum": ["male", "female"]}},
         "required": ["creatinine_mgdl", "height_cm", "age", "sex"]}},

    {"name": "calculate_cvd",
     "description": "Calculate 10-year cardiovascular disease risk using the Framingham "
     "2008 model. Only valid for ages 30-79 — the model was not validated outside this "
     "range, and its accuracy for Southeast Asian populations is not confirmed. Use for "
     "ANY CVD risk estimate instead of guessing yourself.",
     "input_schema": {"type": "object", "properties": {
         "age": {"type": "integer", "description": "Age in years, 30-79"},
         "sex": {"type": "string", "enum": ["male", "female"]},
         "total_cholesterol_mgdl": {"type": "number"},
         "hdl_cholesterol_mgdl": {"type": "number"},
         "systolic_bp_mmhg": {"type": "number"},
         "on_bp_medication": {"type": "boolean"},
         "is_smoker": {"type": "boolean"},
         "has_diabetes": {"type": "boolean"}},
         "required": ["age", "sex", "total_cholesterol_mgdl", "hdl_cholesterol_mgdl",
                       "systolic_bp_mmhg", "on_bp_medication", "is_smoker", "has_diabetes"]}},
]