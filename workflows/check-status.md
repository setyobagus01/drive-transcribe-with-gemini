<required_reading>
references/cli-reference.md
</required_reading>

<process>
Run:
```powershell
& "<skill-dir>/scripts/run.ps1" --status 2>$null
```

Report the output to the user:
- `TO ADD` count and file list
- `TO REMOVE` count (deleted from Drive)
- `ALREADY SYNCED` count

If there are files to add, ask: "Ready to run the sync?"
</process>

<success_criteria>
- [ ] Status output displayed clearly
- [ ] User informed of pending count
</success_criteria>
