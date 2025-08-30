import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io

# Extract text from an image file
def extract_text_from_image(image_path: str) -> str:
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

# Extract text from a PDF file
def extract_text_from_pdf(pdf_path: str) -> str:
    text_output = []
    pages = convert_from_path(pdf_path)
    for page in pages:
        text = pytesseract.image_to_string(page)
        text_output.append(text)
    return "\n".join(text_output)
