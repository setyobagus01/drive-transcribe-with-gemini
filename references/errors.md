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

The script always uses a service account to call the Drive API. Fix checklist:

1. **Drive API enabled?** → Go to Google Cloud Console → APIs & Services → confirm "Google Drive API" is enabled for your project. If not, enable it and wait ~1 min.
2. **Service account JSON correct?** → Check `GOOGLE_CREDENTIALS` in `.env` points to the right file and the file exists.
3. **Folder shared with service account?** → Open the Drive folder → Share → confirm the service account email (ends in `@...iam.gserviceaccount.com`) is listed as Viewer. If not, add it.

**Verify fix:**
```powershell
& "<skill-dir>/scripts/run.ps1" --status 2>$null
```
</error_drive_not_accessible>
