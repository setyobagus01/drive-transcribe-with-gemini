# drive-transcribe-with-gemini

> **Convert Google Drive files to Markdown using Gemini AI.** Docs, spreadsheets, PDFs, images, audio, and video — all transcribed and synced to local `.md` files. A [Claude Code](https://claude.ai/code) skill with incremental updates (only new or changed files are processed).

![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)
![Claude Code Skill](https://img.shields.io/badge/claude--code-skill-blueviolet)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

## Features

- **AI transcription** — images, audio, video, and PDFs described/transcribed via Gemini 2.5
- **Text extraction** — `.docx`, `.xlsx`, `.csv`, `.pptx`, Google Docs/Sheets/Slides converted natively
- **Incremental sync** — manifest-based change detection; skips already-processed files
- **Folder structure preserved** — output mirrors your Drive hierarchy
- **Auto index** — generates `_INDEX.md` table of contents after each run
- **Claude Code integration** — invoke with `/drive-transcribe-with-gemini` in any project

## Use cases

- Sync a Google Drive folder into an Obsidian / Notion-style **markdown vault**
- Build a **RAG knowledge base** from Drive documents, meeting recordings, and slide decks
- **Transcribe audio and video** files stored in Drive (interviews, lectures, podcasts)
- Convert **scanned PDFs and images** to searchable text
- Keep a local **offline mirror** of a shared Drive folder in plain text

## Supported formats

| Category | Extensions |
|----------|-----------|
| Documents | `.docx` `.pptx` `.txt` `.md` `.pdf` + Google Docs / Slides |
| Spreadsheets | `.xlsx` `.csv` + Google Sheets |
| Images | `.jpg` `.png` `.gif` `.webp` `.bmp` `.heic` `.heif` |
| Audio | `.mp3` `.wav` `.m4a` `.ogg` `.flac` |
| Video | `.mp4` `.mov` `.avi` `.webm` `.mkv` |

## Installation

```bash
npx skills add setyobagus01/drive-transcribe-with-gemini
```

Then invoke it in Claude Code by typing `/drive-transcribe-with-gemini`.

## Setup

**1. Install Python dependencies (once):**

```powershell
# Windows
pip install -r .claude\skills\drive-transcribe-with-gemini\scripts\requirements.txt

# Linux / macOS
pip3 install -r .claude/skills/drive-transcribe-with-gemini/scripts/requirements.txt
```

Requires Python 3.9+.

**2. Set up Google Cloud (required for Drive access):**

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → create or select a project
2. Enable the **Google Drive API**: APIs & Services → Library → search → Enable
3. Create a **Service Account** → download the JSON key → save as `credential.json` in `scripts/`
4. Share your Drive folder with the service account email (`@...iam.gserviceaccount.com`) → **Viewer**

**3. Create `.env`** in `scripts/`:

```env
GEMINI_API_KEY="..."            # free key at https://aistudio.google.com/apikey
SOURCE_FOLDER_ID="..."          # Drive folder ID — part after /folders/ in the URL
GOOGLE_CREDENTIALS="./credential.json"   # service account JSON from step above
OUTPUT_DIR="./output"           # optional: output root (default: ./output)
```

## Usage

```powershell
# Windows
& ".claude\skills\drive-transcribe-with-gemini\scripts\run.ps1" [flags]

# Linux / macOS
bash .claude/skills/drive-transcribe-with-gemini/scripts/run.sh [flags]
```

| Flag | Description |
|------|-------------|
| _(none)_ | Process all pending files |
| `--status` | Show pending/removed/synced counts without processing |
| `--limit 3` | Process first N files (useful for test runs) |
| `--type audio` | Process all files of a type: `doc`, `image`, `audio`, `video` |
| `--file "name"` | Process files matching name (case-insensitive substring) |

Flags can be combined: `--type audio --limit 1`

## How it works

1. Lists all files in the Drive source folder recursively
2. Compares against `manifest.json` to find what's new or changed
3. Purges entries for files deleted from Drive
4. Downloads and converts pending files:
   - `.docx` / Google Docs — text extraction via mammoth
   - `.xlsx / .csv` / Google Sheets — interpreted by Gemini
   - `.pptx` / Google Slides — text extraction per slide
   - `.jpg / .png / .heic / .mp3 / .mp4 / .pdf` etc. — transcribed/described via Gemini 2.5
   - `.txt / .md` — copied as-is
5. Writes output to `OUTPUT_DIR/` and rebuilds `_INDEX.md`

## Output

```
output/
  _INDEX.md              # auto-generated table of contents
  manifest.json          # sync state (don't edit manually)
  FOLDER/filename.md     # converted files, folder structure preserved
```

Each `.md` file includes YAML frontmatter:

```yaml
---
source: FOLDER/filename.docx
source_id: <drive file id>
modified: 2024-10-15T08:00:00.000Z
converter: docx
---
```

## Project structure

```
.claude/skills/drive-transcribe-with-gemini/scripts/
  run.ps1              # Windows run wrapper
  run.sh               # Linux / macOS run wrapper
  main.py              # orchestrator
  config.py            # settings & env vars
  requirements.txt
  converters/
    router.py          # dispatches by file extension
    text_based.py      # docx / pptx
    gemini_based.py    # image / audio / video / pdf / spreadsheet
  utils/
    drive.py           # Google Drive API wrapper
    manifest.py        # change detection
    index.py           # _INDEX.md builder + frontmatter
```

## Related

- [Google Gemini API](https://ai.google.dev/) — AI model used for transcription
- [Claude Code](https://claude.ai/code) — AI coding CLI this skill runs inside
- [npx skills](https://github.com/anthropics/claude-code-skills) — skill package manager
