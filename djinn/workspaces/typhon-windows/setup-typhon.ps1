# =============================================================================
# Typhon — Windows Setup Script
# Djinn fleet node setup + debloat (keeps Microsoft Office)
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

Typhon — Windows Node Setup
Djinn Fleet Integration
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
        # Also remove provisioned so it doesn't reinstall for new users
        $prov = Get-AppxProvisionedPackage -Online | Where-Object DisplayName -eq $app
        if ($prov) {
            Remove-AppxProvisionedPackage -Online -PackageName $prov.PackageName -ErrorAction SilentlyContinue
        }
    }

    # Disable Cortana
    Write-Step "Disabling Cortana..."
    New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Force | Out-Null
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "AllowCortana" -Value 0 -Force
    Write-OK "Cortana disabled"

    # Disable telemetry
    Write-Step "Disabling telemetry..."
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Value 0 -Force -ErrorAction SilentlyContinue
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" -Name "AllowTelemetry" -Value 0 -Force -ErrorAction SilentlyContinue
    Write-OK "Telemetry disabled"

    # Disable OneDrive auto-start (keep installed in case needed)
    Write-Step "Disabling OneDrive auto-start..."
    New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\OneDrive" -Force | Out-Null
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\OneDrive" -Name "DisableFileSyncNGSC" -Value 1 -Force
    Write-OK "OneDrive auto-start disabled"

    # Disable Game Bar / DVR (GTX 1650 doesn't need it, wastes resources)
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\GameDVR" -Name "AllowGameDVR" -Value 0 -Force -ErrorAction SilentlyContinue
    Write-OK "Game DVR disabled"

    Write-OK "Bloat removal complete"
}

# =============================================================================
# 2. WINDOWS FEATURES — OpenSSH, Hyper-V, WSL
# =============================================================================
if (-not $SkipWSL) {
    Write-Step "Enabling Windows features..."

    # OpenSSH Server
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 -ErrorAction SilentlyContinue
    Start-Service sshd
    Set-Service -Name sshd -StartupType Automatic
    Write-OK "OpenSSH Server enabled and running"

    # WSL2
    Write-Step "Installing WSL2 with Ubuntu..."
    wsl --install -d Ubuntu --no-launch
    Write-OK "WSL2 Ubuntu queued (will complete after reboot)"

    # Hyper-V (needed for WSL2 full performance)
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All -NoRestart -ErrorAction SilentlyContinue
    Write-OK "Hyper-V enabled"
}

# =============================================================================
# 3. PACKAGE INSTALLS via winget
# =============================================================================
if (-not $SkipInstalls) {
    Write-Step "Installing packages via winget..."

    $packages = @(
        @{ id = "Git.Git";                    name = "Git" }
        @{ id = "Python.Python.3.12";         name = "Python 3.12" }
        @{ id = "Tailscale.Tailscale";        name = "Tailscale" }
        @{ id = "Ollama.Ollama";              name = "Ollama" }
        @{ id = "OBSProject.OBSStudio";       name = "OBS Studio" }
        @{ id = "Microsoft.WindowsTerminal";  name = "Windows Terminal" }
        @{ id = "Notepad++.Notepad++";        name = "Notepad++" }
        @{ id = "DEVCOM.JetBrainsMonoNerdFont"; name = "JetBrains Mono Nerd Font" }
        @{ id = "Rustlang.Rustup";            name = "Rust" }
        @{ id = "7zip.7zip";                  name = "7-Zip" }
    )

    foreach ($pkg in $packages) {
        Write-Host "    Installing $($pkg.name)..." -NoNewline
        winget install --id $pkg.id --silent --accept-package-agreements --accept-source-agreements 2>$null
        Write-OK " done"
    }

    # MediaMTX — download latest Windows binary
    Write-Step "Installing MediaMTX..."
    $mediamtxUrl = "https://github.com/bluenviron/mediamtx/releases/latest/download/mediamtx_windows_amd64.zip"
    $mediamtxDest = "$env:ProgramFiles\MediaMTX"
    New-Item -ItemType Directory -Force -Path $mediamtxDest | Out-Null
    Invoke-WebRequest -Uri $mediamtxUrl -OutFile "$env:TEMP\mediamtx.zip" -UseBasicParsing
    Expand-Archive -Path "$env:TEMP\mediamtx.zip" -DestinationPath $mediamtxDest -Force
    Write-OK "MediaMTX installed to $mediamtxDest"

    # Redis via WSL2 (runs in Ubuntu)
    Write-OK "Redis will run inside WSL2 Ubuntu — configured in post-WSL step"
}

