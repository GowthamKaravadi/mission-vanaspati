# 🛠️ Manual Azure Deployment Guide

> **Full control over every step. Run each command yourself.**

This guide shows you how to deploy Mission Vanaspati to Azure **manually**, without using the automated script. This gives you complete control and understanding of each resource being created.

---

## 📋 Prerequisites

Before starting, ensure you have:
- [x] Azure CLI installed (`az --version`)
- [x] Azure account with credits ($69 remaining)
- [x] Project files ready locally

---

## 🔐 Step 1: Login to Azure

```powershell
# Login to your Azure account
az login

# Verify login successful
az account show --output table

# List available subscriptions
az account list --output table

# Set the correct subscription (if you have multiple)
az account set --subscription "Azure for Students"
```

**✅ Verify:** You should see your account details with subscription info.

---

## 📁 Step 2: Create Resource Group

A Resource Group is a container that holds all related Azure resources.

```powershell
# Set variables (customize these!)
$RESOURCE_GROUP = "mission-vanaspati-rg"
$LOCATION = "eastus"
$APP_NAME = "vanaspati-yourname"    # Must be globally unique!

# Create the resource group
az group create --name $RESOURCE_GROUP --location $LOCATION
```

**✅ Verify:**
```powershell
az group show --name $RESOURCE_GROUP --output table
```

---

## 🗄️ Step 3: Create PostgreSQL Database

### 3.1 Create the Database Server

```powershell
# Set database variables
$DB_SERVER_NAME = "$APP_NAME-db"
$DB_ADMIN_USER = "vanaspatiAdmin"
$DB_ADMIN_PASSWORD = "YourStrongPassword123!"    # Change this!
$DB_NAME = "vanaspati"

# Create PostgreSQL Flexible Server (takes 3-5 minutes)
az postgres flexible-server create `
    --resource-group $RESOURCE_GROUP `
    --name $DB_SERVER_NAME `
    --location $LOCATION `
    --admin-user $DB_ADMIN_USER `
    --admin-password $DB_ADMIN_PASSWORD `
    --sku-name Standard_B1ms `
    --tier Burstable `
    --storage-size 32 `
    --version 15 `
    --yes
```

**✅ Verify:**
```powershell
az postgres flexible-server show --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME --query "state"
```
Should output: `"Ready"`

### 3.2 Create the Database

```powershell
az postgres flexible-server db create `
    --resource-group $RESOURCE_GROUP `
    --server-name $DB_SERVER_NAME `
    --database-name $DB_NAME
```

**✅ Verify:**
```powershell
az postgres flexible-server db list --resource-group $RESOURCE_GROUP --server-name $DB_SERVER_NAME --output table
```

### 3.3 Configure Firewall Rules

```powershell
# Allow Azure services to connect
az postgres flexible-server firewall-rule create `
    --resource-group $RESOURCE_GROUP `
    --name $DB_SERVER_NAME `
    --rule-name "AllowAzureServices" `
    --start-ip-address 0.0.0.0 `
    --end-ip-address 0.0.0.0

# Allow your current IP (for testing)
$MY_IP = (Invoke-RestMethod -Uri "https://api.ipify.org")
az postgres flexible-server firewall-rule create `
    --resource-group $RESOURCE_GROUP `
    --name $DB_SERVER_NAME `
    --rule-name "AllowMyIP" `
    --start-ip-address $MY_IP `
    --end-ip-address $MY_IP
```

**✅ Verify:**
```powershell
az postgres flexible-server firewall-rule list --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME --output table
```

### 3.4 Get Connection String

```powershell
# Build the connection string
$DB_HOST = "$DB_SERVER_NAME.postgres.database.azure.com"
$DATABASE_URL = "postgresql://${DB_ADMIN_USER}:${DB_ADMIN_PASSWORD}@${DB_HOST}:5432/${DB_NAME}?sslmode=require"

# Display it (save this!)
Write-Host "DATABASE_URL: $DATABASE_URL"
```

📝 **Save this connection string!** You'll need it for the App Service.

---

## 📦 Step 4: Create Storage Account (for AI Model)

### 4.1 Create Storage Account

```powershell
# Storage account names must be lowercase, no hyphens, globally unique
$STORAGE_NAME = "vanaspati" + (Get-Random -Maximum 9999)

