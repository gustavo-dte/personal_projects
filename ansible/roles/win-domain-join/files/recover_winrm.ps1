param(
  [string]$Username = $null,
  [string]$B64Password = $null,
  [bool]$ResetPassword = $false
)
# Use Continue — with Stop, native exe stderr creates ErrorRecord objects
# that PowerShell 5.1 treats as terminating errors.
$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'
$hostname = $env:COMPUTERNAME

Write-Output 'RECOVER_WINRM:START'

if ($ResetPassword) {
  if ([string]::IsNullOrEmpty($Username)) {
    Write-Output "PASSWORD_RESET:FAILED:MissingUsername"
    Write-Output ("HOSTNAME:" + $hostname)
    exit 1
  }
  if ([string]::IsNullOrEmpty($B64Password)) {
    Write-Output "PASSWORD_RESET:FAILED:MissingB64Password"
    Write-Output ("HOSTNAME:" + $hostname)
    exit 1
  }

  try {
    $password = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($B64Password))
  } catch {
    Write-Output ("B64_DECODE:FAILED:" + $_.Exception.Message)
    Write-Output ("HOSTNAME:" + $hostname)
    exit 1
  }

  # --- Create or reset local user ---
  $null = & net.exe user $Username 2>$null
  if ($LASTEXITCODE -ne 0) {
    # User does not exist — create it
    Write-Output "USER_EXISTS:FALSE"
    $null = & net.exe user $Username $password /add 2>$null
    if ($LASTEXITCODE -eq 0) {
      Write-Output "USER_CREATED:OK"
      $null = & net.exe localgroup Administrators $Username /add 2>$null
      if ($LASTEXITCODE -eq 0) { Write-Output "ADMIN_GROUP:ADDED" }
      else { Write-Output "ADMIN_GROUP:FAILED:rc=$LASTEXITCODE" }
    } else {
      Write-Output "USER_CREATED:FAILED:rc=$LASTEXITCODE"
    }
  } else {
    # User exists — reset password
    Write-Output "USER_EXISTS:TRUE"
    $null = & net.exe user $Username $password 2>$null
    if ($LASTEXITCODE -eq 0) { Write-Output "PASSWORD_RESET:OK" }
    else { Write-Output "PASSWORD_RESET:FAILED:rc=$LASTEXITCODE" }
  }

  # --- Activate account if disabled ---
  $null = & net.exe user $Username /active:yes 2>$null
} else {
  Write-Output "PASSWORD_RESET:SKIPPED"
}

# --- Allow remote admin for non-built-in-Administrator local accounts ---
try {
  Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' `
    -Name 'LocalAccountTokenFilterPolicy' -Value 1 -Type DWord -Force
  Write-Output "TOKEN_FILTER_POLICY:SET"
} catch {
  Write-Output ("TOKEN_FILTER_POLICY:FAILED:" + $_.Exception.Message)
}

# --- Disable firewall so WinRM is reachable ---
try {
  Set-NetFirewallProfile -Profile Public, Private -Enabled False
  Write-Output "FIREWALL:DISABLED"
} catch {
  Write-Output ("FIREWALL:FAILED:" + $_.Exception.Message)
}

# NOTE: Do NOT restart WinRM here. Azure Run Command uses the VM Guest Agent
# which communicates over a channel that can hang if WinRM restarts mid-execution.
# WinRM does not need a restart for the above changes to take effect.

Write-Output ("HOSTNAME:" + $hostname)
Write-Output 'RECOVER_WINRM:END'
