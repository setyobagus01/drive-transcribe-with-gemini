# Runs main.py with any flags. Requires global pip install (see setup).
# Examples:
#   run.ps1 --status
#   run.ps1 --limit 3
#   run.ps1 --type audio --limit 1
#   run.ps1 --file "photo name"
Set-Location $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"
python main.py $args
