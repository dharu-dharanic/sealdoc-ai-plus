import pytesseract
from pdf2image import convert_from_path
import pdfplumber
from PIL import Image

def extract_text_from_image(image_path):
    """
    Extract text from an image using Tesseract OCR.
    """
    return pytesseract.image_to_string(Image.open(image_path))


def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF.
    1. Try pdfplumber (direct text extraction).
    2. If no text found, fallback to Tesseract OCR via pdf2image.
    """
    text = ""

    # --- Try pdfplumber first ---
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    except Exception as e:
        print(f"[WARN] pdfplumber failed: {e}")

    # --- Fallback to OCR if empty ---
    if not text.strip():
        print("[INFO] No text found with pdfplumber, using Tesseract OCR...")
        pages = convert_from_path(pdf_path)
        for page in pages:
            text += pytesseract.image_to_string(page) + "\n"

    return text.strip()
