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

**Step 3: Drive access method**

Ask the user:
> "How should Claude access your Drive folder?"
> 1. **Public folder** — easiest, no credentials needed (folder must be shared: Anyone with link → Viewer)
> 2. **Service account** — private folder, requires a `credential.json` file from Google Cloud Console

If they choose **public**:
- Confirm they've shared the folder (right-click → Share → Anyone with the link → Viewer)
- No `GOOGLE_CREDENTIALS` line needed in `.env`

If they choose **service account**:
- Ask for the path to their `credential.json` (or `service-account.json`)
- The service account email must be added as a Viewer on the Drive folder

**Step 4: Output directory**

Ask the user:
> "Where do you want the converted markdown files saved?"

- Default is `./wiki/sources` (relative to the project root)
- They can provide any absolute or relative path

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

Public folder:
```env
SOURCE_FOLDER_ID="<their folder ID>"
GEMINI_API_KEY="<their API key>"
OUTPUT_DIR="<their output path>"
```

Service account:
```env
SOURCE_FOLDER_ID="<their folder ID>"
GEMINI_API_KEY="<their API key>"
GOOGLE_CREDENTIALS="<path to credential.json>"
OUTPUT_DIR="<their output path>"
```

Omit `OUTPUT_DIR` if they're happy with the default (`./output`).

**Step 7: Verify setup**

```powershell
& "scripts/run.ps1" --status 2>$null
```

- If it shows file counts → setup is complete
- If it errors → check `references/errors.md` for Drive access or auth issues
</process>

<success_criteria>
- [ ] `.env` file written with correct values
- [ ] `--status` runs without error
- [ ] File counts are visible (TO ADD / ALREADY SYNCED)
</success_criteria>
