# =============================================================================
# Typhon — Typhon's Forge Shop Machine Setup
# Dedicated shop node: slicing, commissions, content, accounting
# Run as Administrator in PowerShell
# =============================================================================

param(
    [switch]$SkipBloatRemoval,
    [switch]$SkipInstalls,
    [switch]$SkipWSL
)

$ErrorActionPreference = "Continue"

function Write-Step { param($msg) Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-OK   { param($msg) Write-Host "    [OK] $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "    [!!] $msg" -ForegroundColor Yellow }

Write-Host @"
 ___  _   ___  _  _  ___  _  _
|_ _|| | | _ \| || ||_ _|| \| |
 | | | |_|  _/| __ | | | | .  |
|___||___|_|  |_||_||___||_|\_|

Typhon's Forge — Shop Machine Setup
Slicing / Commissions / Content / Accounting
"@ -ForegroundColor Magenta

# =============================================================================
# REQUIRE ADMIN
# =============================================================================
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)) {
    Write-Warn "Not running as Administrator. Relaunching..."
    Start-Process powershell "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# =============================================================================
# 1. DEBLOAT — remove everything except Microsoft Office
# =============================================================================
if (-not $SkipBloatRemoval) {
    Write-Step "Removing bloatware (keeping Microsoft Office)..."

    $bloat = @(
        "Microsoft.3DBuilder"
        "Microsoft.BingFinance"
        "Microsoft.BingNews"
        "Microsoft.BingSearch"
        "Microsoft.BingSports"
        "Microsoft.BingWeather"
        "Microsoft.Cortana"
        "Microsoft.GamingApp"
        "Microsoft.GetHelp"
        "Microsoft.Getstarted"
        "Microsoft.Messaging"
        "Microsoft.Microsoft3DViewer"
        "Microsoft.MicrosoftSolitaireCollection"
        "Microsoft.MicrosoftStickyNotes"
        "Microsoft.MixedReality.Portal"
        "Microsoft.NetworkSpeedTest"
        "Microsoft.News"
        "Microsoft.Office.OneNote"
        "Microsoft.OneConnect"
        "Microsoft.Paint3D"
        "Microsoft.People"
        "Microsoft.Print3D"
        "Microsoft.ScreenSketch"
        "Microsoft.SkypeApp"
        "Microsoft.Teams"
        "Microsoft.Todos"
        "Microsoft.WindowsAlarms"
        "Microsoft.WindowsCamera"
        "Microsoft.windowscommunicationsapps"
        "Microsoft.WindowsFeedbackHub"
        "Microsoft.WindowsMaps"
        "Microsoft.WindowsSoundRecorder"
        "Microsoft.Xbox.TCUI"
        "Microsoft.XboxApp"
        "Microsoft.XboxGameOverlay"
        "Microsoft.XboxGamingOverlay"
        "Microsoft.XboxIdentityProvider"
        "Microsoft.XboxSpeechToTextOverlay"
        "Microsoft.YourPhone"
        "Microsoft.ZuneMusic"
        "Microsoft.ZuneVideo"
        "MicrosoftTeams"
        "Clipchamp.Clipchamp"
        "Disney.37853D22215E2"
        "king.com.CandyCrushSaga"
        "king.com.CandyCrushFriends"
        "king.com.FarmHeroesSaga"
        "Amazon.com.Amazon"
        "SpotifyAB.SpotifyMusic"
        "BytedancePte.Ltd.TikTok"
    )

    foreach ($app in $bloat) {
        $pkg = Get-AppxPackage -Name $app -AllUsers -ErrorAction SilentlyContinue
        if ($pkg) {
            Remove-AppxPackage -Package $pkg.PackageFullName -AllUsers -ErrorAction SilentlyContinue
            Write-OK "Removed $app"
        }
        $prov = Get-AppxProvisionedPackage -Online | Where-Object DisplayName -eq $app
        if ($prov) {
            Remove-AppxProvisionedPackage -Online -PackageName $prov.PackageName -ErrorAction SilentlyContinue
        }
    }

    Write-Step "Disabling Cortana..."
    New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Force | Out-Null
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "AllowCortana" -Value 0 -Force
    Write-OK "Cortana disabled"

    Write-Step "Disabling telemetry..."
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Value 0 -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" -Name "AllowTelemetry" -Value 0 -Force -ErrorAction SilentlyContinue
    Write-OK "Telemetry disabled"

    Write-Step "Disabling OneDrive auto-start..."
    New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\OneDrive" -Force | Out-Null
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\OneDrive" -Name "DisableFileSyncNGSC" -Value 1 -Force
    Write-OK "OneDrive auto-start disabled"

    Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\GameDVR" -Name "AllowGameDVR" -Value 0 -Force -ErrorAction SilentlyContinue
    Write-OK "Game DVR disabled"

    # Disable startup programs that open terminals
    Write-Step "Cleaning startup entries..."
    $startupKeys = @(
        "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    )
    foreach ($key in $startupKeys) {
        $vals = Get-ItemProperty -Path $key -ErrorAction SilentlyContinue
        if ($vals) {
            $vals.PSObject.Properties | Where-Object {
                $_.Name -notmatch "^PS" -and
                ($_.Value -match "cmd|powershell|wscript|cscript" -and $_.Value -notmatch "djinn")
            } | ForEach-Object {
                Remove-ItemProperty -Path $key -Name $_.Name -ErrorAction SilentlyContinue
                Write-Warn "Removed startup entry: $($_.Name)"
            }
        }
    }
    Write-OK "Startup cleaned"

    Write-OK "Debloat complete"
}

# =============================================================================
# 2. WINDOWS FEATURES — OpenSSH, Hyper-V, WSL
# =============================================================================
if (-not $SkipWSL) {
    Write-Step "Enabling Windows features..."

    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 -ErrorAction SilentlyContinue
    Start-Service sshd
    Set-Service -Name sshd -StartupType Automatic
    Write-OK "OpenSSH Server enabled and running"

    Write-Step "Installing WSL2 with Ubuntu..."
    wsl --install -d Ubuntu --no-launch
    Write-OK "WSL2 Ubuntu queued (will complete after reboot)"

    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All -NoRestart -ErrorAction SilentlyContinue
    Write-OK "Hyper-V enabled"
}

# =============================================================================
# 3. PACKAGE INSTALLS via winget
# =============================================================================
if (-not $SkipInstalls) {
    Write-Step "Installing packages via winget..."

    $packages = @(
        @{ id = "Git.Git";                      name = "Git" }
        @{ id = "Python.Python.3.12";           name = "Python 3.12" }
        @{ id = "Tailscale.Tailscale";          name = "Tailscale" }
        @{ id = "Ollama.Ollama";                name = "Ollama" }
        @{ id = "OBSProject.OBSStudio";         name = "OBS Studio" }
        @{ id = "Microsoft.WindowsTerminal";    name = "Windows Terminal" }
        @{ id = "Notepad++.Notepad++";          name = "Notepad++" }
        @{ id = "DEVCOM.JetBrainsMonoNerdFont"; name = "JetBrains Mono Nerd Font" }
        @{ id = "7zip.7zip";                    name = "7-Zip" }
        @{ id = "Rustlang.Rustup";              name = "Rust" }
    )

    foreach ($pkg in $packages) {
        Write-Host "    Installing $($pkg.name)..." -NoNewline
        winget install --id $pkg.id --silent --accept-package-agreements --accept-source-agreements 2>$null
        Write-OK " done"
    }

    # OrcaSlicer — not on winget, download directly
    Write-Step "Installing OrcaSlicer (headless slicing engine)..."
    $orcaVersion = "2.3.0"
    $orcaUrl = "https://github.com/SoftFever/OrcaSlicer/releases/download/v$orcaVersion/OrcaSlicer_Windows_V$orcaVersion.exe"
    $orcaDest = "$env:TEMP\OrcaSlicer_setup.exe"
    Write-Host "    Downloading OrcaSlicer v$orcaVersion..." -NoNewline
    Invoke-WebRequest -Uri $orcaUrl -OutFile $orcaDest -UseBasicParsing
    Start-Process -FilePath $orcaDest -ArgumentList "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART" -Wait
    Remove-Item $orcaDest -ErrorAction SilentlyContinue
    Write-OK "OrcaSlicer installed"

    # MediaMTX — for content streaming
    Write-Step "Installing MediaMTX..."
    $mediamtxUrl = "https://github.com/bluenviron/mediamtx/releases/latest/download/mediamtx_windows_amd64.zip"
    $mediamtxDest = "$env:ProgramFiles\MediaMTX"
    New-Item -ItemType Directory -Force -Path $mediamtxDest | Out-Null
    Invoke-WebRequest -Uri $mediamtxUrl -OutFile "$env:TEMP\mediamtx.zip" -UseBasicParsing
    Expand-Archive -Path "$env:TEMP\mediamtx.zip" -DestinationPath $mediamtxDest -Force
    Remove-Item "$env:TEMP\mediamtx.zip" -ErrorAction SilentlyContinue
    Write-OK "MediaMTX installed"

    Write-OK "Redis will run inside WSL2 Ubuntu — configured post-reboot"
}

# =============================================================================
# 4. FORGE DIRECTORY STRUCTURE
# =============================================================================
Write-Step "Building Forge directory structure..."

$forgeDirs = @(
    "C:\Forge"
    "C:\Forge\queue"           # incoming commission jobs
    "C:\Forge\models"          # working STL/3MF files
    "C:\Forge\gcode"           # sliced output
    "C:\Forge\gcode\penelope"
    "C:\Forge\gcode\calliope"
    "C:\Forge\completed"       # finished jobs, archived
    "C:\Forge\content"         # OBS recordings, timelapses, photos
    "C:\Forge\content\photos"
    "C:\Forge\content\videos"
    "C:\Forge\content\reels"
    "C:\Forge\accounting"      # invoices, orders, receipts
    "C:\Forge\shop"            # Etsy listings, product copy, assets
)

foreach ($dir in $forgeDirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Write-OK "Created $dir"
}

# =============================================================================
# 5. NETWORK — map The Library on Oroborus
# =============================================================================
Write-Step "Mapping The Library (Oroborus storage)..."
# Persistent network drive: Z: → \\192.168.1.176\storage (Oroborus / The Library)
$net = New-Object -ComObject WScript.Network
$net.MapNetworkDrive("Z:", "\\192.168.1.176\storage", $true)
Write-OK "Z: mapped to \\192.168.1.176\storage (The Library)"

# =============================================================================
# 6. SSH CONFIG
# =============================================================================
Write-Step "Configuring OpenSSH..."
$sshdConfig = "C:\ProgramData\ssh\sshd_config"
if (Test-Path $sshdConfig) {
    (Get-Content $sshdConfig) -replace '#PasswordAuthentication yes', 'PasswordAuthentication yes' | Set-Content $sshdConfig
    (Get-Content $sshdConfig) -replace '#PubkeyAuthentication yes', 'PubkeyAuthentication yes' | Set-Content $sshdConfig
    Restart-Service sshd
    Write-OK "SSH configured"
}

$authorizedKeysPath = "$env:ProgramData\ssh\administrators_authorized_keys"
$salomonPubKey = "# Paste Salomon public key here: cat ~/.ssh/id_rsa.pub on Salomon"
Add-Content -Path $authorizedKeysPath -Value $salomonPubKey -ErrorAction SilentlyContinue
Write-Warn "Add Salomon SSH key to: $authorizedKeysPath"

# =============================================================================
# 7. FIREWALL
# =============================================================================
Write-Step "Opening firewall ports..."
$ports = @(
    @{ port = 22;    name = "SSH" }
    @{ port = 8080;  name = "Forge Shop Backend" }
    @{ port = 4455;  name = "OBS WebSocket" }
    @{ port = 8554;  name = "MediaMTX RTSP" }
    @{ port = 8889;  name = "MediaMTX WebRTC" }
    @{ port = 6379;  name = "Redis" }
    @{ port = 11434; name = "Ollama" }
)
foreach ($rule in $ports) {
    New-NetFirewallRule -DisplayName "Djinn — $($rule.name)" -Direction Inbound -Protocol TCP -LocalPort $rule.port -Action Allow -ErrorAction SilentlyContinue | Out-Null
    Write-OK "Port $($rule.port) open ($($rule.name))"
}

# =============================================================================
# 8. POWER — always on, no sleep
# =============================================================================
Write-Step "Configuring power (always on)..."
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /change monitor-timeout-ac 30
powercfg /SETACVALUEINDEX SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 d4e98f31-5ffe-4ce1-be31-1b38b384c009 0
Write-OK "Sleep disabled, network wake enabled"

# =============================================================================
# 9. HOSTNAME
# =============================================================================
Write-Step "Setting hostname to typhon..."
Rename-Computer -NewName "typhon" -Force -ErrorAction SilentlyContinue
Write-OK "Hostname set to typhon (takes effect after reboot)"

# =============================================================================
# DONE
# =============================================================================
Write-Host "`n"
Write-Host ("=" * 60) -ForegroundColor Magenta
Write-Host "  Typhon's Forge setup complete." -ForegroundColor Green
Write-Host "  REBOOT REQUIRED" -ForegroundColor Yellow
Write-Host ""
Write-Host "  After reboot:" -ForegroundColor White
Write-Host "    1. WSL2 Ubuntu will finish installing" -ForegroundColor White
Write-Host "    2. Open WSL2, run Djinn bootstrap:" -ForegroundColor White
Write-Host "       curl -sS https://raw.githubusercontent.com/DrManzo/djinn-vault/main/djinn/scripts/bootstrap-node.sh | bash" -ForegroundColor Yellow
Write-Host "    3. Add Salomon SSH key to:" -ForegroundColor White
Write-Host "       C:\ProgramData\ssh\administrators_authorized_keys" -ForegroundColor Yellow
Write-Host "    4. Open Tailscale and join the network" -ForegroundColor White
Write-Host "    5. Open OrcaSlicer and import Forge profiles from Z:\forge\slicer-profiles" -ForegroundColor White
Write-Host "    6. Verify Z: drive is mapped to The Library (Oroborus)" -ForegroundColor White
Write-Host ("=" * 60) -ForegroundColor Magenta
Write-Host ""

# Auto-reboot after 30 seconds — no terminal left open
Write-Host "  Rebooting in 30 seconds... (Ctrl+C to cancel)" -ForegroundColor Yellow
Start-Sleep -Seconds 30
Restart-Computer -Force
