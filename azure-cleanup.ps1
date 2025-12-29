# Azure Resource Cleanup Script
# Use this to delete all resources and stop charges

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName = "mission-vanaspati-rg"
)

Write-Host "WARNING: This will delete ALL resources in $ResourceGroupName" -ForegroundColor Red
$confirm = Read-Host "Are you sure? (yes/no)"

if ($confirm -eq "yes") {
    Write-Host "`nDeleting resource group and all resources..." -ForegroundColor Yellow
    az group delete --name $ResourceGroupName --yes --no-wait
    Write-Host "Deletion initiated. This may take a few minutes to complete." -ForegroundColor Green
    Write-Host "You can check status with: az group show --name $ResourceGroupName" -ForegroundColor Cyan
} else {
    Write-Host "Cancelled." -ForegroundColor Yellow
}
