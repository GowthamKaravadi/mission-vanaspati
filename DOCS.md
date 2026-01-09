# 📚 Documentation Index

## Choose Your Path:

### 🏠 Start Here
**[README.md](README.md)** - Complete project documentation
- Features, local setup, API reference
- Quick start commands
- Troubleshooting guide

---

### ☁️ Azure Deployment

#### 📖 Complete Guide (Recommended)
**[COMPLETE_AZURE_DEPLOYMENT_GUIDE.md](COMPLETE_AZURE_DEPLOYMENT_GUIDE.md)** - All-in-one guide (30-45 min)
- Step-by-step for beginners (zero Azure knowledge required)
- Automated deployment using scripts
- Cost breakdown & budget optimization
- Troubleshooting & quick reference commands

#### 🛠️ Manual Deployment
**[MANUAL_AZURE_DEPLOYMENT.md](MANUAL_AZURE_DEPLOYMENT.md)** - Full control (35-40 min)
- Run every command yourself
- Understand each Azure resource
- For those who want complete control
- Includes verification steps

---

## Quick Reference

### Local Development
```bash
# Start backend
cd "D:\Mission Vanaspati"
python -m uvicorn src.app:app --reload

# Start frontend
cd frontend-react && npm run dev
```

### Azure Deployment
```bash
# Login
az login

# Automated Deploy
.\deploy-azure.ps1 -AppName "your-unique-name"

# Manual Deploy - See MANUAL_AZURE_DEPLOYMENT.md
```

### Cost Management
```bash
# Stop services (save money)
az webapp stop --resource-group mission-vanaspati-rg --name your-app
az postgres flexible-server stop --resource-group mission-vanaspati-rg --name your-app-db

# Start services
az webapp start --resource-group mission-vanaspati-rg --name your-app
az postgres flexible-server start --resource-group mission-vanaspati-rg --name your-app-db
```

---

## File Structure

```
📄 README.md                           ← Main documentation
📄 DOCS.md                             ← This navigation file
📄 COMPLETE_AZURE_DEPLOYMENT_GUIDE.md  ← All-in-one deployment guide
📄 MANUAL_AZURE_DEPLOYMENT.md          ← Manual deployment commands

🔧 deploy-azure.ps1                    ← Automated deployment script
🔧 azure-cleanup.ps1                   ← Delete Azure resources

📁 src/                                ← Backend code (FastAPI)
📁 frontend-react/                     ← Frontend code (React + Vite)
📁 models/                             ← ML model files
📁 VIVA_DOCUMENTATION/                 ← Viva preparation docs
```

---

**New to the project?** Start with [README.md](README.md)  
**Ready to deploy?** Go to [COMPLETE_AZURE_DEPLOYMENT_GUIDE.md](COMPLETE_AZURE_DEPLOYMENT_GUIDE.md)  
**Want full control?** See [MANUAL_AZURE_DEPLOYMENT.md](MANUAL_AZURE_DEPLOYMENT.md)  
**Need help?** Check [README.md → Troubleshooting](README.md#-troubleshooting)
