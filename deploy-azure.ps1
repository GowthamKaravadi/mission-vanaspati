# Azure Deployment Script for Mission Vanaspati
# Prerequisites: Azure CLI installed and logged in (az login)
# 
# SIMPLIFIED VERSION: Model bundled with code (no blob storage needed)
# This saves ~10 minutes deployment time and $0.50/month

param(
    [string]$ResourceGroupName = "mission-vanaspati-rg",
    [string]$Location = "eastus",
    [Parameter(Mandatory=$true)]
    [string]$AppName
)

Write-Host "=== Mission Vanaspati Azure Deployment ===" -ForegroundColor Green
Write-Host "App Name: $AppName" -ForegroundColor Cyan
Write-Host "Location: $Location" -ForegroundColor Cyan

# Verify model files exist
if (-not (Test-Path "models/plant_classifier_final.pth")) {
    Write-Host "ERROR: Model file not found at models/plant_classifier_final.pth" -ForegroundColor Red
    exit 1
}
Write-Host "Model file verified (will be bundled with code)" -ForegroundColor Green

# 1. Create Resource Group
Write-Host "`n[1/4] Creating Resource Group..." -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location

# 2. Create PostgreSQL Flexible Server
Write-Host "`n[2/4] Creating PostgreSQL Database (takes 3-5 minutes)..." -ForegroundColor Yellow
$dbServerName = "$AppName-db"
$dbAdminUser = "vanaspatiAdmin"
$dbAdminPassword = Read-Host "Enter PostgreSQL admin password (min 8 chars, include uppercase, lowercase, number)" -AsSecureString
$dbAdminPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbAdminPassword))

az postgres flexible-server create `
    --resource-group $ResourceGroupName `
    --name $dbServerName `
    --location $Location `
    --admin-user $dbAdminUser `
    --admin-password $dbAdminPasswordPlain `
    --sku-name Standard_B1ms `
    --tier Burstable `
    --storage-size 32 `
    --version 15 `
    --public-access 0.0.0.0 `
    --yes

# Create database
Write-Host "Creating database..." -ForegroundColor Yellow
az postgres flexible-server db create `
    --resource-group $ResourceGroupName `
    --server-name $dbServerName `
    --database-name vanaspatidb

# 3. Create App Service Plan
Write-Host "`n[3/4] Creating App Service Plan..." -ForegroundColor Yellow
$appServicePlan = "$AppName-plan"
az appservice plan create `
    --name $appServicePlan `
    --resource-group $ResourceGroupName `
    --location $Location `
    --sku B1 `
    --is-linux

# 4. Create Web App & Deploy Code
Write-Host "`n[4/4] Creating Web App and Deploying Code..." -ForegroundColor Yellow
az webapp create `
    --resource-group $ResourceGroupName `
    --plan $appServicePlan `
    --name $AppName `
    --runtime "PYTHON:3.11"

# Configure startup command
az webapp config set `
    --resource-group $ResourceGroupName `
    --name $AppName `
    --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker src.app:app --bind 0.0.0.0:8000"

# Configure Environment Variables
Write-Host "Configuring environment variables..." -ForegroundColor Yellow

# Generate secret key
$secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 50 | ForEach-Object {[char]$_})

# Database URL
$databaseUrl = "postgresql://${dbAdminUser}:${dbAdminPasswordPlain}@${dbServerName}.postgres.database.azure.com/vanaspatidb?sslmode=require"

az webapp config appsettings set `
    --resource-group $ResourceGroupName `
    --name $AppName `
    --settings `
        DATABASE_URL="$databaseUrl" `
        SECRET_KEY="$secretKey" `
        ENVIRONMENT="production" `
        MODEL_PATH="/home/site/wwwroot/models/plant_classifier_final.pth" `
        CLASS_MAPPING_PATH="/home/site/wwwroot/models/class_mapping.json" `
        ALLOWED_ORIGINS="*" `
        PYTHONPATH="/home/site/wwwroot"

# Deploy code (model bundled with code)
Write-Host "`nDeploying application code (includes model files)..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes due to model file size..." -ForegroundColor Cyan

az webapp up `
    --resource-group $ResourceGroupName `
    --name $AppName `
    --runtime "PYTHON:3.11" `
    --sku B1

Write-Host "`n=== Deployment Complete! ===" -ForegroundColor Green
Write-Host "`nBackend URL: https://$AppName.azurewebsites.net" -ForegroundColor Cyan
Write-Host "Database Server: $dbServerName.postgres.database.azure.com" -ForegroundColor Cyan
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Initialize database: https://$AppName.azurewebsites.net/init-db"
Write-Host "2. Deploy frontend to Vercel (free) with VITE_API_URL=https://$AppName.azurewebsites.net"
Write-Host "3. Update ALLOWED_ORIGINS with your frontend URL:"
Write-Host "   az webapp config appsettings set --resource-group $ResourceGroupName --name $AppName --settings ALLOWED_ORIGINS='https://your-frontend.vercel.app'"
Write-Host "`nCost Saving Tip: Stop services when not using!" -ForegroundColor Magenta
Write-Host "   az webapp stop --resource-group $ResourceGroupName --name $AppName"
Write-Host "   az postgres flexible-server stop --resource-group $ResourceGroupName --name $dbServerName"
