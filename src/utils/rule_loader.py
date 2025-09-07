import json
import os

RULES_PATH = os.path.join("src", "config", "redaction_rules.json")

with open(RULES_PATH, "r") as f:
    RULES = json.load(f)

def get_rules(use_case: str, sub_use_case: str = None):
    use_case = use_case.lower()
    sub_use_case = sub_use_case.lower() if sub_use_case else None

    if use_case not in RULES:
        return {"keep": [], "redact": []}

    if sub_use_case and sub_use_case in RULES[use_case]:
        return RULES[use_case][sub_use_case]

    return RULES[use_case].get("_default", {"keep": [], "redact": []})
