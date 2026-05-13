# Wrapper for azd postprovision hook (Windows PowerShell).
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $ScriptDir
Set-Location $Root
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
& .\.venv\Scripts\Activate.ps1
pip install --quiet --upgrade pip
pip install --quiet azure-identity azure-search-documents azure-cosmos
python scripts/load_search_index.py
