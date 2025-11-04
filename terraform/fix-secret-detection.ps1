# Fix Secret Detection Issues in terraform-docs.yml
# This script adds pragma comments to exclude false positive secret detections

$ErrorActionPreference = "Stop"

Write-Host "Fixing secret detection issues..." -ForegroundColor Cyan

# File path
$file = "D:\DevOps\DTE\vmware\source_code\cloud-platform-vm-migration\terraform\azure_sql\terraform-docs.yml"

if (-not (Test-Path $file)) {
    Write-Host "ERROR: File not found: $file" -ForegroundColor Red
    exit 1
}

Write-Host "Reading file: $file" -ForegroundColor Yellow

# Read content
$content = Get-Content $file -Raw

# Backup original
$backup = "$file.backup"
Copy-Item $file $backup
Write-Host "Backup created: $backup" -ForegroundColor Green

# Replace all occurrences of admin_login_secret without pragma comment
$pattern = 'admin_login_secret\s+=\s+var\.sql_admin_credentials(?!\s+#\s+pragma)'
$replacement = 'admin_login_secret     = var.sql_admin_credentials  # pragma: allowlist secret'

$newContent = $content -replace $pattern, $replacement

# Write back
Set-Content -Path $file -Value $newContent -NoNewline

Write-Host "`nChanges applied successfully!" -ForegroundColor Green
Write-Host "`nVerifying changes..." -ForegroundColor Yellow

# Count occurrences
$count = ([regex]::Matches($newContent, 'pragma: allowlist secret')).Count
Write-Host "Found $count pragma comments in the file" -ForegroundColor Cyan

if ($count -ge 2) {
    Write-Host "`n✅ SUCCESS: Both occurrences have been updated!" -ForegroundColor Green
    Write-Host "`nYou can now run: git add . && pre-commit run detect-secrets --all-files" -ForegroundColor Cyan
} else {
    Write-Host "`n⚠️  WARNING: Expected at least 2 occurrences, found $count" -ForegroundColor Yellow
    Write-Host "Please verify the changes manually" -ForegroundColor Yellow
}

Write-Host "`nOriginal file backed up to: $backup" -ForegroundColor Gray
