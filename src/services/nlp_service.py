
import re
import spacy

# Load SpaCy model (small, fast)
nlp = spacy.load("en_core_web_sm")

# --- Core Regex patterns for generic PII ---
REGEX_PATTERNS = {
    "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "PHONE": r"(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})",
    "SSN": r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b",
    "AADHAAR": r"\b\d{4}\s\d{4}\s\d{4}\b",
    "ID": r"\b[A-Z0-9]{6,12}\b",
    "ACCOUNT_NUMBER": r"\b\d{9,18}\b",
    "CARD_NUMBER": r"\b(?:\d[ -]*?){13,16}\b",
    "INSURANCE_ID": r"\b[A-Z]{2,5}\d{5,12}\b",
    "POLICY_ID": r"\b\d{5,12}\b",
    "NPI": r"\b\d{10}\b",
    "GENDER": r"\b(Male|Female|Other)\b",
    "DATE": r"((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s\d{1,2},\s\d{4})",
    "ADDRESS": r"\d{1,5}\s[\w\s]+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Circle|Cir|Highway|Hwy|Parkway|Pkwy|Place|Pl)\,?\s[\w\s]+\,?\s[A-Z]{2}\s\d{5}"
}

def detect_sensitive_entities(text):
    """
    Detect sensitive entities in text using SpaCy NER + regex.
    Returns a list of tuples: (start, end, label).
    """
    doc = nlp(text)
    entities = []

    # --- Step 1: Named Entities (SpaCy) ---
    for ent in doc.ents:
        label = ent.label_

        # Custom check: Doctor vs Patient
        if label == "PERSON":
            context_window = text[max(0, ent.start_char - 20): ent.end_char + 20].lower()
            if "dr." in context_window or "doctor" in context_window or "physician" in context_window:
                entities.append((ent.start_char, ent.end_char, "DOCTOR"))
            else:
                entities.append((ent.start_char, ent.end_char, "PERSON"))
        elif label == "GPE":
            entities.append((ent.start_char, ent.end_char, "ADDRESS"))
        else:
            entities.append((ent.start_char, ent.end_char, label))

    # --- Step 2: Regex matches ---
    for label, pattern in REGEX_PATTERNS.items():
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            entities.append((match.start(), match.end(), label))

    return entities


def redact_entities(text, entities, rules, style="black_box"):
    """
    Redact entities based on rules + chosen style.
    Returns redacted text only (no audit log).
    """
    redacted = list(text)

    for start, end, label in entities:
        if label in rules.get("redact", []) and label not in rules.get("keep", []):
            length = end - start

            if style == "black_box":
                replacement = "█" * length
            elif style == "stars":
                replacement = "*" * length
            elif style == "brackets":
                replacement = "[REDACTED]"
            else:
                replacement = "█" * length

            redacted[start:end] = list(replacement.ljust(length))

    return "".join(redacted)
