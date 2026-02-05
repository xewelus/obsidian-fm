$ErrorActionPreference = 'Stop'

# Remove tracked directories that shouldn't be public
$dirs = @('.claude','ai','src/obsidian_fm.egg-info','src/obsidian_fm/__pycache__','tests/__pycache__')
foreach ($d in $dirs) {
  if (Test-Path $d) {
    Write-Host "git rm -r $d" -ForegroundColor Yellow
    git rm -r --ignore-unmatch -- $d
  }
}

# Remove tracked pyc files anywhere
$pyc = @(git ls-files '*.pyc')
if ($pyc.Count -gt 0) {
  Write-Host "git rm (pyc) count=$($pyc.Count)" -ForegroundColor Yellow
  git rm --ignore-unmatch -- $pyc
}

Write-Host "Done" -ForegroundColor Green
