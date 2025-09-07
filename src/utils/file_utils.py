import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
REDACTED_FOLDER = "redacted"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REDACTED_FOLDER, exist_ok=True)

def save_file(file) -> str:
    """
    Saves uploaded file securely.
    Returns file path.
    """
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    return file_path
