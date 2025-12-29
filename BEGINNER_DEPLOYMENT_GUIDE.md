# 🌱 Mission Vanaspati - Azure Deployment for Beginners

> **Complete step-by-step guide for first-time Azure users**

## 🎯 What You'll Do

Deploy your plant disease detection app to the cloud:
- **Local (now)** = Only you can access it
- **Azure (after)** = Anyone can access via URL

---

## 📦 What is Azure? (Simple Explanation)

**Azure** = Microsoft's cloud service (like Google Drive, but for apps)

### What we need from Azure:

1. **App Service** = A place to run your Python backend
   - Like renting a computer that runs 24/7
   - Costs: ~$13/month

2. **Database** = PostgreSQL storage for users, feedback, remedies
   - Like Excel, but powerful and always available
   - Costs: ~$12/month

3. **Storage** = A place to store your trained model file (500MB)
   - Like Google Drive for files
   - Costs: ~$0.50/month

4. **Static Web App** = A place to show your React website
   - Completely FREE!

**Total: $25.50/month** (you have $69 remaining credits = ~2.7 months)

**💡 Smart Tip:** Stop the App Service when not using it to save ~$13/month!
```bash
az webapp stop --resource-group mission-vanaspati-rg --name your-app-name
```
This can extend your hosting to 4-5 months!

---

## ✅ Step 1: Install Azure CLI (One-time Setup)

**What is CLI?** = Command Line Interface = A way to talk to Azure using text commands

### Download & Install:
1. Go to: https://aka.ms/installazurecliwindows
2. Download the installer (MSI file)
3. Run it and click "Next" until done
4. **Restart PowerShell** after installation

### Test it works:
```powershell
az --version
```
You should see version info. If not, restart your computer.

---

## ✅ Step 2: Login to Azure

Open PowerShell and type:
```powershell
az login
```

**What happens:**
- A browser window opens
- Log in with your Azure for Students account
- Browser says "You're logged in" - close it
- PowerShell shows your account info

✅ **You're now connected to Azure!**

---

## ✅ Step 3: Choose a Unique App Name

Your app needs a unique name (like choosing a username).

**Rules:**
- Only letters, numbers, hyphens
- Must be globally unique (no one else can have it)
- Examples: `vanaspati-john`, `plant-disease-mary`, `mission-vanaspati-2024`

**Write yours here:** `____________________`

---

## ✅ Step 4: Run the Deployment Script

### Copy this command and replace YOUR-APP-NAME:

```powershell
cd "d:\Mission Vanaspati"
.\deploy-azure.ps1 -AppName "YOUR-APP-NAME"
```

**Example:**
```powershell
cd "d:\Mission Vanaspati"
.\deploy-azure.ps1 -AppName "vanaspati-john"
```

### What happens (takes 10-15 minutes):

**Step 1/6:** Creates a "Resource Group" (a folder to organize everything)
**Step 2/6:** Creates PostgreSQL database and asks for password
   - **Enter a strong password** (write it down!)
   - Example: `MyPlant2024!Pass`
   
**Step 3/6:** Uploads your trained model (plant_classifier_final.pth) to cloud storage

**Step 4/6:** Creates a web server for your Python backend

**Step 5/6:** Deploys your FastAPI code

**Step 6/6:** Sets up environment variables (configuration)

### ✅ When done, you'll see:
```
=== Deployment Complete! ===

Backend URL: https://vanaspati-john.azurewebsites.net
```

**Copy this URL!** You'll need it.

---

## ✅ Step 5: Test Your Backend

Open your browser and go to:
```
https://YOUR-APP-NAME.azurewebsites.net/docs
```

**Example:** `https://vanaspati-john.azurewebsites.net/docs`

You should see an API documentation page. This means your backend is working! 🎉

---

## ✅ Step 6: Initialize the Database

Visit this URL in your browser:
```
https://YOUR-APP-NAME.azurewebsites.net/init-db
```

**What this does:** Creates all the database tables (users, remedies, feedback)

You should see: `{"message": "Database initialized successfully"}`

---

## ✅ Step 7: Deploy the Frontend

### What is Frontend?
Your React app (the website users see) needs to be deployed separately.

### Option A: Deploy to Vercel (Easiest - FREE Forever)

