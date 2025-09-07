import os
import json
from pdf2image import convert_from_path
from PIL import Image
from src.services.cv_service import redact_image
from src.services.nlp_service import detect_sensitive_entities, redact_entities

# Load redaction rules once at startup
RULES_FILE = "configs/redaction_rules.json"
with open(RULES_FILE, "r") as f:
    ALL_RULES = json.load(f)


def redact_text(text, use_case="default", style="black_box"):
    """
    Redact sensitive info in plain text using NLP + rules.
    """
    entities = detect_sensitive_entities(text)
    rules = ALL_RULES.get(use_case, ALL_RULES.get("default", {}))
    return redact_entities(text, entities, rules, style)


def redact_file(input_path, output_path=None, use_case="default", style="black_box"):
    """
    Redact sensitive info in a file (image or PDF).
    """
    if not output_path:
        output_path = input_path.replace("uploads", "redacted")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if input_path.lower().endswith((".png", ".jpg", ".jpeg")):
        return redact_image(input_path, output_path, use_case, style)

    elif input_path.lower().endswith(".pdf"):
        return redact_pdf(input_path, output_path, use_case, style)

    else:
        return None


def redact_pdf(pdf_path, output_path, use_case="default", style="black_box"):
    """
    Redact sensitive info in a PDF by converting pages -> images -> redact -> rebuild PDF.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Convert PDF pages -> images
    pages = convert_from_path(pdf_path)

    redacted_images = []
    for i, page in enumerate(pages):
        temp_input = f"temp_page_{i}.png"
        temp_output = f"temp_page_{i}_redacted.png"

        page.save(temp_input, "PNG")

        # Redact with CV
        redact_image(temp_input, temp_output, use_case, style)

        # Open, copy, then close to free file
        img = Image.open(temp_output)
        redacted_images.append(img.copy())   # make a copy in memory
        img.close()                          # release file handle

        os.remove(temp_input)
        os.remove(temp_output)

    # Save all redacted pages back into one PDF
    redacted_images[0].save(output_path, save_all=True, append_images=redacted_images[1:])

    return output_path
