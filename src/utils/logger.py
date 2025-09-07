import logging
import os

# Ensure logs folder exists
LOG_FOLDER = "logs"
os.makedirs(LOG_FOLDER, exist_ok=True)

LOG_FILE = os.path.join(LOG_FOLDER, "app.log")

# Create logger
logger = logging.getLogger("SealDocAI")
logger.setLevel(logging.DEBUG)  # Or INFO

# File handler
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.INFO)
fh_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
fh.setFormatter(fh_formatter)
logger.addHandler(fh)

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # Or INFO
ch_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
ch.setFormatter(ch_formatter)
logger.addHandler(ch)
