# Run IPL Insights with the project venv (ensures plotly & all deps are available).
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root "venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "venv not found. Create it and run: pip install -r requirements.txt"
    exit 1
}

& $Python -m pip install -r (Join-Path $Root "requirements.txt") -q
& $Python -m streamlit run (Join-Path $Root "dashboard\app.py")