1. **Go to:** https://vercel.com
2. Click "Sign up" with GitHub
3. Click "Add New Project"
4. Import your repository
5. **Configure:**
   - Framework Preset: `Vite`
   - Root Directory: `frontend-react`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - **Add Environment Variable:**
     - Name: `VITE_API_URL`
     - Value: `https://YOUR-APP-NAME.azurewebsites.net`
6. Click "Deploy"

**Done in 2 minutes!** Vercel gives you a URL like: `https://your-app.vercel.app`

### Option B: Use Azure Static Web Apps (Uses Credits)

I'll help with this later if needed. Vercel is easier for beginners.

---

## ✅ Step 8: Update CORS Settings

**What is CORS?** = Security that allows your frontend to talk to your backend

After frontend is deployed, run this (replace URLs):

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

## ✅ Step 9: Create Your Admin Account

1. Visit your deployed frontend: `https://your-app.vercel.app`
2. Click "Sign Up"
3. Create an account with your email

### Make yourself admin:

Go to Azure Portal: https://portal.azure.com
1. Search for "PostgreSQL"
2. Click your database (mission-vanaspati-db)
3. Click "Connect" → "Query Editor"
4. Login with:
   - Username: `vanaspatiAdmin`
   - Password: (the one you created in Step 4)
5. Run this SQL:
```sql
UPDATE users SET role = 'admin' WHERE email = 'your-email@example.com';
```

Now you can access the Admin Panel!

---

## ✅ Step 10: Load Remedies Data

Your app needs the remedies data for predictions.

**SSH into your backend:**
```powershell
az webapp ssh --resource-group mission-vanaspati-rg --name YOUR-APP-NAME
```

**Inside the remote terminal:**
```bash
cd /home/site/wwwroot
python load_remedies.py
```

Type `exit` to leave.

---

## 🎉 YOU'RE DONE!

### Your Live URLs:
- **Frontend:** `https://your-app.vercel.app`
- **Backend API:** `https://YOUR-APP-NAME.azurewebsites.net`
- **Admin Panel:** `https://your-app.vercel.app` (click Admin after login)

### Test it:
1. Upload a plant image
2. Get prediction
3. View remedies
4. Check analytics in Admin Panel

---

## 🔧 Common Issues & Fixes

### "az: command not found"
**Fix:** Restart PowerShell or computer after installing Azure CLI

### "Name already taken"
**Fix:** Choose a different app name (must be globally unique)

### "Database connection failed"
**Fix:** Check you entered the correct password, try re-running init-db

### "CORS error" in browser console
**Fix:** Make sure you ran Step 8 with correct frontend URL

### "Model not found" error
**Fix:** Check models/plant_classifier_final.pth exists before deploying

### Frontend shows "Network Error"
**Fix:** 
1. Check backend URL in Vercel environment variables
2. Make sure backend is running (visit /docs endpoint)
3. Verify CORS is set correctly

---

## 💰 Managing Costs

### Check your spending:
https://portal.azure.com → Cost Management → Cost Analysis

### Stop everything (when not using):
```powershell
cd "d:\Mission Vanaspati"
.\azure-cleanup.ps1
```

This deletes everything and stops all charges.

### Start fresh later:
Just run `deploy-azure.ps1` again!

---

## 📞 Need Help?

### Check logs:
```powershell
az webapp log tail --resource-group mission-vanaspati-rg --name YOUR-APP-NAME
```

### View in browser:
Azure Portal → App Services → YOUR-APP-NAME → Log stream

---

## 🎓 What You Learned

✅ Cloud deployment basics
✅ Azure services (App Service, PostgreSQL, Storage)
✅ Frontend vs Backend deployment
✅ Environment variables
✅ Database management
✅ CORS and security

**You're now a cloud developer!** 🚀

---

## Quick Reference Card

```powershell
# Login to Azure
az login

# Deploy everything
.\deploy-azure.ps1 -AppName "your-app-name"

# Check status
az webapp show --resource-group mission-vanaspati-rg --name your-app-name --query state

# Restart app
az webapp restart --resource-group mission-vanaspati-rg --name your-app-name

# View logs
az webapp log tail --resource-group mission-vanaspati-rg --name your-app-name

# Delete everything
.\azure-cleanup.ps1
```

Save this for later! 📋