# Create storage account
az storage account create `
    --resource-group $RESOURCE_GROUP `
    --name $STORAGE_NAME `
    --location $LOCATION `
    --sku Standard_LRS `
    --kind StorageV2
```

**✅ Verify:**
```powershell
az storage account show --resource-group $RESOURCE_GROUP --name $STORAGE_NAME --query "provisioningState"
```
Should output: `"Succeeded"`

### 4.2 Create Container for Models

```powershell
# Get storage key
$STORAGE_KEY = (az storage account keys list --resource-group $RESOURCE_GROUP --account-name $STORAGE_NAME --query "[0].value" -o tsv)

# Create container
az storage container create `
    --account-name $STORAGE_NAME `
    --account-key $STORAGE_KEY `
    --name "models" `
    --public-access off
```

**✅ Verify:**
```powershell
az storage container list --account-name $STORAGE_NAME --account-key $STORAGE_KEY --output table
```

### 4.3 Upload Model Files

```powershell
# Navigate to project folder
cd "D:\Mission Vanaspati"

# Upload the PyTorch model (this takes 5-10 minutes for 500MB)
Write-Host "Uploading plant_classifier_final.pth (this may take a while)..."
az storage blob upload `
    --account-name $STORAGE_NAME `
    --account-key $STORAGE_KEY `
    --container-name "models" `
    --file "models/plant_classifier_final.pth" `
    --name "plant_classifier_final.pth" `
    --max-connections 4

# Upload class mapping
az storage blob upload `
    --account-name $STORAGE_NAME `
    --account-key $STORAGE_KEY `
    --container-name "models" `
    --file "models/class_mapping.json" `
    --name "class_mapping.json"
```

**✅ Verify:**
```powershell
az storage blob list --account-name $STORAGE_NAME --account-key $STORAGE_KEY --container-name "models" --output table
```

### 4.4 Generate SAS URL for Model Access

```powershell
# Generate SAS token (valid for 1 year)
$EXPIRY_DATE = (Get-Date).AddYears(1).ToString("yyyy-MM-ddTHH:mmZ")

$MODEL_SAS = az storage blob generate-sas `
    --account-name $STORAGE_NAME `
    --account-key $STORAGE_KEY `
    --container-name "models" `
    --name "plant_classifier_final.pth" `
    --permissions r `
    --expiry $EXPIRY_DATE `
    --output tsv

$MODEL_URL = "https://$STORAGE_NAME.blob.core.windows.net/models/plant_classifier_final.pth?$MODEL_SAS"

Write-Host "MODEL_URL: $MODEL_URL"
```

📝 **Save this MODEL_URL!** You'll need it for environment variables.

---

## 🚀 Step 5: Create App Service (Web Server)

### 5.1 Create App Service Plan

```powershell
$PLAN_NAME = "$APP_NAME-plan"

# Create Linux App Service Plan (B1 = Basic tier, ~$13/month)
az appservice plan create `
    --resource-group $RESOURCE_GROUP `
    --name $PLAN_NAME `
    --location $LOCATION `
    --sku B1 `
    --is-linux
```

**✅ Verify:**
```powershell
az appservice plan show --resource-group $RESOURCE_GROUP --name $PLAN_NAME --query "sku.name"
```
Should output: `"B1"`

### 5.2 Create Web App

```powershell
# Create the web app with Python 3.11
az webapp create `
    --resource-group $RESOURCE_GROUP `
    --plan $PLAN_NAME `
    --name $APP_NAME `
    --runtime "PYTHON:3.11"
```

**✅ Verify:**
```powershell
az webapp show --resource-group $RESOURCE_GROUP --name $APP_NAME --query "state"
```
Should output: `"Running"`

### 5.3 Configure Startup Command

```powershell
az webapp config set `
    --resource-group $RESOURCE_GROUP `
    --name $APP_NAME `
    --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker src.app:app --bind 0.0.0.0:8000"
```

---

## ⚙️ Step 6: Configure Environment Variables

