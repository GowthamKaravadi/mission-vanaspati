# Azure Deployment Script for Mission Vanaspati
# Prerequisites: Azure CLI installed and logged in (az login)

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName = "mission-vanaspati-rg",
    
    [Parameter(Mandatory=$true)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory=$true)]
    [string]$AppName = "mission-vanaspati"
)

Write-Host "=== Mission Vanaspati Azure Deployment ===" -ForegroundColor Green

# 1. Create Resource Group
Write-Host "`n[1/6] Creating Resource Group..." -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location

# 2. Create PostgreSQL Flexible Server
Write-Host "`n[2/6] Creating PostgreSQL Database..." -ForegroundColor Yellow
$dbServerName = "$AppName-db"
$dbAdminUser = "vanaspatiAdmin"
$dbAdminPassword = Read-Host "Enter PostgreSQL admin password" -AsSecureString
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
    --version 14 `
    --public-access 0.0.0.0

# Create database
Write-Host "Creating database..." -ForegroundColor Yellow
az postgres flexible-server db create `
    --resource-group $ResourceGroupName `
    --server-name $dbServerName `
    --database-name vanaspatidb

# 3. Create Storage Account for Model File
Write-Host "`n[3/6] Creating Storage Account for Model..." -ForegroundColor Yellow
$storageAccountName = ($AppName -replace '-','') + "storage"
az storage account create `
    --name $storageAccountName `
    --resource-group $ResourceGroupName `
    --location $Location `
    --sku Standard_LRS

# Get storage connection string
$storageConnectionString = az storage account show-connection-string `
    --name $storageAccountName `
    --resource-group $ResourceGroupName `
    --query connectionString `
    --output tsv

# Create blob container
az storage container create `
    --name models `
    --connection-string $storageConnectionString `
    --public-access blob

# Upload model file
Write-Host "Uploading model file..." -ForegroundColor Yellow
az storage blob upload `
    --container-name models `
    --name plant_classifier_final.pth `
    --file "models/plant_classifier_final.pth" `
    --connection-string $storageConnectionString

# Upload class mapping
az storage blob upload `
    --container-name models `
    --name class_mapping.json `
    --file "models/class_mapping.json" `
    --connection-string $storageConnectionString

# Get blob URLs
$modelUrl = "https://$storageAccountName.blob.core.windows.net/models/plant_classifier_final.pth"
$classMappingUrl = "https://$storageAccountName.blob.core.windows.net/models/class_mapping.json"

Write-Host "Model URL: $modelUrl" -ForegroundColor Cyan
Write-Host "Class Mapping URL: $classMappingUrl" -ForegroundColor Cyan

# 4. Create App Service Plan
Write-Host "`n[4/6] Creating App Service Plan..." -ForegroundColor Yellow
$appServicePlan = "$AppName-plan"
az appservice plan create `
    --name $appServicePlan `
    --resource-group $ResourceGroupName `
    --location $Location `
    --sku B1 `
    --is-linux

# 5. Create Web App
Write-Host "`n[5/6] Creating Web App..." -ForegroundColor Yellow
az webapp create `
    --resource-group $ResourceGroupName `
    --plan $appServicePlan `
    --name $AppName `
    --runtime "PYTHON:3.12"

# Configure startup command
az webapp config set `
    --resource-group $ResourceGroupName `
    --name $AppName `
    --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.fastapi_test:app"

# 6. Configure Environment Variables
Write-Host "`n[6/6] Configuring Environment Variables..." -ForegroundColor Yellow

# Generate secret key
$secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 50 | ForEach-Object {[char]$_})

# Database URL
$databaseUrl = "postgresql://${dbAdminUser}:${dbAdminPasswordPlain}@${dbServerName}.postgres.database.azure.com/vanaspatidb?sslmode=require"

# Frontend URL (will be set after Static Web App is created)
$frontendUrl = "https://$AppName.azurewebsites.net"

az webapp config appsettings set `
    --resource-group $ResourceGroupName `
    --name $AppName `
    --settings `
        DATABASE_URL=$databaseUrl `
        SECRET_KEY=$secretKey `
        ENVIRONMENT=production `
        API_HOST=0.0.0.0 `
        API_PORT=8000 `
        FRONTEND_URL=$frontendUrl `
        MODEL_PATH=$modelUrl `
        CLASS_MAPPING_PATH=$classMappingUrl `
        ALLOWED_ORIGINS=$frontendUrl

# Deploy code
Write-Host "`nDeploying application code..." -ForegroundColor Yellow
az webapp up `
    --resource-group $ResourceGroupName `
    --name $AppName `
    --runtime "PYTHON:3.12" `
    --sku B1 `
    --location $Location

Write-Host "`n=== Deployment Complete! ===" -ForegroundColor Green
Write-Host "`nBackend URL: https://$AppName.azurewebsites.net" -ForegroundColor Cyan
Write-Host "Database Server: $dbServerName.postgres.database.azure.com" -ForegroundColor Cyan
Write-Host "Model URL: $modelUrl" -ForegroundColor Cyan
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Update frontend API URL in frontend-react/src/services/api.js"
Write-Host "2. Deploy frontend using GitHub Actions (already configured)"
Write-Host "3. Update FRONTEND_URL in App Service settings after frontend deployment"
Write-Host "4. Initialize database by visiting: https://$AppName.azurewebsites.net/init-db"
