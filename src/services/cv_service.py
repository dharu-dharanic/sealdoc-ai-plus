
import cv2
import pytesseract
from src.services.nlp_service import detect_sensitive_entities
import json
import os

# Load redaction rules
RULES_FILE = "configs/redaction_rules.json"
if os.path.exists(RULES_FILE):
    with open(RULES_FILE, "r") as f:
        ALL_RULES = json.load(f)
else:
    ALL_RULES = {"default": {"redact": ["EMAIL", "PHONE", "SSN"], "keep": []}}


def apply_redaction(image, x, y, w, h, style="black_box"):
    """
    Apply the chosen redaction style to a region in the image.
    """
    roi = image[y:y+h, x:x+w]

    if style == "black_box":
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), -1)

    elif style == "blur":
        roi = cv2.GaussianBlur(roi, (51, 51), 30)
        image[y:y+h, x:x+w] = roi

    elif style == "pixelate":
        small = cv2.resize(roi, (10, 10), interpolation=cv2.INTER_LINEAR)
        pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        image[y:y+h, x:x+w] = pixelated

    return image


def redact_image(image_path, output_path, use_case="default", style="black_box"):
    """
    Redacts sensitive entities in an image based on use-case rules + style.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")

    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    rules = ALL_RULES.get(use_case, ALL_RULES.get("default", {}))

    for i, word in enumerate(data["text"]):
        word = word.strip()
        if not word:
            continue

        entities = detect_sensitive_entities(word)
        for _, _, label in entities:
            if label in rules.get("redact", []) and label not in rules.get("keep", []):
                x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                image = apply_redaction(image, x, y, w, h, style)

    cv2.imwrite(output_path, image)
    return output_path
