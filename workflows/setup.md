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

**Step 2: Google Cloud service account**

Ask the user:
> "Do you have a Google Cloud service account JSON key for Drive access?"

- **Yes** → ask for the path to the file
- **No** → walk them through these steps:
  1. Go to [Google Cloud Console](https://console.cloud.google.com/) → create or select a project
  2. Enable the **Google Drive API**: APIs & Services → Library → search "Google Drive API" → Enable
  3. Create a service account: IAM & Admin → Service Accounts → Create → download JSON key
  4. Save the JSON file as `credential.json` inside `<skill-dir>/scripts/`
  5. Open the Drive folder → Share → paste the service account email (ends in `@...iam.gserviceaccount.com`) → **Viewer** → Done

**Step 3: Google Drive folder ID**

Ask the user:
> "What is the Google Drive folder ID that contains your files?"

The folder ID is the string after `/folders/` in the Drive URL:
```
https://drive.google.com/drive/folders/1ABC123xyz...
                                        ^^^^^^^^^^^^^ this part
```

**Step 4: Output directory**

Ask the user:
> "Where do you want the converted markdown files saved?"

- Default is `./output` (relative to the project root)
- They can provide any absolute or relative path
- If they're happy with the default, skip `OUTPUT_DIR` in the `.env`

**Step 5: Install dependencies (once)**

```powershell
pip install -r "<skill-dir>/scripts/requirements.txt"
```

On Linux/macOS, also make the run script executable (once):
```bash
chmod +x "<skill-dir>/scripts/run.sh"
```

**Step 6: Write the .env file**

Create at `<skill-dir>/scripts/.env`:

```env
SOURCE_FOLDER_ID="<their folder ID>"
GEMINI_API_KEY="<their Gemini key>"
GOOGLE_CREDENTIALS="<path to credential.json>"
OUTPUT_DIR="<their output path>"
```

Omit `OUTPUT_DIR` if they're using the default (`./output`).

**Step 7: Verify setup**

```powershell
& "<skill-dir>/scripts/run.ps1" --status 2>$null
```

- If it shows file counts → setup is complete
- If it returns `accessNotConfigured` → Drive API not enabled; go back to Step 2
- If it returns `HttpError 403` → service account email not added to the folder; go back to Step 2 item 5
</process>

<success_criteria>
- [ ] `.env` file written with correct values
- [ ] `--status` runs without error
- [ ] File counts are visible (TO ADD / ALREADY SYNCED)
</success_criteria>
