<cli_flags>
| Flag | Description |
|------|-------------|
| _(none)_ | Process all pending files |
| `--limit N` | Process at most N files (test batches) |
| `--status` | Show pending/removed/synced counts, then exit |
| `--type TYPE` | Filter to one format type: `doc`, `image`, `audio`, `video` |
| `--file PATTERN` | Filter to files whose name contains PATTERN (case-insensitive) |

Flags can be combined: `--type audio --limit 3`
</cli_flags>

<processing_notes>
- Processing order: doc → image → audio → video (priority sort)
- `--file` and `--type` both force-requeue previously skipped entries
- Audio/video use `gemini-2.5-flash` (uploads via Files API, slower but complete)
- Images use inline `Part.from_bytes` except HEIC/HEIF (also uses Files API)
- `MAX_PARALLEL = 1` — sequential processing, no concurrency
- Manifest at `<OUTPUT_DIR>/manifest.json` (default: `./output/manifest.json` relative to scripts/)
</processing_notes>

<constraints>
- Max file size: 2 GB
- Max video duration: ~64 min (token-derived: 1M ctx ÷ 258 tokens/sec; prompt overhead reduces this further — videos over 45 min may fail)
- Max audio duration: ~8 hours (32 tokens/sec)
- Gemini RPM: 60 (paid tier)
- Per-file timeout: 1800s (config), set PowerShell timeout to 600000ms
</constraints>
