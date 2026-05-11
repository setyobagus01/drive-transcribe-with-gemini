<required_reading>
references/cli-reference.md
</required_reading>

<process>
**Targeting a specific file by name:**

```powershell
& "scripts/run.ps1" --file "partial name here"
```

- Match is case-insensitive substring of the filename
- Forces re-queue even if previously skipped or errored
- Do NOT include path separators — name only

**Targeting all files of a format type:**

```powershell
& "scripts/run.ps1" --type audio --limit 1
```

Valid types: `doc`, `image`, `audio`, `video`

- `--type` forces re-queue of all previously skipped files of that type
- Combine with `--limit 1` for a single test before bulk processing
- Audio/video files can take 1–5 minutes each; set timeout to 600000ms

**After running, check the output file at your configured `OUTPUT_DIR` path.**
</process>

<success_criteria>
- [ ] Target file found and processed (DONE log line)
- [ ] Output `.md` file present in configured `OUTPUT_DIR`
- [ ] No FAIL in log output
</success_criteria>
