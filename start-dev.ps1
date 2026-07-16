# Arranque local de Flash (API en Docker puerto 8001 + frontend Vite 5173)
# Uso: .\start-dev.ps1
# Nota: el puerto 8000 suele estar ocupado por otros proyectos; Flash usa 8001.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "==> Levantando MySQL + API (Docker Compose, API en :8001)..." -ForegroundColor Cyan
docker compose up -d --build db api

Write-Host "==> Esperando health de la API en :8001 ..." -ForegroundColor Cyan
$ok = $false
for ($i = 0; $i -lt 40; $i++) {
  try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:8001/health" -UseBasicParsing -TimeoutSec 3
    if ($r.StatusCode -eq 200) { $ok = $true; break }
  } catch { Start-Sleep -Seconds 2 }
}
if (-not $ok) {
  Write-Host "La API aun no responde. Revisa: docker compose logs api -f" -ForegroundColor Yellow
} else {
  Write-Host "API OK -> http://127.0.0.1:8001/health" -ForegroundColor Green
  Write-Host "Docs  -> http://127.0.0.1:8001/docs" -ForegroundColor Green
}

Write-Host "==> Iniciando Vite en :5173 ..." -ForegroundColor Cyan
Write-Host "Abre: http://localhost:5173/pages/login.html" -ForegroundColor Green
Set-Location frontend
if (-not (Test-Path node_modules)) { npm install }
npm run dev
