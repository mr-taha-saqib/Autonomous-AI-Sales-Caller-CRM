# Local development bootstrap for Windows (PowerShell).
# Runs the backend (uvicorn) and frontend (next dev) against a local Postgres.

Write-Host "▶ Algorixe dev bootstrap" -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    Copy-Item "config/.env.example" ".env"
    Write-Host "Created .env from template — fill in TWILIO_* and ANTHROPIC_API_KEY." -ForegroundColor Yellow
}

# Backend
Push-Location backend
if (-not (Test-Path ".venv")) { python -m venv .venv }
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.cli seed
Start-Process powershell -ArgumentList "-NoExit","-Command","uvicorn app.main:app --reload --port 8000"
Pop-Location

# Frontend
Push-Location frontend
npm install
Start-Process powershell -ArgumentList "-NoExit","-Command","npm run dev"
Pop-Location

Write-Host "✅ Dev servers launching: API http://localhost:8000  Web http://localhost:3000" -ForegroundColor Green
