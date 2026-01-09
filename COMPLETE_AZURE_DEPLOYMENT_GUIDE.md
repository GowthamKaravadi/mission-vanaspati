# ☁️ Mission Vanaspati - Complete Azure Deployment Guide

> **The ONLY guide you need! Step-by-step with zero Azure knowledge required.**

---

## 📋 Table of Contents

1. [What is Azure?](#-what-is-azure-simple-explanation)
2. [Cost Overview](#-cost-overview)
3. [Pre-Deployment Checklist](#-pre-deployment-checklist)
4. [Step-by-Step Deployment](#-step-by-step-deployment)
5. [Frontend Deployment](#-frontend-deployment)
6. [Post-Deployment Setup](#-post-deployment-setup)
7. [Testing Your Deployment](#-testing-your-deployment)
8. [Budget Management & Cost Saving](#-budget-management--cost-saving)
9. [Common Issues & Fixes](#-common-issues--fixes)
10. [Quick Reference Commands](#-quick-reference-commands)
11. [Cleanup](#-cleanup-when-done)

---

## 📦 What is Azure? (Simple Explanation)

**Azure** = Microsoft's cloud service. Think of it as renting computers on the internet that run 24/7.

### What we'll create:

| Service | What It Does | Real-World Analogy | Cost |
|---------|--------------|-------------------|------|
| **App Service** | Runs your Python backend + AI model | Renting a computer online | $13/month |
| **PostgreSQL Database** | Stores users, feedback, history | Like Excel, but powerful | $12/month |
| **Static Web App** | Hosts your React website | Website hosting | **FREE** |

**💰 Total: $25/month** (Your $69 credits = ~2.7 months free)

> **Note:** Model files are bundled with your code (no separate storage needed!)

---

## 💰 Cost Overview

### Your Budget
| Detail | Value |
|--------|-------|
| **Available Credits** | $69 |
| **Monthly Cost (24/7)** | $25 |
| **Duration (always-on)** | ~2.7 months |

### 💡 Smart Strategy: Extend to 5+ Months!

| Usage Pattern | Monthly Cost | Your Credits Last |
|--------------|--------------|-------------------|
| Always-On (24/7) | $25.50 | 2.7 months |
| Stop Nights (12h/day) | ~$13 | **5+ months** |
| Stop Nights + Weekends | ~$8 | **8+ months** |
| Only for Demos | ~$1-2/session | **35+ sessions** |

**🎯 Recommendation:** Stop services when not using them!

---

## ✅ Pre-Deployment Checklist

Before starting, verify these on your local machine:

### Required Files (Already in your project ✅)
- [x] `src/app.py` - Backend API
- [x] `models/plant_classifier_final.pth` - AI Model (~500MB)
- [x] `models/class_mapping.json` - Class names
- [x] `remedies.json` - Disease treatments
- [x] `requirements-azure.txt` - Python dependencies
- [x] `Procfile` - App startup command
- [x] `deploy-azure.ps1` - Automated deployment script
- [x] `azure-cleanup.ps1` - Cleanup script

### Local Testing (Recommended)
- [ ] Backend running on http://localhost:8000
- [ ] Can upload and predict plant disease
- [ ] Login/Signup working

---

## 🚀 Step-by-Step Deployment

### **STEP 1: Install Azure CLI** ⏱️ 5 minutes

> **What is CLI?** = Command Line Interface. A way to control Azure using text commands.

**Option A: Using Windows Package Manager (Recommended)**
```powershell
winget install Microsoft.AzureCLI
```

**Option B: Download Installer**
1. Go to: https://aka.ms/installazurecliwindows
2. Download the MSI file
3. Run installer, click Next until done

**⚠️ IMPORTANT: Restart PowerShell after installation!**

**Verify Installation:**
```powershell
az --version
```
You should see version info like `azure-cli 2.x.x`

---

### **STEP 2: Login to Azure** ⏱️ 2 minutes

Open PowerShell and run:
```powershell
az login
```

**What happens:**
1. Browser opens automatically
2. Sign in with your Azure for Students account (the one with $69 credits)
3. Browser shows "You're logged in"
4. Close the browser tab
5. PowerShell shows your account info

**Verify your subscription:**
```powershell
az account list --output table
```

You should see "Azure for Students" in the list.

---

### **STEP 3: Choose Your Unique App Name** ⏱️ 1 minute

Your app needs a **globally unique** name (like choosing a username).

**Rules:**
- Only letters, numbers, and hyphens (-)
- No spaces or special characters
- Must be unique worldwide

**Examples:**
- `vanaspati-yourname`
- `plant-disease-2025`
- `mission-vanaspati-john`

📝 **Write your chosen name here:** `____________________`

---

### **STEP 4: Run the Deployment Script** ⏱️ 10-15 minutes

Navigate to your project folder and run the script:

```powershell
cd "D:\Mission Vanaspati"
.\deploy-azure.ps1 -AppName "YOUR-CHOSEN-NAME"
```

**Example:**
```powershell
cd "D:\Mission Vanaspati"
.\deploy-azure.ps1 -AppName "vanaspati-john"
```

### What Happens During Deployment:

| Step | What It Does | Time |
|------|--------------|------|
| 1/6 | Creates Resource Group (folder for all resources) | 30 sec |
| 2/6 | Creates PostgreSQL Database | 3-5 min |
| 3/6 | Creates Storage & Uploads AI Model | 5-10 min |
| 4/6 | Creates App Service (web server) | 2-3 min |
| 5/6 | Deploys your Python code | 2-3 min |
| 6/6 | Sets environment variables | 30 sec |

**⚠️ During Step 2, you'll be asked to create a database password:**
- Enter a strong password (e.g., `MyPlant2024!Pass`)
- **📝 WRITE THIS PASSWORD DOWN!** You'll need it later.

### When Complete, You'll See:
```
=== Deployment Complete! ===

Backend URL: https://vanaspati-john.azurewebsites.net
```

🎉 **Copy this URL!** This is your live backend.

---

### **STEP 5: Test Your Backend** ⏱️ 2 minutes

Open your browser and visit:
```
https://YOUR-APP-NAME.azurewebsites.net/docs
```

**Example:** `https://vanaspati-john.azurewebsites.net/docs`

You should see a Swagger API documentation page. This means your backend is live! 🎉

---

### **STEP 6: Initialize the Database** ⏱️ 1 minute

Visit this URL in your browser:
```
https://YOUR-APP-NAME.azurewebsites.net/init-db
```

You should see:
```json
{"message": "Database initialized successfully"}
```

This creates all the database tables (users, remedies, feedback, etc.)

---

## 🌐 Frontend Deployment

Your React frontend needs to be deployed separately.

### **Option A: Deploy to Vercel (RECOMMENDED - FREE Forever)**

1. **Go to:** https://vercel.com
2. Click **"Sign up"** with GitHub
3. Click **"Add New Project"**
4. Import your repository (or upload manually)
5. **Configure the project:**

| Setting | Value |
|---------|-------|
| Framework Preset | `Vite` |
| Root Directory | `frontend-react` |
| Build Command | `npm run build` |
| Output Directory | `dist` |

6. **Add Environment Variable:**
   - Click "Environment Variables"
   - Name: `VITE_API_URL`
   - Value: `https://YOUR-APP-NAME.azurewebsites.net` (your backend URL)

7. Click **"Deploy"**

**⏱️ Done in 2-3 minutes!** 

Vercel gives you a URL like: `https://your-app.vercel.app`

📝 **Write your frontend URL here:** `____________________`

---

### **Option B: Azure Static Web Apps (Uses your credits)**

```powershell
cd "D:\Mission Vanaspati\frontend-react"

# Build the frontend
npm run build

# Create Static Web App
az staticwebapp create `
    --name vanaspati-frontend `
    --resource-group mission-vanaspati-rg `
    --source dist `
    --location "Central US"
```

---

## ⚙️ Post-Deployment Setup

### **STEP 7: Update CORS Settings** ⏱️ 1 minute

> **What is CORS?** = Security setting that allows your frontend to talk to your backend.

Run this command (replace with your actual URLs):

```powershell
az webapp config appsettings set `
    --resource-group mission-vanaspati-rg `
    --name YOUR-APP-NAME `
    --settings ALLOWED_ORIGINS="https://your-app.vercel.app"
```

**Example:**
```powershell
az webapp config appsettings set `
    --resource-group mission-vanaspati-rg `
    --name vanaspati-john `
    --settings ALLOWED_ORIGINS="https://vanaspati-john.vercel.app"
```

---

### **STEP 8: Load Remedies Data** ⏱️ 2 minutes

SSH into your backend server:
```powershell
az webapp ssh --resource-group mission-vanaspati-rg --name YOUR-APP-NAME
```

Once connected (you'll see a Linux terminal), run:
```bash
cd /home/site/wwwroot
python load_remedies.py
```

Type `exit` to leave SSH.

---

### **STEP 9: Create Admin Account** ⏱️ 3 minutes

1. Visit your frontend URL
2. Click **Sign Up** and create an account
3. Now make yourself admin:

**Option A: Using Azure Portal**
1. Go to https://portal.azure.com
2. Search for "PostgreSQL flexible servers"
3. Click your database
4. Go to **Databases** in left menu
5. Use **Query Editor** or connect with a tool
6. Run this SQL:
```sql
UPDATE users SET role = 'admin' WHERE email = 'your-email@example.com';
```

**Option B: Using SSH**
```powershell
az webapp ssh --resource-group mission-vanaspati-rg --name YOUR-APP-NAME
```

Then run:
```python
python -c "
from src.database import SessionLocal, User
db = SessionLocal()
user = db.query(User).filter(User.email == 'your-email@example.com').first()
if user:
    user.role = 'admin'
    db.commit()
    print('Admin access granted!')
"
```

---

## 🧪 Testing Your Deployment

### Quick Test Checklist:

| Test | How to Verify |
|------|---------------|
| Backend Running | Visit `https://YOUR-APP-NAME.azurewebsites.net/docs` |
| Database Connected | Visit `https://YOUR-APP-NAME.azurewebsites.net/init-db` |
| Frontend Running | Visit your Vercel/Azure Static URL |
| Sign Up Works | Create a new account |
| Login Works | Login with username or email |
| Prediction Works | Upload a plant image |
| Remedies Load | Check if treatments appear |
| Admin Panel | Login and click Admin (if admin) |

### API Testing (Optional):
```powershell
# Test health
curl https://YOUR-APP-NAME.azurewebsites.net/

# Test signup
curl -X POST "https://YOUR-APP-NAME.azurewebsites.net/auth/signup?username=testuser&email=test@test.com&password=Test123!"
```

---

## 💰 Budget Management & Cost Saving

### ⭐ IMPORTANT: Stop Services When Not Using!

**Stop All Services (Save Money):**
```powershell
# Stop backend
az webapp stop --resource-group mission-vanaspati-rg --name YOUR-APP-NAME

# Stop database
az postgres flexible-server stop --resource-group mission-vanaspati-rg --name YOUR-APP-NAME-db
```

**Start All Services (When Needed):**
```powershell
# Start backend
az webapp start --resource-group mission-vanaspati-rg --name YOUR-APP-NAME

# Start database
az postgres flexible-server start --resource-group mission-vanaspati-rg --name YOUR-APP-NAME-db

# Wait 2-3 minutes for services to fully start
```

### Cost Saving Strategies:

| Strategy | Savings | How Long Credits Last |
|----------|---------|----------------------|
| Stop at night (8PM-8AM) | 50% | **5+ months** |
| Stop nights + weekends | 60-70% | **8+ months** |
| Only run for demos | 80-90% | **35+ demo sessions** |

### Set Up Budget Alerts:
1. Go to https://portal.azure.com
2. Search for "Cost Management"
3. Click "Budgets" → "Add"
4. Set alerts at $50, $60, $65

### Check Your Spending:
```powershell
# Check in portal
# https://portal.azure.com → Cost Management → Cost Analysis
```

### 📱 Mobile Tip:
Download **Azure Mobile App** (iOS/Android) to start/stop services from your phone!

---

## 🔧 Common Issues & Fixes

### ❌ "az: command not found"
**Fix:** Restart PowerShell or your computer after installing Azure CLI.

### ❌ "Name already taken"
**Fix:** Choose a different app name. Names must be globally unique.

### ❌ "Database connection failed"
**Fix:** 
1. Verify you entered the correct password
2. Visit `/init-db` endpoint again
3. Check database firewall allows Azure services

### ❌ "CORS error" in browser
**Fix:** Make sure you ran the CORS settings command with your correct frontend URL.

### ❌ "Model not found" error
**Fix:** 
1. Check `models/plant_classifier_final.pth` exists locally
2. Re-run deployment script to re-upload

### ❌ Frontend shows "Network Error"
**Fix:**
1. Check backend URL in Vercel environment variables
2. Verify backend is running: visit `/docs` endpoint
3. Check CORS is configured correctly

### ❌ App won't start or crashes
**Fix:**
```powershell
# View logs to see the error
az webapp log tail --resource-group mission-vanaspati-rg --name YOUR-APP-NAME

# Restart the app
az webapp restart --resource-group mission-vanaspati-rg --name YOUR-APP-NAME
```

---

## 📋 Quick Reference Commands

Save this section for easy access!

```powershell
# ═══════════════════════════════════════════════
# AZURE CLI QUICK REFERENCE
# ═══════════════════════════════════════════════

# --- LOGIN & SETUP ---
az login                                    # Login to Azure
az account list --output table              # List subscriptions

# --- DEPLOYMENT ---
cd "D:\Mission Vanaspati"
.\deploy-azure.ps1 -AppName "your-app"      # Deploy everything

# --- CHECK STATUS ---
az webapp show --resource-group mission-vanaspati-rg --name YOUR-APP-NAME --query state
az postgres flexible-server show --resource-group mission-vanaspati-rg --name YOUR-APP-NAME-db --query state

# --- START SERVICES ---
az webapp start --resource-group mission-vanaspati-rg --name YOUR-APP-NAME
az postgres flexible-server start --resource-group mission-vanaspati-rg --name YOUR-APP-NAME-db

# --- STOP SERVICES (SAVE MONEY!) ---
az webapp stop --resource-group mission-vanaspati-rg --name YOUR-APP-NAME
az postgres flexible-server stop --resource-group mission-vanaspati-rg --name YOUR-APP-NAME-db

# --- RESTART ---
az webapp restart --resource-group mission-vanaspati-rg --name YOUR-APP-NAME

# --- VIEW LOGS ---
az webapp log tail --resource-group mission-vanaspati-rg --name YOUR-APP-NAME

# --- SSH INTO SERVER ---
az webapp ssh --resource-group mission-vanaspati-rg --name YOUR-APP-NAME

# --- UPDATE CORS ---
az webapp config appsettings set `
    --resource-group mission-vanaspati-rg `
    --name YOUR-APP-NAME `
    --settings ALLOWED_ORIGINS="https://your-frontend-url"

# --- DELETE EVERYTHING ---
.\azure-cleanup.ps1
# OR
az group delete --name mission-vanaspati-rg --yes
```

---

## 🗑️ Cleanup (When Done)

When you want to delete everything and stop all charges:

```powershell
cd "D:\Mission Vanaspati"
.\azure-cleanup.ps1
```

Or manually:
```powershell
az group delete --name mission-vanaspati-rg --yes --no-wait
```

**⚠️ This deletes EVERYTHING!** Your app, database, and all data will be gone.

---

## 🎓 Summary: What You Learned

After completing this guide, you now know how to:

- ✅ Install and use Azure CLI
- ✅ Deploy a Python backend to the cloud
- ✅ Set up a PostgreSQL database
- ✅ Upload files to cloud storage
- ✅ Deploy a React frontend
- ✅ Configure CORS for API security
- ✅ Manage cloud costs effectively
- ✅ Start/Stop services to save money
- ✅ View logs and troubleshoot issues

**🎉 Congratulations! You're now a cloud developer!**

---

## 📞 Quick Help

| Problem | Solution |
|---------|----------|
| Something broke | Check logs: `az webapp log tail ...` |
| Need to restart | `az webapp restart ...` |
| Want to save money | Stop services when not using |
| Forgot password | Re-deploy (or reset in Azure Portal) |
| Need help | Check Azure Portal → Your App → "Diagnose and solve problems" |

---

## 🚀 Your Deployment Checklist

- [ ] **Step 1:** Install Azure CLI
- [ ] **Step 2:** Login with `az login`
- [ ] **Step 3:** Choose unique app name
- [ ] **Step 4:** Run `deploy-azure.ps1`
- [ ] **Step 5:** Test backend at `/docs`
- [ ] **Step 6:** Initialize DB at `/init-db`
- [ ] **Step 7:** Deploy frontend to Vercel
- [ ] **Step 8:** Update CORS settings
- [ ] **Step 9:** Load remedies data
- [ ] **Step 10:** Create admin account
- [ ] **Step 11:** Test everything works!
- [ ] **Step 12:** Set up budget alerts
- [ ] **Step 13:** Stop services when not using

---

**Good luck with your deployment! 🚀🌿**

*Estimated Total Time: 30-45 minutes for first-time deployment*