# =============================================================================
# 4. SSH CONFIG — allow password auth + key auth for Djinn
# =============================================================================
Write-Step "Configuring OpenSSH..."
$sshdConfig = "C:\ProgramData\ssh\sshd_config"
if (Test-Path $sshdConfig) {
    (Get-Content $sshdConfig) -replace '#PasswordAuthentication yes', 'PasswordAuthentication yes' | Set-Content $sshdConfig
    (Get-Content $sshdConfig) -replace '#PubkeyAuthentication yes', 'PubkeyAuthentication yes' | Set-Content $sshdConfig
    Restart-Service sshd
    Write-OK "SSH configured"
}

# Add Salomon's public key to authorized_keys
$authorizedKeysPath = "$env:ProgramData\ssh\administrators_authorized_keys"
$salomonPubKey = "# Add Salomon's public key here after first boot"
Add-Content -Path $authorizedKeysPath -Value $salomonPubKey -ErrorAction SilentlyContinue
Write-Warn "Remember to add Salomon's SSH public key to $authorizedKeysPath"

# =============================================================================
# 5. FIREWALL — open ports Djinn needs
# =============================================================================
Write-Step "Opening firewall ports..."
$ports = @(
    @{ port = 22;   name = "SSH" }
    @{ port = 8080; name = "Typhon Studio Backend" }
    @{ port = 4455; name = "OBS WebSocket" }
    @{ port = 8554; name = "MediaMTX RTSP" }
    @{ port = 8889; name = "MediaMTX WebRTC" }
    @{ port = 6379; name = "Redis" }
    @{ port = 11434; name = "Ollama" }
)
foreach ($rule in $ports) {
    New-NetFirewallRule -DisplayName "Djinn — $($rule.name)" -Direction Inbound -Protocol TCP -LocalPort $rule.port -Action Allow -ErrorAction SilentlyContinue | Out-Null
    Write-OK "Port $($rule.port) open ($($rule.name))"
}

# =============================================================================
# 6. POWER — prevent sleep, keep network alive
# =============================================================================
Write-Step "Configuring power settings..."
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /change monitor-timeout-ac 30
# Keep network adapter active during sleep
powercfg /SETACVALUEINDEX SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 d4e98f31-5ffe-4ce1-be31-1b38b384c009 0
Write-OK "Sleep disabled, network wake enabled"

# =============================================================================
# 7. HOSTNAME
# =============================================================================
Write-Step "Setting hostname to typhon..."
Rename-Computer -NewName "typhon" -Force -ErrorAction SilentlyContinue
Write-OK "Hostname set to typhon (takes effect after reboot)"

# =============================================================================
# DONE
# =============================================================================
Write-Host "`n" + ("=" * 60) -ForegroundColor Magenta
Write-Host "  Setup complete. REBOOT REQUIRED." -ForegroundColor Green
Write-Host "  After reboot:" -ForegroundColor White
Write-Host "    1. WSL2 Ubuntu will finish installing" -ForegroundColor White
Write-Host "    2. Open WSL2 and run the Djinn bootstrap:" -ForegroundColor White
Write-Host "       curl -sS https://raw.githubusercontent.com/DrManzo/djinn-vault/main/djinn/scripts/bootstrap-node.sh | bash" -ForegroundColor Yellow
Write-Host "    3. Add Salomon public key to:" -ForegroundColor White
Write-Host "       C:\ProgramData\ssh\administrators_authorized_keys" -ForegroundColor Yellow
Write-Host "    4. Run Tailscale and join the network" -ForegroundColor White
Write-Host ("=" * 60) -ForegroundColor Magenta

$reboot = Read-Host "`nReboot now? (y/n)"
if ($reboot -eq 'y') { Restart-Computer -Force }
