"""Routes a file to the right converter based on extension."""
from pathlib import Path
from converters import text_based, gemini_based
import config


# Sentinel: signals "upload original file as-is, no conversion needed"
PASSTHROUGH = object()


def route_and_convert(local_path):
    """Returns (text_or_PASSTHROUGH, converter_used).

    If the first value is PASSTHROUGH, caller should upload the original binary
    instead of writing markdown.
    """
    ext = Path(local_path).suffix.lower()

    # Plain text/markdown: pass through unchanged
    if ext in config.TEXT_EXTS:
        return PASSTHROUGH, f"passthrough-{ext.lstrip('.')}"

    if ext in config.PDF_EXTS:
        return gemini_based.convert_pdf(local_path), "pdf"

    if ext in config.DOC_EXTS:
        return text_based.convert_docx(local_path), "docx"
    if ext in config.SPREADSHEET_EXTS:
        return gemini_based.convert_spreadsheet(local_path), "spreadsheet"
    if ext in config.PRESENTATION_EXTS:
        return text_based.convert_pptx(local_path), "pptx"
    if ext in config.IMAGE_EXTS:
        return gemini_based.convert_image(local_path), "image"
    if ext in config.AUDIO_EXTS:
        return gemini_based.convert_audio(local_path), "audio"
    if ext in config.VIDEO_EXTS:
        return gemini_based.convert_video(local_path), "video"

    raise ValueError(f"Unsupported file type: {ext}")