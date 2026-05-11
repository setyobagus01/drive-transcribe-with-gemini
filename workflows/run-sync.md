<required_reading>
references/cli-reference.md
</required_reading>

<process>
**Step 1: Ask the user two questions**

Use AskUserQuestion with both questions at once:

Question 1 — file types (multiselect):
- All types
- Documents (doc)
- Images (image)
- Audio (audio)
- Video (video)

Question 2 — batch size (single select):
- All pending files
- Limited batch (ask how many if selected — default: 3)

**Recommended test set** (covers all converter paths):

| File | Converter path |
|------|---------------|
| 3× `.jpg/.png/.webp` | Gemini inline image |
| 1× `.heic` | Gemini Files API image |
| 1× `.docx` / Google Doc | mammoth / python-docx |
| 1× `.xlsx` / `.csv` / Google Sheet | Gemini spreadsheet |
| 1× `.pptx` / Google Slides | python-pptx |
| 1× `.pdf` | Gemini Files API |
| 1× `.txt` | passthrough → `.md` |
| 1× `.mp3/.wav/.m4a` | Gemini audio |
| 1× `.mp4/.mov` | Gemini video |

**Step 2: Build the command(s)**

Base (Windows / Linux+macOS):
```powershell
& "<skill-dir>/scripts/run.ps1" [flags]   # Windows
bash "<skill-dir>/scripts/run.sh" [flags] # Linux/macOS
```

- If **All types** selected → no `--type` flag
- If **specific types** selected → `--type` only accepts one value; run one command per type
- If **limited batch** → add `--limit N` to each command

Examples:
```powershell
& "scripts/run.ps1" --limit 3
& "scripts/run.ps1" --type audio
& "scripts/run.ps1" --type image --limit 5

# Multiple types selected — run sequentially:
& "scripts/run.ps1" --type image --limit 3
& "scripts/run.ps1" --type doc --limit 3
```

Set timeout to 600000ms — audio/video files can take several minutes each.

**Step 3: Report results**

From the log output, report:
- How many files were processed
- Any failures (FAIL lines)
- Output location confirmation
</process>

<success_criteria>
- [ ] Command completed without unhandled exceptions
- [ ] Progress logged to completion (`Done. Output in: ...`)
- [ ] Any FAILed files noted for follow-up
</success_criteria>
