# Loop Engineering installer (PowerShell) — copies the bundled skills into your agent's skills dir.
# Usage: irm https://raw.githubusercontent.com/XuanRuiMu/loop-engineering/main/install.ps1 | iex
#   or:  install.ps1 [TARGET_DIR]   (default = ~/.claude/skills)
$ErrorActionPreference = "Stop"

$Repo  = "XuanRuiMu/loop-engineering"
$Branch = "main"
$Target = if ($args.Count -gt 0) { $args[0] } else { Join-Path $HOME ".claude/skills" }

Write-Host "Loop Engineering installer"
Write-Host "Target: $Target"
New-Item -ItemType Directory -Force -Path $Target | Out-Null

$tmp = New-Item -ItemType Directory -Path (Join-Path $env:TEMP ("loop-install-" + (Get-Random))) | Select-Object -ExpandProperty FullName
$url = "https://github.com/$Repo/archive/refs/heads/$Branch.tar.gz"
$zip = Join-Path $tmp "loop.tgz"
Write-Host "Downloading $url"
Invoke-WebRequest -Uri $url -OutFile $zip
tar -xzf $zip -C $tmp
$src = Join-Path $tmp "loop-engineering-$Branch" "skills"
Copy-Item -Path (Join-Path $src "*") -Destination $Target -Recurse -Force
Remove-Item $tmp -Recurse -Force

Write-Host "Installed. Restart your agent to load the skills."
