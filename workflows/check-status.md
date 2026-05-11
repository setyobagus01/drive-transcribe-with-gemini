<process>
Run:
```powershell
& "scripts/run.ps1" --status 2>$null
```

Report the output to the user:
- TO ADD count and file list
- TO REMOVE count (deleted from Drive)
- ALREADY SYNCED count

If there are files to add, ask: "Ready to run the sync?"
</process>

<success_criteria>
- [ ] Status output displayed clearly
- [ ] User informed of pending count
</success_criteria>
