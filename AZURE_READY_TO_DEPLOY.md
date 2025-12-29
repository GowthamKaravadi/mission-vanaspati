# ☁️ Azure Deployment - Quick Start Guide

> **Everything ready! Choose your path and deploy in 10-15 minutes**

**Status:** ✅ All files ready | ✅ Username feature integrated | ✅ $69 budget optimized

---

## 📦 Available Deployment Files

### 1. **Automated Deployment Scripts**
- ✅ [`deploy-azure.ps1`](deploy-azure.ps1) - One-command PowerShell deployment
  - Creates all resources automatically
  - Sets up database, storage, app service
  - Configures environment variables
  - **Time: 10-15 minutes**

- ✅ [`azure-cleanup.ps1`](azure-cleanup.ps1) - Clean up resources when done
  - Removes all Azure resources
  - Prevents unnecessary charges

### 2. **Documentation Guides**
- ✅ [`AZURE_DEPLOYMENT_CHECKLIST.md`](AZURE_DEPLOYMENT_CHECKLIST.md) - **Start Here!**
  - Complete pre-deployment checklist
  - Testing procedures
  - Cost breakdown
  - Troubleshooting guide
  
- ✅ [`BEGINNER_DEPLOYMENT_GUIDE.md`](BEGINNER_DEPLOYMENT_GUIDE.md) - For Azure beginners
  - Step-by-step instructions with explanations
  - What is Azure? Simple explanations
  - Screenshots and examples
  - **Recommended for first-time deployers**
  
- ✅ [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) - Manual deployment
  - Detailed commands for each step
  - Advanced configuration options
  - For experienced users
  
- ✅ [`QUICKSTART.md`](QUICKSTART.md) - Quick commands
  - 3-command deployment
  - For those who know Azure

### 3. **Configuration Files**
- ✅ [`requirements-azure.txt`](requirements-azure.txt) - Python dependencies
  - FastAPI, PyTorch, SQLAlchemy, PostgreSQL
  - All dependencies verified compatible
  
- ✅ [`Procfile`](Procfile) - App startup command
  - Uvicorn server configuration
  
- ✅ [`.env.production`](.env.production) - Environment template
  - Database, secrets, API settings
  - Model paths, CORS configuration
  
- ✅ [`frontend-react/.env.production`](frontend-react/.env.production) - Frontend env
  - API URL configuration

### 4. **CI/CD Pipeline**
- ✅ [`.github/workflows/azure-static-web-apps.yml`](.github/workflows/azure-static-web-apps.yml)
  - Automatic frontend deployment on push
  - GitHub Actions integration

---

## 🎯 Deployment Paths (Choose One)

### **Path 1: Automated (RECOMMENDED)**
```powershell
# Install Azure CLI (one-time)
winget install Microsoft.AzureCLI

# Login
az login

# Deploy everything
.\deploy-azure.ps1 -ResourceGroupName "mission-vanaspati-rg" -Location "eastus" -AppName "your-unique-name"
```

**Pros:** 
- Fastest method (10-15 minutes)
- Fewer errors
- Automatic configuration

**Cons:**
- Less control over details

---

### **Path 2: Beginner Step-by-Step**
Follow: [`BEGINNER_DEPLOYMENT_GUIDE.md`](BEGINNER_DEPLOYMENT_GUIDE.md)

**Pros:**
- Learn what each step does
- Understand Azure services
- Easy to troubleshoot

**Cons:**
- Takes longer (30-45 minutes)

---

### **Path 3: Manual Expert**
Follow: [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md)

**Pros:**
- Full control
- Custom configurations
- Best for production

**Cons:**
- Most time-consuming (45-60 minutes)
- Requires Azure experience

---

## 💰 Azure Costs

| Service | SKU | Monthly Cost |
|---------|-----|--------------|
| **Backend** (App Service) | B1 Basic | $13.00 |
| **Database** (PostgreSQL) | B1ms Burstable | $12.00 |
| **Storage** (Model files) | Standard LRS | $0.50 |
| **Frontend** (Static Web App) | Free Tier | $0.00 |
| **TOTAL** | | **$25.50/month** |

**Your remaining Azure credits:** $69  
**Free hosting duration:** ~2.7 months (almost 3 months)

### 💡 Cost-Saving Options:
- **F1 Free Tier** (Backend): Saves $13/month but no custom domain/SSL
- **Stop when not in use**: Save ~60% by stopping overnight/weekends
- **B1ms Database** → Shared tier: Not recommended (too slow for ML model)

---

## ✅ Pre-Deployment Checklist

Before you start, verify:

### Local Environment
- [x] ✅ Backend running on localhost:8000
- [x] ✅ Frontend running successfully  
- [x] ✅ Database migrations completed (username feature)
- [x] ✅ Model file exists: `models/plant_classifier_final.pth`
- [x] ✅ Class mapping exists: `models/class_mapping.json`
- [ ] Test signup with username (recommended)
- [ ] Test login with username/email (recommended)
- [ ] Test disease prediction (recommended)

### Azure Prerequisites
- [ ] **Azure CLI installed** - Run: `az --version`
- [ ] **Azure account logged in** - Run: `az login`
- [ ] **Choose unique app name** - Example: `vanaspati-yourname`
- [ ] **Choose region** - Recommend: `eastus`, `westus2`, or `centralus`

---

## 🚀 Quick Start (5 Steps)

### Step 1: Install Azure CLI
```powershell
# Option A: Winget (Windows 10/11)
winget install Microsoft.AzureCLI

# Option B: Download installer
# Visit: https://aka.ms/installazurecliwindows
```

Restart PowerShell after installation.

### Step 2: Login to Azure
```powershell
az login
```

Your browser will open. Sign in with your Azure for Students account.

### Step 3: Verify Subscription
```powershell
# List subscriptions
az account list --output table

# Set active subscription (if needed)
az account set --subscription "Azure for Students"
```

### Step 4: Run Deployment Script
```powershell
# Navigate to project
cd "D:\Mission Vanaspati"

# Deploy (replace 'yourname' with something unique)
.\deploy-azure.ps1 `
    -ResourceGroupName "mission-vanaspati-rg" `
    -Location "eastus" `
    -AppName "vanaspati-yourname"
```

**What happens:**
1. Creates resource group
2. Sets up PostgreSQL database (prompts for password)
3. Creates storage account
4. Uploads model files (500MB - may take 5-10 minutes)
5. Creates App Service
6. Deploys backend code
7. Configures environment variables

### Step 5: Initialize Database
```bash
# Visit in browser (replace 'yourname'):
https://vanaspati-yourname.azurewebsites.net/init-db
```

Should show: `{"message": "Database initialized successfully"}`

---

## 📱 Post-Deployment Tasks

### 1. Create Admin User
```bash
# SSH into app
az webapp ssh --resource-group mission-vanaspati-rg --name vanaspati-yourname

# Create admin
python -c "
from src.database import SessionLocal, User
db = SessionLocal()
admin = User(
    username='admin',
    email='admin@yourdomain.com',
    hashed_password=User.hash_password('YourSecurePass123'),
    is_admin=True
)
db.add(admin)
db.commit()
print('Admin created!')
"
```

### 2. Load Remedies Data
```bash
# Option A: API endpoint
curl -X POST https://vanaspati-yourname.azurewebsites.net/load-remedies

# Option B: Via SSH
az webapp ssh --resource-group mission-vanaspati-rg --name vanaspati-yourname
python load_remedies.py
```

### 3. Deploy Frontend

#### Option A: GitHub Actions (Automatic)
1. Create Azure Static Web App in Azure Portal
2. Get deployment token
3. Add token to GitHub Secrets as `AZURE_STATIC_WEB_APPS_API_TOKEN`
4. Push code to GitHub
5. Automatic deployment!

#### Option B: Manual Build
```bash
cd frontend-react

# Update API URL
# Edit .env.production:
VITE_API_URL=https://vanaspati-yourname.azurewebsites.net

# Build
npm run build

# Deploy
az staticwebapp create \
    --name vanaspati-frontend \
    --resource-group mission-vanaspati-rg \
    --source dist \
    --location "Central US"
```

### 4. Update CORS
```bash
# Get frontend URL
$frontendUrl = "https://your-frontend.azurestaticapps.net"

# Update backend
az webapp config appsettings set \
    --resource-group mission-vanaspati-rg \
    --name vanaspati-yourname \
    --settings FRONTEND_URL=$frontendUrl ALLOWED_ORIGINS=$frontendUrl
```

---

## 🧪 Testing Your Deployment

### Backend Tests
```bash
# Health check
curl https://vanaspati-yourname.azurewebsites.net/docs

# Test signup
curl -X POST "https://vanaspati-yourname.azurewebsites.net/auth/signup?username=testuser&email=test@example.com&password=TestPass123"

# Test login
curl -X POST "https://vanaspati-yourname.azurewebsites.net/auth/login" \
  -F "username=testuser" \
  -F "password=TestPass123"
```

### Frontend Tests
- Visit frontend URL
- Create account with username
- Login with username
- Login with email (both should work!)
- Upload plant image
- Check disease library
- Submit feedback

---

## 📊 Monitoring

### View Logs
```bash
# Real-time logs
az webapp log tail --resource-group mission-vanaspati-rg --name vanaspati-yourname

