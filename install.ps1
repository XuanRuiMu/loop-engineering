param(
    [Parameter(Position = 0)]
    [string]$TargetDir,
    [switch]$Remote,
    [switch]$Force,
    [switch]$AllowDirty,
    [switch]$RecoverStaleLock,
    [switch]$PurgeBackups,
    [string]$RemoteCommit
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($TargetDir)) {
    throw "TargetDir is required; pass the active agent skills directory explicitly."
}
if ($Remote -and $RemoteCommit -notmatch '^[0-9a-fA-F]{40}$') {
    throw "RemoteCommit must be a full 40-character audited commit SHA when -Remote is used."
}
$Target = [IO.Path]::GetFullPath($TargetDir)
$ManagedMarker = "loop-engineering-managed-v1"
$targetCreated = $false

function Assert-NoReparseAncestor([string]$Path) {
    $current = [IO.Path]::GetFullPath($Path)
    while ($true) {
        if (Test-Path -LiteralPath $current) {
            $item = Get-Item -LiteralPath $current -Force
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "Reparse point is not allowed: $current"
            }
        }
        $parent = [IO.Directory]::GetParent($current)
        if ($null -eq $parent -or $parent.FullName -eq $current) { break }
        $current = $parent.FullName
    }
}

function Assert-SafeSource([string]$Path) {
    foreach ($item in @(Get-ChildItem -LiteralPath $Path -Recurse -Force)) {
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "Source reparse point is not allowed: $($item.FullName)"
        }
        if ($item.PSIsContainer) { continue }
        $name = $item.Name.ToLowerInvariant()
        $extension = $item.Extension.ToLowerInvariant()
        if ($name -eq ".env" -or $name -like ".env.*" -or $extension -in @(".env", ".pem", ".key", ".p12", ".pfx") -or $name -in @(".npmrc", ".pypirc", "credentials.json", "id_rsa") -or $name -match "(^|[._-])(auth|secrets?|credentials?|tokens?|passwords?|private)([._-]|$)" -or $name -match "(secret|credential|token|password|private)$") {
            throw "Sensitive or secret-like source file is not installable: $($item.FullName)"
        }
    }
}

