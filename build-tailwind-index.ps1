$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Path '.\tailwindcss-v3.exe')) {
  throw 'No se encontró tailwindcss-v3.exe en la raíz del proyecto.'
}

if (-not (Test-Path '.\tailwind\index.input.css')) {
  throw 'No se encontró tailwind/index.input.css.'
}

New-Item -ItemType Directory -Force -Path '.\assets\css' | Out-Null

.\tailwindcss-v3.exe -i .\tailwind\index.input.css -o .\assets\css\index.css -c .\tailwind.config.js --minify
Write-Host 'CSS compilado: assets/css/index.css (Tailwind v3)'
