$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Path '.\tailwindcss-v3.exe')) {
  throw 'No se encontro tailwindcss-v3.exe en la raiz del proyecto.'
}

if (-not (Test-Path '.\tailwind\contacto.input.css')) {
  throw 'No se encontro tailwind/contacto.input.css.'
}

New-Item -ItemType Directory -Force -Path '.\assets\css' | Out-Null

.\tailwindcss-v3.exe -i .\tailwind\contacto.input.css -o .\assets\css\contacto.css -c .\tailwind.contacto.config.js --minify
Write-Host 'CSS compilado: assets/css/contacto.css (Tailwind v3)'
