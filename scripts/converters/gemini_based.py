"""Gemini-based conversion for audio, video, images, and scanned PDFs."""
import time
from pathlib import Path
from google import genai
from google.genai import types

import config

_client = None


def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


IMAGE_PROMPT = """Extract all visible text from this image completely and accurately.
Preserve the original structure such as headings, lists, tables, or paragraphs where present.
Respond in the same language as the content. Output clean markdown. No preamble."""

AUDIO_PROMPT = """Transcribe this audio in full. Then add:
1. A brief summary (3-5 bullet points)
2. Key topics and entities mentioned
3. Speaker labels if more than one speaker is present

IMPORTANT: Write every word of your response — including the summary, topics, and section headers — in the same language as the spoken content. Do NOT switch to English for any section unless the audio itself is in English.
Output markdown with sections: ## Transcript, ## Summary, ## Topics. No preamble."""

VIDEO_PROMPT = """Analyze this video for a knowledge base. Provide:
1. Full transcription of spoken content (with timestamps every ~30 seconds)
2. Visual description of important scenes, slides, or on-screen text
3. Summary (5-7 bullet points)
4. Key topics

IMPORTANT: Write every word of your response — including the visuals, summary, topics, and section headers — in the same language as the content. Do NOT switch to English for any section unless the video itself is in English.
Output markdown with sections: ## Transcript, ## Visuals, ## Summary, ## Topics. No preamble."""

PDF_PROMPT = """Extract all text from this PDF. Preserve structure (headings, lists, tables, paragraphs).
Respond in the same language as the content. Output clean markdown. No preamble."""


def _with_retry(fn, *args, **kwargs):
    """Retry on transient errors with exponential backoff."""
    last_err = None
    for attempt in range(config.MAX_RETRIES):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            last_err = e
            wait = 2 ** attempt * 5  # 5s, 10s, 20s
            print(f"  retry {attempt+1}/{config.MAX_RETRIES} in {wait}s: {e}")
            time.sleep(wait)
    raise last_err


def _upload_and_generate(path, prompt, mime_type=None):
    """Upload via Files API (needed for files >20MB or video/audio), then generate."""
    client = get_client()
    uploaded = _with_retry(
        client.files.upload,
        file=path,
        config={"mime_type": mime_type} if mime_type else None,
    )

    # Wait for processing (video/audio need this)
    while uploaded.state.name == "PROCESSING":
        time.sleep(2)
        uploaded = client.files.get(name=uploaded.name)
    if uploaded.state.name == "FAILED":
        raise RuntimeError(f"Gemini file processing failed for {path}")

    response = _with_retry(
        client.models.generate_content,
        model=config.GEMINI_MEDIA_MODEL,
        contents=[uploaded, prompt],
    )
    try:
        client.files.delete(name=uploaded.name)
    except Exception:
        pass
    if not response.text:
        raise RuntimeError(f"Gemini returned empty response for {path}")
    return response.text


_IMAGE_MIME = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp",
}

# HEIC/HEIF require the Files API upload path (not supported inline)
_UPLOAD_IMAGE_MIME = {
    ".heic": "image/heic",
    ".heif": "image/heif",
}


def convert_image(path):
    path = Path(path)
    ext = path.suffix.lower()
    if ext in _UPLOAD_IMAGE_MIME:
        return _upload_and_generate(path, IMAGE_PROMPT, mime_type=_UPLOAD_IMAGE_MIME[ext])
    mime_type = _IMAGE_MIME.get(ext, "image/jpeg")
    client = get_client()
    part = types.Part.from_bytes(data=path.read_bytes(), mime_type=mime_type)
    response = _with_retry(
        client.models.generate_content,
        model=config.GEMINI_MODEL,
        contents=[part, IMAGE_PROMPT],
    )
    if not response.text:
        raise RuntimeError(f"Gemini returned empty response for {path}")
    return response.text


def convert_audio(path):
    return _upload_and_generate(path, AUDIO_PROMPT)


def convert_video(path):
    return _upload_and_generate(path, VIDEO_PROMPT)


def convert_pdf(path):
    return _upload_and_generate(path, PDF_PROMPT, mime_type="application/pdf")


SPREADSHEET_PROMPT = """Below is spreadsheet data. Convert it to clean, readable markdown.
Group related rows under headings where the data has a grouping column (e.g. a person's name repeated across rows).
Preserve all data. Use bullet points or sections — avoid wide tables.
Respond in the same language as the content. No preamble.

{data}"""


def convert_spreadsheet(path):
    import pandas as pd
    path = Path(path)
    ext = path.suffix.lower()
    if ext in (".xlsx", ".xls"):
        xl = pd.ExcelFile(path)
        sheets = []
        for sheet in xl.sheet_names:
            df = xl.parse(sheet).fillna("")
            sheets.append(f"Sheet: {sheet}\n{df.to_csv(index=False)}")
        data = "\n\n".join(sheets)
    else:
        data = pd.read_csv(path).fillna("").to_csv(index=False)

    client = get_client()
    response = _with_retry(
        client.models.generate_content,
        model=config.GEMINI_MODEL,
        contents=[SPREADSHEET_PROMPT.format(data=data)],
    )
    if not response.text:
        raise RuntimeError(f"Gemini returned empty response for {path}")
    return response.text