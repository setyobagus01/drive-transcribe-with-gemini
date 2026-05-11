"""Configuration. Set these via env vars or directly here."""
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Google Drive
SOURCE_FOLDER_ID = os.getenv("SOURCE_FOLDER_ID", "YOUR_SOURCE_FOLDER_ID")
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CREDENTIALS", "credentials.json")

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash-lite"        # images, docs — cheap + fast
GEMINI_MEDIA_MODEL = "gemini-2.5-flash"      # audio/video — handles long content without truncating

# Local working dir
WORK_DIR = Path(os.getenv("WORK_DIR", "./.kb-work"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))
MANIFEST_FILE = "manifest.json"

# Processing
MAX_PARALLEL = 1   # keep low for SSL stability
MAX_RETRIES = 5
GEMINI_RPM = 60    # paid tier allows much higher
GEMINI_TIMEOUT = 1800  # seconds — large audio/video uploads + transcription can take 20-30min

# File routing
TEXT_EXTS = {".txt", ".md"}
DOC_EXTS = {".docx"}
PDF_EXTS = {".pdf"}
SPREADSHEET_EXTS = {".xlsx", ".xls", ".csv"}
PRESENTATION_EXTS = {".pptx"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".webm", ".mkv"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".heic", ".heif"}

ALL_SUPPORTED = (TEXT_EXTS | DOC_EXTS | PDF_EXTS | SPREADSHEET_EXTS
                 | PRESENTATION_EXTS | AUDIO_EXTS | VIDEO_EXTS | IMAGE_EXTS)

# Google Workspace native formats → export extension
GOOGLE_WORKSPACE_MIME = {
    "application/vnd.google-apps.document": ".docx",
    "application/vnd.google-apps.spreadsheet": ".xlsx",
    "application/vnd.google-apps.presentation": ".pptx",
}