Assert-NoReparseAncestor $Target
if (Test-Path -LiteralPath $Target) {
    $targetItem = Get-Item -LiteralPath $Target -Force
    if (-not $targetItem.PSIsContainer) {
        throw "Target must be a directory: $Target"
    }
} else {
    New-Item -ItemType Directory -Path $Target | Out-Null
    $targetCreated = $true
}
$lock = Join-Path $Target ".loop-install.lock"
if (Test-Path -LiteralPath $lock) {
    $lockItem = Get-Item -LiteralPath $lock -Force
    if (($lockItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "Installer lock must not be a reparse point: $lock"
    }
    if ($RecoverStaleLock) {
        $ownerFile = Join-Path $lock "owner.json"
        if (-not (Test-Path -LiteralPath $ownerFile)) {
            throw "Installer lock owner metadata is missing; review manually before recovery: $lock"
        }
        try {
            $owner = Get-Content -LiteralPath $ownerFile -Raw | ConvertFrom-Json
            $ownerPid = [int]$owner.pid
            $ownerHost = [string]$owner.host
            $ownerStarted = [DateTime]::Parse([string]$owner.started).ToUniversalTime()
        } catch {
            throw "Installer lock owner metadata is invalid; review manually before recovery: $lock"
        }
        if ($ownerPid -lt 1 -or [string]::IsNullOrWhiteSpace($ownerHost) -or $ownerStarted -eq [DateTime]::MinValue) {
            throw "Installer lock owner metadata is invalid; review manually before recovery: $lock"
        }
        if ($ownerHost -ne [Environment]::MachineName) {
            Remove-Item -LiteralPath $lock -Recurse -Force
        } else {
            $ownerProcess = Get-Process -Id $ownerPid -ErrorAction SilentlyContinue
            if ($ownerProcess) {
                $sameOwner = $false
                try {
                    $sameOwner = $ownerProcess.StartTime.ToUniversalTime() -eq $ownerStarted
                } catch {
                    throw "Installer lock owner start time cannot be verified; review manually before recovery: $lock"
                }
                if ($sameOwner) {
                    throw "Installer lock owner is still running (PID $ownerPid)."
                }
            }
            Remove-Item -LiteralPath $lock -Recurse -Force
        }
    } else {
        throw "Installer lock exists; verify no installer is running and use -RecoverStaleLock only after review: $lock"
    }
}
$lockCreated = $false
try {
    New-Item -ItemType Directory -Path $lock -ErrorAction Stop | Out-Null
    $lockCreated = $true
    [pscustomobject]@{ pid = $PID; host = [Environment]::MachineName; started = [DateTime]::UtcNow.ToString("o") } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $lock "owner.json") -Encoding UTF8
} catch {
    if ($lockCreated -and (Test-Path -LiteralPath $lock)) {
        Remove-Item -LiteralPath $lock -Recurse -Force -ErrorAction SilentlyContinue
    }
    throw "Another installer is running or the target is not writable: $lock"
}
$records = @()
$BackupRoot = $null
$tmp = $null
try {
    if ($Remote) {
        $repo = "XuanRuiMu/loop-engineering"
        $tmp = New-Item -ItemType Directory -Path (Join-Path $env:TEMP ("loop-install-" + [guid]::NewGuid().ToString("N"))) | Select-Object -ExpandProperty FullName
        $url = "https://github.com/$repo/archive/$RemoteCommit.tar.gz"
        $archive = Join-Path $tmp "loop.tgz"
        Invoke-WebRequest -Uri $url -OutFile $archive
        tar -xzf $archive -C $tmp
        if ($LASTEXITCODE -ne 0) { throw "Remote archive extraction failed." }
        $src = Join-Path $tmp ("loop-engineering-$RemoteCommit/skills")
    } else {
        $src = Join-Path $RepoRoot "skills"
        $gitRoot = $null
        $gitExit = 1
        try {
            $gitRoot = & git -C $RepoRoot rev-parse --show-toplevel 2>$null
            $gitExit = $LASTEXITCODE
        } catch {
            $gitExit = 1
        }
        if ($gitExit -eq 0 -and -not $AllowDirty) {
            $dirty = & git -C $gitRoot status --porcelain 2>$null
            if ($dirty) {
                throw "Source worktree is dirty; review it and pass -AllowDirty to install intentionally."
            }
        }
    }
    if (-not (Test-Path -LiteralPath $src -PathType Container)) {
        throw "Skills directory not found: $src"
    }
    Assert-NoReparseAncestor $src
    $srcFull = [IO.Path]::GetFullPath($src)
    $targetFull = [IO.Path]::GetFullPath($Target).TrimEnd('\') + '\'
    $sourceFull = $srcFull.TrimEnd('\') + '\'
    if ($sourceFull.StartsWith($targetFull, [StringComparison]::OrdinalIgnoreCase) -or $targetFull.StartsWith($sourceFull, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Source and target must not overlap: $src -> $Target"
    }
    Assert-SafeSource $src
    $staleStages = @(Get-ChildItem -LiteralPath $Target -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -like ".loop-stage-*" })
    if ($staleStages.Count -gt 0) {
        throw "Stale installer stage requires manual review before retrying: $($staleStages.FullName -join ', ')"
    }
    $sourceEntries = @(Get-ChildItem -LiteralPath $src -Force | Where-Object { $_.Name -ne "__pycache__" })
    $nonDirectories = @($sourceEntries | Where-Object { -not $_.PSIsContainer })
    if ($nonDirectories.Count -gt 0) {
        throw "Managed skills must contain directories only: $($nonDirectories.FullName -join ', ')"
    }
    $entries = @($sourceEntries | Where-Object { $_.PSIsContainer })
    $missingSkill = @($entries | Where-Object { -not (Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") -PathType Leaf) })
    if ($missingSkill.Count -gt 0) {
        throw "Managed source entries must contain SKILL.md: $($missingSkill.FullName -join ', ')"
    }
    foreach ($entry in $entries) {
        $destination = Join-Path $Target $entry.Name
        if (Test-Path -LiteralPath $destination) {
            $destinationItem = Get-Item -LiteralPath $destination -Force
            if (($destinationItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "Managed destination must not be a reparse point: $destination"
            }
            if (-not $destinationItem.PSIsContainer) {
                throw "Managed destination must be a directory: $destination"
            }
            if (-not $Force) {
                throw "Destination exists; use -Force to replace managed skill entry: $destination"
            }
            $marker = Join-Path $destination ".loop-managed"
            $markerValue = if (Test-Path -LiteralPath $marker -PathType Leaf) { (Get-Content -LiteralPath $marker -Raw).Trim().TrimStart([char]0xFEFF) } else { "" }
            if (-not (Test-Path -LiteralPath $marker -PathType Leaf) -or $markerValue -ne $ManagedMarker) {
                throw "Refusing to overwrite an unmarked or foreign destination: $destination"
            }
        }
    }
    foreach ($entry in $entries) {
        $destination = Join-Path $Target $entry.Name
        $stage = Join-Path $Target (".loop-stage-" + [guid]::NewGuid().ToString("N"))
        New-Item -ItemType Directory -Path $stage | Out-Null
        Get-ChildItem -LiteralPath $entry.FullName -Force | Where-Object { $_.Name -ne "__pycache__" } | Copy-Item -Destination $stage -Recurse -Force
        Get-ChildItem -LiteralPath $stage -Directory -Filter "__pycache__" -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
        Get-ChildItem -LiteralPath $stage -File -Filter "*.pyc" -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force
        Set-Content -LiteralPath (Join-Path $stage ".loop-managed") -Value $ManagedMarker -Encoding UTF8
        $records += [pscustomobject]@{ Name = $entry.Name; Destination = $destination; Stage = $stage; Backup = $null; Installed = $false }
    }
    $BackupRoot = Join-Path (Split-Path -Parent $Target) (".loop-backups-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $BackupRoot -ErrorAction Stop | Out-Null
    $committed = $false
    try {
        foreach ($record in $records) {
            if (Test-Path -LiteralPath $record.Destination) {
                $record.Backup = Join-Path $BackupRoot $record.Name
                Move-Item -LiteralPath $record.Destination -Destination $record.Backup
            }
        }
        foreach ($record in $records) {
            Move-Item -LiteralPath $record.Stage -Destination $record.Destination
            $record.Stage = $null
            $record.Installed = $true
        }
        $committed = $true
    } catch {
        if (-not $committed) {
            foreach ($record in $records) {
                if ($record.Installed -and (Test-Path -LiteralPath $record.Destination)) {
                    Remove-Item -LiteralPath $record.Destination -Recurse -Force
                }
                if ($record.Backup -and (Test-Path -LiteralPath $record.Backup)) {
                    Move-Item -LiteralPath $record.Backup -Destination $record.Destination
                }
            }
        }
        throw
    }
    foreach ($record in $records) {
        if ($record.Backup -and (Test-Path -LiteralPath $record.Backup)) {
            if ($PurgeBackups) {
                Remove-Item -LiteralPath $record.Backup -Recurse -Force -ErrorAction SilentlyContinue
            } else {
                Write-Host "Retained recoverable backup: $($record.Backup)"
            }
        }
    }
    if ($PurgeBackups) {
        foreach ($backupDirectory in @(Get-ChildItem -LiteralPath (Split-Path -Parent $Target) -Directory -Force -Filter ".loop-backups-*" -ErrorAction SilentlyContinue)) {
            Remove-Item -LiteralPath $backupDirectory.FullName -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    Write-Host "Copied managed skills to $Target. Runtime reload/load verification is not implied."
} finally {
    foreach ($record in $records) {
        if ($record.Stage -and (Test-Path -LiteralPath $record.Stage)) {
            Remove-Item -LiteralPath $record.Stage -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    if ($tmp -and (Test-Path -LiteralPath $tmp)) {
        Remove-Item -LiteralPath $tmp -Recurse -Force
    }
    if (Test-Path -LiteralPath $lock) {
        Remove-Item -LiteralPath $lock -Recurse -Force -ErrorAction SilentlyContinue
    }
    if ($BackupRoot -and (Test-Path -LiteralPath $BackupRoot) -and -not (Get-ChildItem -LiteralPath $BackupRoot -Force)) {
        Remove-Item -LiteralPath $BackupRoot -Force -ErrorAction SilentlyContinue
    }
    if ($targetCreated -and (Test-Path -LiteralPath $Target) -and -not (Get-ChildItem -LiteralPath $Target -Force)) {
        Remove-Item -LiteralPath $Target -Force -ErrorAction SilentlyContinue
    }
}