# Download logs
az webapp log download --resource-group mission-vanaspati-rg --name vanaspati-yourname
```

### Check Status
```bash
az webapp show \
    --resource-group mission-vanaspati-rg \
    --name vanaspati-yourname \
    --query state
```

### View in Azure Portal
1. Go to: https://portal.azure.com
2. Navigate to: App Services → vanaspati-yourname
3. Check: Monitoring → Metrics

---

## 🔧 Troubleshooting

### Model Upload Fails
```bash
# Upload manually with Azure CLI
az storage blob upload \
    --account-name yourstorageaccount \
    --container-name models \
    --name plant_classifier_final.pth \
    --file models/plant_classifier_final.pth \
    --max-connections 4
```

### Database Connection Issues
```bash
# Allow Azure services
az postgres flexible-server firewall-rule create \
    --resource-group mission-vanaspati-rg \
    --name your-db-server \
    --rule-name AllowAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0
```

### App Won't Start
```bash
# Check logs
az webapp log tail --resource-group mission-vanaspati-rg --name vanaspati-yourname

# Restart app
az webapp restart --resource-group mission-vanaspati-rg --name vanaspati-yourname
```

For more issues, see: [`AZURE_DEPLOYMENT_CHECKLIST.md`](AZURE_DEPLOYMENT_CHECKLIST.md#-troubleshooting)

---

## 🗑️ Cleanup (When Done)

```bash
# Delete all resources
.\azure-cleanup.ps1 -ResourceGroupName "mission-vanaspati-rg"

# Or manually
az group delete --name mission-vanaspati-rg --yes --no-wait
```

---

## 📚 Documentation Quick Links

- **START HERE:** [`AZURE_DEPLOYMENT_CHECKLIST.md`](AZURE_DEPLOYMENT_CHECKLIST.md)
- **Beginner Guide:** [`BEGINNER_DEPLOYMENT_GUIDE.md`](BEGINNER_DEPLOYMENT_GUIDE.md)
- **Manual Guide:** [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md)
- **Quick Commands:** [`QUICKSTART.md`](QUICKSTART.md)
- **Username Feature:** [`USERNAME_FEATURE_SUMMARY.md`](USERNAME_FEATURE_SUMMARY.md)

---

## ✨ What's Included

### Backend Features
✅ FastAPI REST API  
✅ PyTorch disease classification (38 diseases, 50 classes)  
✅ User authentication (username + email)  
✅ Admin panel  
✅ Feedback system  
✅ Prediction history  
✅ Plant image validation  
✅ PostgreSQL database  

### Frontend Features
✅ React 19 with Vite  
✅ Dark/Light theme  
✅ Disease Library (searchable)  
✅ Single & batch prediction  
✅ Prediction history  
✅ Admin dashboard  
✅ Analytics & charts  
✅ Responsive design  

### New Username Feature
✅ Username field in signup  
✅ Login with username or email  
✅ Username display in UI  
✅ Database migration completed  
✅ Backward compatible  

---

## 🎉 Ready to Deploy!

You have **everything needed** for Azure deployment:
- ✅ 4 comprehensive guides
- ✅ Automated deployment script
- ✅ All configuration files
- ✅ CI/CD pipeline ready
- ✅ Username feature integrated
- ✅ Database migrations complete

**Recommended Next Step:**  
Open [`AZURE_DEPLOYMENT_CHECKLIST.md`](AZURE_DEPLOYMENT_CHECKLIST.md) and follow the checklist!

**Estimated Total Time:**
- Automated deployment: 15-20 minutes
- Manual first-time: 45-60 minutes

**Your Azure Credits:** $69 = ~2.7 months free hosting 🎁

**💰 Pro Tip:** Stop services when not in use to extend to 4-5 months!
```bash
az webapp stop --resource-group mission-vanaspati-rg --name your-app-name
az postgres flexible-server stop --resource-group mission-vanaspati-rg --name your-db
```

---

## 💡 Pro Tips

1. **Choose a unique app name** - Azure app names must be globally unique
2. **Pick a close region** - Use `eastus` or `westus2` for best performance
3. **Save your database password** - You'll need it later
4. **Test locally first** - Verify everything works before deploying
5. **Monitor costs** - Check Azure Cost Management regularly
6. **Use staging slots** - For testing before production (available in higher tiers)

---

## 🆘 Need Help?

1. ✅ Check logs: `az webapp log tail`
2. ✅ Review error messages in Azure Portal
3. ✅ Verify environment variables are set
4. ✅ Ensure model files uploaded successfully
5. ✅ Check database connection string
6. ✅ Review [`AZURE_DEPLOYMENT_CHECKLIST.md`](AZURE_DEPLOYMENT_CHECKLIST.md) troubleshooting section

Good luck with your deployment! 🚀🌿
