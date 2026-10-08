# Builds dist\FlypadKeepalive.exe with PyInstaller.
#
# Usage (PowerShell, from the repo root):
#     .\build.ps1
#
# Creates .venv with the pinned build dependencies the first time.
# Note: installing vgamepad with pip may launch the old ViGEmBus installer bundled with it.
# It is not needed for building; cancel it (use drivers\ for the reference v1.22.0 driver).

# Not "Stop": PyInstaller logs to stderr, which PowerShell would treat as an error.
# Failures are detected through $LASTEXITCODE instead.
Set-Location $PSScriptRoot

$python = ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "Creating .venv..."
    python -m venv .venv
}

Write-Host "Installing build dependencies..."
& $python -m pip install --disable-pip-version-check -q -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }

Write-Host "Building..."
& $python -m PyInstaller --clean --noconfirm flypad_keepalive.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

$exe = Get-Item dist\FlypadKeepalive.exe
Write-Host ("Done: {0} ({1:N1} MB)" -f $exe.FullName, ($exe.Length / 1MB))
