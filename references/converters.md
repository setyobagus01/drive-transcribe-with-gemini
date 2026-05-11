<converter_behavior>
## Per-format converter notes

| Format | Converter | Output |
|--------|-----------|--------|
| `.docx`, Google Doc | mammoth → python-docx fallback | Markdown |
| `.xlsx`, `.xls`, `.csv`, Google Sheet | Gemini (inline text prompt) | Markdown, grouped by first column |
| `.pptx`, Google Slides | python-pptx (text only) | Markdown, one section per slide |
| `.txt`, `.md` | passthrough | Copied as `.md`, no LLM |
| `.pdf` | Gemini Files API | Markdown (text + structure extracted) |
| `.jpg`, `.png`, `.gif`, `.webp`, `.bmp` | Gemini inline | Markdown |
| `.heic`, `.heif` | Gemini Files API | Markdown |
| `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` | Gemini Files API | Markdown (transcript + summary + topics) |
| `.mp4`, `.mov`, `.avi`, `.webm`, `.mkv` | Gemini Files API | Markdown (transcript + visuals + summary + topics) |
</converter_behavior>

<sheets_output>
## Sheets output

xlsx/csv files are parsed by pandas into CSV text, then sent to Gemini as an inline prompt. Gemini restructures the content into readable markdown — typically grouped sections when the first column is a repeating label (e.g. interview subjects), or a table for simple data.

**When the output looks off:**
- Gemini may still choose a table for complex sheets — this is a judgment call it makes based on the data shape.
- Very large sheets (500+ rows) are truncated to the first 500 rows before sending to Gemini.
</sheets_output>
