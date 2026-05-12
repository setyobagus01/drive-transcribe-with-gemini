<process>
**Step 0: Install the skill (if not already installed)**

```bash
npx skills add setyobagus01/drive-transcribe-with-gemini
```

**Step 1: Gemini API key**

Ask the user:
> "Do you already have a Gemini API key?"

- **Yes** → ask them to paste it (or confirm they'll add it manually to `.env`)
- **No** → direct them: get one free at https://aistudio.google.com/apikey — click **Get API key**, copy it, come back

**Step 2: Google Drive folder ID**

Ask the user:
> "What is the Google Drive folder ID that contains your files?"

The folder ID is the string after `/folders/` in the Drive URL:
```
https://drive.google.com/drive/folders/1ABC123xyz...
                                        ^^^^^^^^^^^^^ this part
```

**Step 3: Output directory**

Ask the user:
> "Where do you want the converted markdown files saved?"

- Default is `./output` (relative to the project root)
- They can provide any absolute or relative path
- If they're happy with the default, skip `OUTPUT_DIR` in the `.env`

**Step 4: Install dependencies (once)**

```powershell
pip install -r "<skill-dir>/scripts/requirements.txt"
```

On Linux/macOS, also make the run script executable (once):
```bash
chmod +x "<skill-dir>/scripts/run.sh"
```

**Step 5: Write the .env file**

Create at `<skill-dir>/scripts/.env`:

```env
SOURCE_FOLDER_ID="<their folder ID>"
GEMINI_API_KEY="<their API key>"
OUTPUT_DIR="<their output path>"
```

Omit `OUTPUT_DIR` if they're using the default (`./output`). Do NOT add `GOOGLE_CREDENTIALS` at this stage.

**Step 6: Verify setup**

```powershell
& "<skill-dir>/scripts/run.ps1" --status 2>$null
```

- If it shows file counts → setup is complete
- If it returns `HttpError 403 / 404` or `Access denied` → the folder is private; follow the `<drive_access>` fallback in `SKILL.md` to collect service account credentials and retry
</process>

<success_criteria>
- [ ] `.env` file written with correct values
- [ ] `--status` runs without error
- [ ] File counts are visible (TO ADD / ALREADY SYNCED)
</success_criteria>
