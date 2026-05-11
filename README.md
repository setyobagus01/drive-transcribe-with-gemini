# drive-transcribe-with-gemini

Converts Google Drive files — docs, images, audio, video — to local markdown. Gemini-powered transcription for media; direct text extraction for structured formats. Incremental: only new or changed files are processed.

## Installation

```bash
npx skills add setyobagus01/drive-transcribe-with-gemini
```

Then invoke it in Claude Code by typing `/drive-transcribe-with-gemini`.

## Setup

**Install dependencies (once, globally):**

```powershell
# Windows
pip install -r .claude\skills\drive-transcribe-with-gemini\scripts\requirements.txt

# Linux / macOS
pip3 install -r .claude/skills/drive-transcribe-with-gemini/scripts/requirements.txt
```

Requires Python 3.9+.

**Create `.env`** in `scripts/`:

```env
GEMINI_API_KEY="..."
SOURCE_FOLDER_ID="..."               # Drive folder ID — part after /folders/ in the URL
GOOGLE_CREDENTIALS="./credential.json"   # optional: only if folder is private
OUTPUT_DIR="./output"                # optional: output root (default: ./output)
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
| `--limit 3` | Process first 3 files (test batch) |
| `--type audio` | Process all files of a type: `doc`, `image`, `audio`, `video` |
| `--file "name"` | Process files matching name (case-insensitive) |

Flags can be combined: `--type audio --limit 1`

## How it works

1. Lists all files in the Drive source folder recursively
2. Compares against `manifest.json` to find what's new or changed
3. Purges entries for files deleted from Drive
4. Downloads and converts pending files:
   - `.docx` / Google Docs — text extraction via mammoth
   - `.xlsx / .csv` / Google Sheets — interpreted by Gemini
   - `.pptx` / Google Slides — text extraction per slide
   - `.jpg / .png / .heic / .mp3 / .mp4 / .pdf` etc. — transcribed/described via Gemini
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