```powershell
# Set all environment variables
az webapp config appsettings set `
    --resource-group $RESOURCE_GROUP `
    --name $APP_NAME `
    --settings `
        DATABASE_URL="$DATABASE_URL" `
        SECRET_KEY="$(New-Guid)" `
        ENVIRONMENT="production" `
        MODEL_PATH="/home/site/wwwroot/models/plant_classifier_final.pth" `
        CLASS_MAPPING_PATH="/home/site/wwwroot/models/class_mapping.json" `
        ALLOWED_ORIGINS="*" `
        PYTHONPATH="/home/site/wwwroot"
```

**✅ Verify:**
```powershell
az webapp config appsettings list --resource-group $RESOURCE_GROUP --name $APP_NAME --output table
```

---

## 📤 Step 7: Deploy Your Code

### 7.1 Create Deployment Package

```powershell
cd "D:\Mission Vanaspati"

# Create a ZIP file with all necessary files
$files = @(
    "src",
    "models",
    "remedies.json",
    "requirements-azure.txt",
    "config.py",
    "load_remedies.py",
    "init_db.py"
)

# Compress files
Compress-Archive -Path $files -DestinationPath "deploy.zip" -Force
```

### 7.2 Deploy via ZIP

```powershell
# Deploy the ZIP file
az webapp deploy `
    --resource-group $RESOURCE_GROUP `
    --name $APP_NAME `
    --src-path "deploy.zip" `
    --type zip
```

**Alternative: Deploy via Git (if you prefer)**
```powershell
# Configure local git deployment
az webapp deployment source config-local-git `
    --resource-group $RESOURCE_GROUP `
    --name $APP_NAME

# Get the deployment URL
$GIT_URL = az webapp deployment source config-local-git `
    --resource-group $RESOURCE_GROUP `
    --name $APP_NAME `
    --query url -o tsv

# Add as remote and push
git remote add azure $GIT_URL
git push azure main
```

**✅ Verify Deployment:**
```powershell
# Check deployment status
az webapp log deployment show --resource-group $RESOURCE_GROUP --name $APP_NAME

# View the app URL
Write-Host "Your app is live at: https://$APP_NAME.azurewebsites.net"
```

---

## 🔧 Step 8: Post-Deployment Configuration

### 8.1 Enable Logging

```powershell
az webapp log config `
    --resource-group $RESOURCE_GROUP `
    --name $APP_NAME `
    --docker-container-logging filesystem `
    --level verbose
```

### 8.2 Initialize Database

Open in browser:
```
https://YOUR-APP-NAME.azurewebsites.net/init-db
```

Or via curl:
```powershell
Invoke-RestMethod -Uri "https://$APP_NAME.azurewebsites.net/init-db"
```

**✅ Verify:** Should return `{"message": "Database initialized successfully"}`

### 8.3 Load Remedies Data

```powershell
# SSH into the app
az webapp ssh --resource-group $RESOURCE_GROUP --name $APP_NAME

# Inside SSH, run:
cd /home/site/wwwroot
python load_remedies.py
exit
```

---

## 🌐 Step 9: Deploy Frontend

### Option A: Vercel (Recommended - FREE)

1. Go to https://vercel.com
2. Sign up with GitHub
3. Import your repository
4. Configure:
   - Root Directory: `frontend-react`
   - Framework: `Vite`
   - Build Command: `npm run build`
   - Output: `dist`
5. Add Environment Variable:
   - `VITE_API_URL` = `https://YOUR-APP-NAME.azurewebsites.net`
6. Deploy!

### Option B: Azure Static Web Apps

```powershell
cd "D:\Mission Vanaspati\frontend-react"

# Install dependencies and build
npm install
npm run build

# Create Static Web App
az staticwebapp create `
    --resource-group $RESOURCE_GROUP `
    --name "$APP_NAME-frontend" `
    --source "dist" `
    --location "Central US" `
    --branch "main" `
    --app-location "/" `
    --output-location "dist"
```

---

## 🔒 Step 10: Update CORS

After frontend is deployed:

```powershell
$FRONTEND_URL = "https://your-frontend-url.vercel.app"  # Replace with actual URL

az webapp config appsettings set `
    --resource-group $RESOURCE_GROUP `
    --name $APP_NAME `
    --settings ALLOWED_ORIGINS="$FRONTEND_URL"

# Restart to apply changes
az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME
```

