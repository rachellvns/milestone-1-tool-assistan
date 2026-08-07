from tools import calculator, fx, files

REGISTRY = {"calculator": calculator.run,
            "get_fx_rate": fx.run,
            "read_data": files.run}

TOOLS = [
    
        {"name": "calculator",
        "description": "Evaluate an arithmetic expression exactly."
        "Use for ANY math instead of computing yourself.",
        "input_schema": {"type": "object", "properties": {"expression": {"type": "string"}},
                         "required": ["expression"]}},
        
        {"name": "get_fx_rate",
        "description": "Get the current exchange rate between two currencies."
        "Use for ANY currency conversion instead of estimating yourself.",
        "input_schema": {"type": "object", "properties": {"base_currency": {"type": "string", "description": "3-letter currency code to convert from, e.g USD"},
                         "quote_currency": {"type": "string", "description": "3-letter currency code to convert to, e.g MYR"}},
                        "required": ["base_currency", "quote_currency"]}},
        
        {"name": "read_data",
         "description": "Read and return the contents of a data file (e.g CSV, JSON, TXT) from disk."
        "Use to access file contents instead of guessing at them.",
        "input_schema": {"type": "object", "properties": {"path": {"type": "string", "description": "Path to the file to read"}},
                         "required": ["path"]}},
]