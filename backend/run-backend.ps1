$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

# Cargar variables desde .env (si existe)
$envFile = Join-Path $root '.env'
if (Test-Path $envFile) {
  Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith('#')) { return }
    $parts = $line -split '=', 2
    if ($parts.Count -eq 2) {
      $key = $parts[0].Trim()
      $value = $parts[1].Trim()
      [System.Environment]::SetEnvironmentVariable($key, $value, 'Process')
    }
  }
}

if (-not $env:WEB3FORMS_ACCESS_KEY -or $env:WEB3FORMS_ACCESS_KEY -eq 'REEMPLAZA_CON_TU_ACCESS_KEY_REAL') {
  Write-Host 'WARNING: WEB3FORMS_ACCESS_KEY no esta definida o sigue en placeholder.' -ForegroundColor Yellow
}

Write-Host 'Iniciando backend en http://127.0.0.1:8000 ...' -ForegroundColor Cyan

$uvicorn = Get-Command uvicorn -ErrorAction SilentlyContinue
if ($uvicorn) {
  uvicorn main:app --reload --port 8000
} else {
  python -m uvicorn main:app --reload --port 8000
}
