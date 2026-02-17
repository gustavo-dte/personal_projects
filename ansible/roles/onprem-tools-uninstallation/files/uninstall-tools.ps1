<# What this script does each product:
Detects if the software is installed
Stops any related Windows services (if running)
Forcefully uninstalls the software
Prints a single status line per package (GitHub Actions friendly)
powershell -File ../../ansible-uninstall/roles/onprem-tools-uninstall/files/uninstall-tools.ps1 #>

$ErrorActionPreference = "SilentlyContinue"

# Track if any software was uninstalled to determine if reboot is needed
$rebootNeeded = $false

# Function to check Add or Remove Programs for specific software
function Check-AddRemovePrograms {
    Write-Host "Checking Add or Remove Programs for installed software: Puppet Agent, EMC PowerPath, VMware Tools, HP Insight Management Agent, EMC Avamar for Windows"
    $apps = @("Puppet Agent", "EMC PowerPath", "VMware Tools", "HP Insight", "EMC Avamar for Windows")
    foreach ($appName in $apps) {
        $app = Get-InstalledApp $appName
        if ($app) {
            Write-Host "$appName : FOUND"
        } else {
            Write-Host "$appName : NOT FOUND"
        }
    }
}

# Run the check for Add or Remove Programs
Check-AddRemovePrograms

# Actions log prefix (optional but nice)
function Write-Status {
    param (
        [string]$Name,
        [string]$Status
    )
    Write-Output "$Name : $Status"
}

# Stop related services safely
function Stop-Services {
    param (
        [string[]]$ServiceNames
    )

    foreach ($svc in $ServiceNames) {
        Write-Verbose "Checking service: $svc"
        $service = Get-Service -Name $svc -ErrorAction SilentlyContinue
        if ($service -and $service.Status -ne "Stopped") {
            Write-Verbose "Stopping service: $svc"
            Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue
            $service.WaitForStatus("Stopped","00:00:30")
            Write-Verbose "Service $svc stopped"
        } else {
            Write-Verbose "Service $svc not running or not found"
        }
    }
}

# Find installed software via registry
function Get-InstalledApp {
    param (
        [string]$DisplayName
    )

    Write-Host "Searching for installed app: $DisplayName"
    $paths = @(
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )

    foreach ($path in $paths) {
        Write-Host "Checking registry path: $path"
        $app = Get-ItemProperty $path | Where-Object {
            $_.DisplayName -like "*$DisplayName*"
        }
        if ($app) {
            Write-Host "Found app: $($app.DisplayName)"
            return $app
        }
    }
    Write-Host "App not found: $DisplayName"
    return $null
}

# Uninstall via MSI or UninstallString
function Uninstall-App {
    param (
        [object]$App
    )

    Write-Verbose "Uninstalling app: $($App.DisplayName)"
    if ($App.UninstallString -match "msiexec") {
        $uninstallString = $App.UninstallString
        # CRITICAL FIX: Correct MSI command from /I (install) to /X (uninstall) if present
        if ($uninstallString -match "MsiExec\.exe /I\{([^\}]+)\}") {
            $guid = $matches[1]
            $uninstallString = "MsiExec.exe /X{$guid} /qn /norestart"
            Write-Verbose "Corrected MSI command from /I to /X for GUID: $guid"
        } else {
            $guid = ($uninstallString -replace ".*\{","{" -replace "\}.*","}")
            Write-Verbose "Using msiexec to uninstall GUID: $guid"
        }
        Start-Process "msiexec.exe" -ArgumentList ($uninstallString -replace "MsiExec\.exe ", "") -Wait
    } else {
        Write-Verbose "Using uninstall string: $($App.UninstallString)"
        Start-Process "cmd.exe" -ArgumentList "/c $($App.UninstallString) /quiet /norestart" -Wait
    }
    Write-Verbose "Uninstall process completed for $($App.DisplayName)"
}

# ================================
# Puppet Agent
# ================================
$app = Get-InstalledApp "Puppet Agent"
if ($app) {
    Stop-Services @("puppet")
    Uninstall-App $app
    Write-Status "Puppet Agent" "UNINSTALLED"
    $script:rebootNeeded = $true
} else {
    Write-Status "Puppet Agent" "NOT FOUND"
}

# ================================
# EMC PowerPath
# ================================
$app = Get-InstalledApp "EMC PowerPath"
if ($app) {
    Stop-Services @("PowerPath")
    Uninstall-App $app
    Write-Status "EMC PowerPath" "UNINSTALLED"
    $script:rebootNeeded = $true
} else {
    Write-Status "EMC PowerPath" "NOT FOUND"
}

# ================================
# VMware Tools
# ================================
$app = Get-InstalledApp "VMware Tools"
if ($app) {
    Stop-Services @(
        "VMTools",
        "VMware Physical Disk Helper Service",
        "VMware Snapshot Provider",
        "VMware Tools Service"
    )
    Uninstall-App $app
    Write-Status "VMware Tools" "UNINSTALLED"
    $script:rebootNeeded = $true
} else {
    Write-Status "VMware Tools" "NOT FOUND"
}

# ================================
# HP Insight Management Agent
# ================================
$app = Get-InstalledApp "HP Insight"
if ($app) {
    Stop-Services @(
        "HP Insight Management Agents",
        "HP Insight Foundation Agents"
    )
    Uninstall-App $app
    Write-Status "HP Insight Management Agent" "UNINSTALLED"
    $script:rebootNeeded = $true
} else {
    Write-Status "HP Insight Management Agent" "NOT FOUND"
}

# ================================
# EMC Avamar for Windows
# ================================
$app = Get-InstalledApp "EMC Avamar for Windows"
if ($app) {
    Stop-Services @("avagent")
    Uninstall-App $app
    Write-Status "EMC Avamar for Windows" "UNINSTALLED"
    $script:rebootNeeded = $true
} else {
    Write-Status "EMC Avamar for Windows" "NOT FOUND"
}

# ================================
# Reboot the server only if any tools were uninstalled
# ================================
if ($rebootNeeded) {
    Write-Host "Rebooting the server to complete the uninstallation process..."
    Restart-Computer -Force
} else {
    Write-Host "No tools were found or uninstalled. Skipping reboot."
}