---

## ✅ Verification Checklist

Run these commands to verify everything is working:

```powershell
# 1. Check Resource Group
az group show --name $RESOURCE_GROUP --query "properties.provisioningState"
# Expected: "Succeeded"

# 2. Check Database
az postgres flexible-server show --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME --query "state"
# Expected: "Ready"

# 3. Check Storage Account
az storage account show --resource-group $RESOURCE_GROUP --name $STORAGE_NAME --query "provisioningState"
# Expected: "Succeeded"

# 4. Check App Service
az webapp show --resource-group $RESOURCE_GROUP --name $APP_NAME --query "state"
# Expected: "Running"

# 5. Test API Endpoint
Invoke-RestMethod -Uri "https://$APP_NAME.azurewebsites.net/"
# Expected: Health check response

# 6. Test Swagger Docs
Start-Process "https://$APP_NAME.azurewebsites.net/docs"
# Expected: Opens Swagger UI in browser
```

---

## 📊 View Your Resources

```powershell
# List all resources in your resource group
az resource list --resource-group $RESOURCE_GROUP --output table
```

Expected output:
| Name | Type |
|------|------|
| vanaspati-yourname | Microsoft.Web/sites |
| vanaspati-yourname-plan | Microsoft.Web/serverfarms |
| vanaspati-yourname-db | Microsoft.DBforPostgreSQL/flexibleServers |
| vanaspatiXXXX | Microsoft.Storage/storageAccounts |

---

## 🔍 Troubleshooting Commands

```powershell
# View real-time logs
az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME

# Download all logs
az webapp log download --resource-group $RESOURCE_GROUP --name $APP_NAME

# Restart the app
az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME

# Check environment variables
az webapp config appsettings list --resource-group $RESOURCE_GROUP --name $APP_NAME --output table

# SSH into the server
az webapp ssh --resource-group $RESOURCE_GROUP --name $APP_NAME

# Check deployment logs
az webapp log deployment show --resource-group $RESOURCE_GROUP --name $APP_NAME
```

---

## 💰 Cost Management

```powershell
# Stop services (SAVE MONEY!)
az webapp stop --resource-group $RESOURCE_GROUP --name $APP_NAME
az postgres flexible-server stop --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME

# Start services
az webapp start --resource-group $RESOURCE_GROUP --name $APP_NAME
az postgres flexible-server start --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME

# Check current status
az webapp show --resource-group $RESOURCE_GROUP --name $APP_NAME --query "state"
az postgres flexible-server show --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME --query "state"
```

---

## 🗑️ Cleanup (Delete Everything)

```powershell
# Delete entire resource group (removes all resources)
az group delete --name $RESOURCE_GROUP --yes --no-wait

# Verify deletion
az group list --output table
```

---

## 📝 Quick Reference: All Variables

Save these for future reference:

```powershell
# Resource Names
$RESOURCE_GROUP = "mission-vanaspati-rg"
$LOCATION = "eastus"
$APP_NAME = "vanaspati-yourname"
$PLAN_NAME = "$APP_NAME-plan"
$DB_SERVER_NAME = "$APP_NAME-db"
$DB_NAME = "vanaspati"
$STORAGE_NAME = "vanaspatiXXXX"

# Credentials (KEEP SECRET!)
$DB_ADMIN_USER = "vanaspatiAdmin"
$DB_ADMIN_PASSWORD = "YourStrongPassword123!"

# URLs
$BACKEND_URL = "https://$APP_NAME.azurewebsites.net"
$FRONTEND_URL = "https://your-app.vercel.app"
$DATABASE_URL = "postgresql://..."
```

---

## ⏱️ Time Estimate

| Step | Time |
|------|------|
| Login & Setup | 2 min |
| Create Resource Group | 1 min |
| Create PostgreSQL | 5 min |
| Create Storage & Upload Model | 10 min |
| Create App Service | 3 min |
| Configure & Deploy | 5 min |
| Post-Deployment Setup | 5 min |
| Frontend Deployment | 5 min |
| **Total** | **~35-40 min** |

---

**🎉 You now have complete control over your Azure deployment!**
