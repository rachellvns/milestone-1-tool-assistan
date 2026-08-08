# Parsing/rendering/saving utilities for JSON-mode health reports.
# Kept separate from chat.py so these pure functions can be tested and reused independently of the interactive chat loop.

import json
import re
from datetime import datetime
from pathlib import Path


def extract_json(text: str) -> dict | None:
    """Try to pull a JSON object out of the model's reply, even if it accidentally wrapped it in markdown fences or added stray text."""
    text = text.strip()

    # try straight parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # try stripping markdown code fences (```json ... ``` or ``` ... ```)
    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # try grabbing the first { ... last } as a last resort
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def safe_get(d: dict, *keys, default=None):
    """Safely walk nested dict keys, returning default if anything's missing
    or the wrong type at any point."""
    current = d
    for k in keys:
        if not isinstance(current, dict) or k not in current:
            return default
        current = current[k]
    return current


def render_report_from_json(data: dict) -> str:
    SPECIAL_MESSAGES = {
        "not_selected_by_user": "Not selected by user",
        "not_applicable_under_30": "Not applicable — CVD risk is only validated for ages 30 and older",
    }

    def section(title, value, unit, category, missing):
        missing = missing if isinstance(missing, list) else []
        if value is None:
            for flag, message in SPECIAL_MESSAGES.items():
                if flag in missing:
                    return f"**{title}**\n- {message}"
            reason = f"missing: {', '.join(missing)}" if missing else "insufficient data"
            return f"**{title}**\n- Not calculated — {reason}"
        cat = category if category else "uncategorized"
        return f"**{title}**\n- Value: {value}{unit} — {cat}"

    bmi_val = safe_get(data, "bmi", "value")
    bmi_cat = safe_get(data, "bmi", "category")
    bmi_missing = safe_get(data, "bmi", "missing_fields", default=[])

    egfr_val = safe_get(data, "egfr", "value")
    egfr_stage = safe_get(data, "egfr", "ckd_stage")
    egfr_missing = safe_get(data, "egfr", "missing_fields", default=[])

    cvd_val = safe_get(data, "cvd_risk", "value_percent")
    cvd_cat = safe_get(data, "cvd_risk", "category")
    cvd_missing = safe_get(data, "cvd_risk", "missing_fields", default=[])

    disclaimer = safe_get(data, "disclaimer",
        default="This report is for informational purposes only and is not "
                "a substitute for professional medical advice, diagnosis, "
                "or treatment. Please consult a qualified healthcare provider.")

    report = "## Health Report\n\n"
    report += section("Body Mass Index (BMI)", bmi_val, "", bmi_cat, bmi_missing) + "\n\n"
    report += section("Kidney Function (eGFR)", egfr_val, " mL/min/1.73m²", egfr_stage, egfr_missing) + "\n\n"
    report += section("Cardiovascular Risk (10-year)", cvd_val, "%", cvd_cat, cvd_missing) + "\n\n"
    report += f"---\n*{disclaimer}*"
    return report


def save_report_json(data: dict, filename: str | None = None) -> Path:
    """Save a report dict as a downloadable, timestamped JSON file.

    - data: the report dict to save (e.g. output of extract_json, or a
      validated pydantic model's .model_dump()).
    - filename: optional explicit filename. If omitted, a timestamped
      filename like 'HealthReport-20260808-143000.json' is generated.

    Returns the Path the file was written to.
    """
    if filename is None:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"HealthReport-{ts}.json"

    path = Path(filename)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path