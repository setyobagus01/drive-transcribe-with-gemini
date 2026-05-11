<error_timeout>
**Symptom:** Command hangs or raises a timeout exception mid-sync.

**Causes & fixes:**

1. **PowerShell timeout too low** — always run with `timeout=600000` (10 min). Audio/video files can take 1–5 min each.

2. **File is too long** — videos over ~45 min or unusually large audio may exceed Gemini's token budget. Skip with `--limit 1` to isolate the offending file, then decide to exclude it.

3. **Gemini rate limit hit** — if many files queue at once, RPM (60/min on paid tier) can be exhausted. Use `--limit 5` to pace the run.

4. **Increase per-file timeout in config** — `PER_FILE_TIMEOUT` in `config.py` defaults to 1800s; raise it for very long videos if needed.
</error_timeout>

<error_drive_not_accessible>
**Symptom:** `HttpError 403`, `HttpError 404`, `File not found`, or `Access denied` when listing or downloading files.

**Root cause:** The Drive folder or its files are not accessible to the account or method being used.

**Option A — Make the folder public (simplest)**

1. Open the folder in Google Drive
2. Right-click → **Share**
3. Change access to **Anyone with the link** → **Viewer**
4. Click **Done**
5. Remove (or leave absent) the `GOOGLE_CREDENTIALS` line from `.env` — the script will use public access

**Option B — Use a service account with credential.json (for private folders)**

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → your project
2. Enable the **Google Drive API**
3. Create a **Service Account** → download the JSON key → save as `credential.json`
4. Copy the service account email (ends in `@...iam.gserviceaccount.com`)
5. Open your Drive folder → Share → paste the service account email → **Viewer**
6. Set in `.env`:
   ```env
   GOOGLE_CREDENTIALS="./credential.json"
   ```

**Verify fix:**
```powershell
& "<skill-dir>/scripts/run.ps1" --status 2>$null
```
</error_drive_not_accessible>
