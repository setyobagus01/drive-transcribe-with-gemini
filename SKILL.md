---
name: drive-transcribe-with-gemini
description: Converts Google Drive files — docs, images, audio, video — to local markdown. Use for Drive→markdown sync, status checks, or targeting specific files/types. Gemini-powered transcription; incremental reruns.
---

<objective>
Converts Google Drive files — documents, spreadsheets, images, audio, and video — to local markdown files using Gemini transcription. Handles incremental sync (only unprocessed files), status checks, and targeted processing by file name or format type. The output is structured markdown written to a local directory, suitable for note vaults or knowledge bases.
</objective>

<quick_start>
1. Install dependencies (once):
```powershell
pip install -r "<skill-dir>/scripts/requirements.txt"
```
2. Create `scripts\.env` with at minimum:
```
GEMINI_API_KEY=your_key_here
SOURCE_FOLDER_ID=your_drive_folder_id
```
3. Verify setup with a dry status check:
```powershell
& "<skill-dir>/scripts/run.ps1" --status
```
If it lists files without errors, you're ready to sync.
</quick_start>

<requirements>
**Python:** 3.9+

**.env file** — create at `scripts\.env`:
| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | yes | Get free at https://aistudio.google.com/apikey |
| `SOURCE_FOLDER_ID` | yes | Drive folder ID — the part after `/folders/` in the URL |
| `GOOGLE_CREDENTIALS` | if private folder | Path to service account `credential.json` |
| `OUTPUT_DIR` | no | Output folder (default: `./output`) |
</requirements>

<essential_principles>
**Use the run script for all commands** — path is relative to this skill's directory:
```powershell
# Windows (PowerShell)
& "<skill-dir>/scripts/run.ps1" [flags]

# Linux / macOS
bash "<skill-dir>/scripts/run.sh" [flags]
```
Claude: derive `<skill-dir>` from the path where you read this SKILL.md.

**Models:**
- `gemini-2.5-flash-lite` — images, docs (fast/cheap)
- `gemini-2.5-flash` — audio, video, HEIC (handles long content)

**Supported formats:** `.docx .xlsx .csv .pptx .txt .md .pdf .jpg .png .gif .webp .bmp .heic .heif .mp3 .wav .m4a .ogg .flac .mp4 .mov .avi .webm .mkv`

**Common errors — quick lookup:**
| Symptom | Cause | Action |
|---------|-------|--------|
| `Set GEMINI_API_KEY env var` | Missing key in `.env` | Run setup (option 4) |
| `HttpError 403 / 404` | Drive not accessible | See `references/errors.md` |
| Hangs / timeout | File too large or rate limit hit | See `references/errors.md` |
| `FileNotFoundError: credentials.json` | Missing service account file | Set `GOOGLE_CREDENTIALS` in `.env` |
</essential_principles>

<intake>
What do you want to do?

1. **Run sync** — process pending files (full run or test batch)
2. **Check status** — see what's pending without processing anything
3. **Target specific file or type** — process one file by name or all files of a format type
4. **Setup** — configure Gemini API key and Google Drive folder
5. **Troubleshoot an error** — fix timeout, Drive access, or auth issues

**Wait for response before proceeding.**
</intake>

<routing>
| Response | Workflow |
|----------|----------|
| 1, "run", "sync", "process", "full" | `workflows/run-sync.md` |
| 2, "status", "check", "pending", "what's" | `workflows/check-status.md` |
| 3, "target", "file", "type", "specific", "audio", "video", "image", "doc" | `workflows/target.md` |
| 4, "setup", "configure", "api key", "folder", "first time", "credential" | `workflows/setup.md` |
| 5, "error", "timeout", "403", "404", "access denied", "not found", "troubleshoot" | Read `references/errors.md` and guide the user through the matching fix |
| _(unrecognized)_ | Re-display the `<intake>` menu and ask the user to pick a number |

**After reading the workflow, follow it exactly.**
</routing>

<success_criteria>
- [ ] User intent was identified and mapped to a workflow
- [ ] Correct workflow file was read before taking action
- [ ] At least one file was processed without a FAIL log line, or the user received a clear status or error summary
- [ ] Output confirmed present in configured `OUTPUT_DIR` (for processing workflows)
</success_criteria>

<reference_index>
- **CLI flags and usage:** `references/cli-reference.md`
- **Converter behavior and output cleaning:** `references/converters.md`
- **Error troubleshooting:** `references/errors.md`
</reference_index>

<workflows_index>
| Workflow | Purpose |
|----------|---------|
| run-sync.md | Full sync or limited test batch |
| check-status.md | Show pending files without processing |
| target.md | Process by file name or format type |
| setup.md | First-time config: Gemini API key + Drive folder access |
</workflows_index>
