# 📚 Documentation Index

## Choose Your Path:

### 🏠 Start Here
**[README.md](README.md)** - Complete project documentation
- Features, local setup, API reference
- Quick start commands
- Troubleshooting guide

---

### ☁️ Azure Deployment (Choose ONE)

#### 1️⃣ Quick & Easy
**[AZURE_READY_TO_DEPLOY.md](AZURE_READY_TO_DEPLOY.md)** - Fast deployment (10-15 min)
- 3-command automated deployment
- For users familiar with command line

#### 2️⃣ Step-by-Step
**[BEGINNER_DEPLOYMENT_GUIDE.md](BEGINNER_DEPLOYMENT_GUIDE.md)** - Detailed guide (30 min)
- For first-time Azure users
- Explains each step
- Includes screenshots and explanations

#### 3️⃣ Budget Conscious
**[BUDGET_OPTIMIZED_DEPLOYMENT.md](BUDGET_OPTIMIZED_DEPLOYMENT.md)** - Maximize your $69
- Cost-saving strategies
- Start/stop commands
- Extend hosting to 5-8 months

---

## Quick Reference

### Local Development
```bash
# Start backend
python -m uvicorn src.fastapi_test:app --reload

# Start frontend
cd frontend-react && npm run dev
```

### Azure Deployment
```bash
# Login
az login

# Deploy
.\deploy-azure.ps1 -ResourceGroupName "vanaspati-rg" -Location "eastus" -AppName "your-unique-name"
```

### Cost Management
```bash
# Stop services (save money)
az webapp stop --resource-group vanaspati-rg --name your-app
az postgres flexible-server stop --resource-group vanaspati-rg --name your-db

# Start services
az webapp start --resource-group vanaspati-rg --name your-app
az postgres flexible-server start --resource-group vanaspati-rg --name your-db
```

---

## File Structure

```
📄 README.md                        ← Main documentation
📄 DOCS.md                          ← This navigation file
📄 AZURE_READY_TO_DEPLOY.md        ← Quick Azure deployment
📄 BEGINNER_DEPLOYMENT_GUIDE.md    ← Detailed Azure guide
📄 BUDGET_OPTIMIZED_DEPLOYMENT.md  ← Cost optimization

🔧 deploy-azure.ps1                ← Automated deployment script
🔧 azure-cleanup.ps1               ← Delete Azure resources

📁 src/                            ← Backend code
📁 frontend-react/                 ← Frontend code
📁 models/                         ← ML model files
```

---

**New to the project?** Start with [README.md](README.md)  
**Ready to deploy?** Go to [AZURE_READY_TO_DEPLOY.md](AZURE_READY_TO_DEPLOY.md)  
**Need help?** Check [README.md → Troubleshooting](README.md#-troubleshooting)
