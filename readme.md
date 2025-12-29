# 🌿 Mission Vanaspati - Complete Guide

**Plant Disease Classification System with ML**  
FastAPI + React + PyTorch + PostgreSQL

> 📚 **Navigation:** See [DOCS.md](DOCS.md) for all documentation | **Deploy:** [AZURE_READY_TO_DEPLOY.md](AZURE_READY_TO_DEPLOY.md)

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Features](#features)
3. [Local Development](#local-development)
4. [Azure Deployment](#azure-deployment)
5. [API Reference](#api-reference)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Local Setup (5 Minutes)

```powershell
# 1. Clone and navigate
cd "D:\Mission Vanaspati"

# 2. Activate virtual environment
.\vanaspati_env\Scripts\Activate.ps1

# 3. Start backend
python -m uvicorn src.fastapi_test:app --reload

# 4. In new terminal, start frontend
cd frontend-react
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### First Time Setup

```bash
# Install dependencies (if needed)
pip install -r requirements.txt
cd frontend-react && npm install

# Initialize database
python init_db.py

# Load disease remedies
python load_remedies.py
```

---

## ✨ Features

### Core Features
- 🔬 **AI Disease Detection** - 38 plant diseases, 50 classes (ResNet50)
- 👤 **User Authentication** - Username/email login, JWT tokens
- 📊 **Batch Processing** - Analyze multiple images at once
- 📖 **Disease Library** - Searchable encyclopedia of all diseases
- 💬 **Feedback System** - Report accuracy, suggest improvements
- 📈 **Analytics Dashboard** - Admin panel with charts
- 🌙 **Dark/Light Theme** - System preference detection
- 📱 **Responsive Design** - Mobile-friendly UI

### Technical Stack
**Backend:**
- FastAPI - REST API framework
- PyTorch 2.5.1 - Deep learning
- PostgreSQL - User data & predictions
- JWT - Authentication
- SQLAlchemy - ORM

**Frontend:**
- React 19 - UI framework
- Vite - Build tool
- Framer Motion - Animations
- Recharts - Data visualization

**ML Model:**
- ResNet50 pretrained on ImageNet
- Fine-tuned on PlantVillage dataset
- Image validation (green detection, texture analysis)
- 38 disease classes across multiple crops

---

## 💻 Local Development

### Database Setup

**Option 1: PostgreSQL (Recommended)**
```bash
# Install PostgreSQL
# Create database
createdb vanaspati_db

# Update connection in src/database.py
DATABASE_URL = "postgresql://user:password@localhost:5432/vanaspati_db"

# Initialize
python init_db.py
```

**Option 2: SQLite (Quick Testing)**
```python
# In src/database.py, change to:
DATABASE_URL = "sqlite:///./vanaspati.db"
```

### Create Admin User

```python
# Run after database initialization
from src.database import SessionLocal, User
db = SessionLocal()
admin = User(
    username='admin',
    email='admin@example.com',
    hashed_password=User.hash_password('YourPassword123'),
    is_admin=True
)
db.add(admin)
db.commit()
```

### Model Training (Optional)

```bash
# Train new model
python src/train.py

# Config in config.py:
# - Epochs, batch size, learning rate
# - Two-stage training (freeze/unfreeze)
# - MixUp augmentation
# - AdamW optimizer + CosineAnnealingLR
```

### API Testing

```bash
# Health check
curl http://localhost:8000/

# Signup
curl -X POST "http://localhost:8000/auth/signup?username=test&email=test@example.com&password=Test123"

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -F "username=test" \
  -F "password=Test123"

# Predict (with token)
curl -X POST "http://localhost:8000/predict" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@image.jpg"
```

---

## ☁️ Azure Deployment

### Option 1: Automated (10 Minutes) ⭐ RECOMMENDED

```powershell
# 1. Install Azure CLI (one-time)
winget install Microsoft.AzureCLI

# 2. Login
az login

# 3. Deploy everything
.\deploy-azure.ps1 -ResourceGroupName "vanaspati-rg" -Location "eastus" -AppName "vanaspati-yourname"
```

**What it deploys:**
- PostgreSQL database (B1ms tier)
- App Service (B1 tier)
- Storage Account (model files)
- Automatic configuration

### Option 2: Manual Deployment

#### 1. Create Resources

```bash
# Resource group
az group create --name vanaspati-rg --location eastus

# PostgreSQL
az postgres flexible-server create \
  --resource-group vanaspati-rg \
  --name vanaspati-db \
  --admin-user vanaspatiAdmin \
  --admin-password "YourSecurePass123!" \
  --sku-name Standard_B1ms \
  --tier Burstable

# Create database
az postgres flexible-server db create \
  --resource-group vanaspati-rg \
  --server-name vanaspati-db \
  --database-name vanaspatidb
```

#### 2. Deploy Backend

```bash
# Create App Service
az appservice plan create \
  --name vanaspati-plan \
  --resource-group vanaspati-rg \
  --sku B1 \
  --is-linux

az webapp create \
  --resource-group vanaspati-rg \
  --plan vanaspati-plan \
  --name vanaspati-yourname \
  --runtime "PYTHON:3.12"

# Deploy code
az webapp up \
  --resource-group vanaspati-rg \
  --name vanaspati-yourname \
  --runtime "PYTHON:3.12"
```

#### 3. Deploy Frontend

```bash
# Build
cd frontend-react
npm run build

# Deploy to Azure Static Web Apps
az staticwebapp create \
  --name vanaspati-frontend \
  --resource-group vanaspati-rg \
  --source dist \
  --location "Central US"
```

### Post-Deployment Steps

```bash
# 1. Initialize database
curl https://vanaspati-yourname.azurewebsites.net/init-db

# 2. SSH to create admin
az webapp ssh --resource-group vanaspati-rg --name vanaspati-yourname
python -c "from src.database import *; ..."

# 3. Load remedies
curl -X POST https://vanaspati-yourname.azurewebsites.net/load-remedies

# 4. Update CORS
az webapp config appsettings set \
  --resource-group vanaspati-rg \
  --name vanaspati-yourname \
  --settings FRONTEND_URL=https://your-frontend.azurestaticapps.net
```

### Cost Management

**Monthly Costs:**
- App Service (B1): $13
- PostgreSQL (B1ms): $12
- Storage: $0.50
- Static Web App: FREE
- **Total: $25.50/month**

**With $69 credits = 2.7 months 24/7 OR 5-8 months with smart scheduling**

**Save money:**
```bash
# Stop when not using
az webapp stop --resource-group vanaspati-rg --name vanaspati-yourname
az postgres flexible-server stop --resource-group vanaspati-rg --name vanaspati-db

# Start when needed (2-3 min)
az webapp start --resource-group vanaspati-rg --name vanaspati-yourname
az postgres flexible-server start --resource-group vanaspati-rg --name vanaspati-db
```

---

## 📚 API Reference

### Authentication

**POST /auth/signup**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"  // Min 8 chars, 1 uppercase, 1 number
}
```

**POST /auth/login**
```
Form data:
- username: string (username or email)
- password: string
```
Returns: `{ access_token, username, email, is_admin }`

**GET /auth/me**
Headers: `Authorization: Bearer TOKEN`  
Returns: Current user info

### Predictions

**POST /predict**
- Headers: `Authorization: Bearer TOKEN`
- Body: `multipart/form-data` with `file` field
- Returns: Disease name, confidence, remedies

**POST /predict/batch**
- Multiple files in `files` array
- Returns: Array of predictions

### Admin (Requires admin role)

**GET /admin/users** - List all users  
**PUT /admin/users/{id}/toggle-admin** - Make user admin  
**DELETE /admin/users/{id}** - Delete user  
**GET /admin/feedback** - View feedback  
**PATCH /admin/feedback/{id}** - Update feedback status

---

## 🔧 Troubleshooting

### Backend Issues

**"Module not found"**
```bash
pip install -r requirements.txt
```

**"Database connection failed"**
```bash
# Check PostgreSQL is running
# Verify DATABASE_URL in src/database.py
# For Azure: Check firewall rules
```

**"Model not found"**
```bash
# Verify model file exists
ls models/plant_classifier_final.pth

# Download if missing (500MB)
# Contact repo owner for model file
```

### Frontend Issues

**"Network Error"**
```bash
# Check backend is running
# Update API URL in frontend-react/.env.development
VITE_API_URL=http://localhost:8000
```

**"CORS Error"**
```bash
# Backend: Update ALLOWED_ORIGINS in src/fastapi_test.py
# Or set environment variable FRONTEND_URL
```

### Deployment Issues

**"App won't start"**
```bash
# Check logs
az webapp log tail --resource-group vanaspati-rg --name vanaspati-yourname

# Restart
az webapp restart --resource-group vanaspati-rg --name vanaspati-yourname
```

**"Model upload failed"**
```bash
# Upload manually
az storage blob upload \
  --account-name yourstorage \
  --container-name models \
  --name plant_classifier_final.pth \
  --file models/plant_classifier_final.pth
```

---

## 🎓 Project Structure

```
Mission Vanaspati/
├── src/
│   ├── app.py              # Main FastAPI app
│   ├── auth.py             # JWT authentication
│   ├── database.py         # SQLAlchemy models
│   ├── fastapi_test.py     # API endpoints
│   ├── train.py            # Model training
│   └── core/
│       ├── model.py        # ResNet50 model
│       ├── predictor.py    # Inference + validation
│       ├── dataset.py      # Data loading
│       └── trainer.py      # Training loop
├── frontend-react/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── context/        # Auth, Theme, History
│   │   └── services/       # API client
│   └── package.json
├── models/
│   ├── plant_classifier_final.pth   # Trained model
│   └── class_mapping.json           # Class names
├── data/                   # Training datasets
├── requirements.txt        # Python dependencies
├── deploy-azure.ps1       # Automated deployment
└── README.md              # This file
```

---

## 📖 Key Concepts

### Username Authentication
- Users can signup with username + email
- Login with either username OR email
- UI displays username (not email)
- Database migrated from email-only to username+email

### Image Validation
Model validates plant images before prediction:
- **Green pixel detection** - Minimum 10% green pixels
- **Texture analysis** - Standard deviation check
- **Edge density** - Rejects solid colors or noise
- **Aspect ratio** - Rejects unusual dimensions

### Two-Stage Training
1. **Stage 1 (5 epochs)** - Freeze pretrained layers, train classifier only
2. **Stage 2 (15 epochs)** - Unfreeze all layers, fine-tune entire model
3. **MixUp augmentation** - Mix training samples for better generalization
4. **CosineAnnealingLR** - Learning rate scheduling

---

## 🤝 Contributing

To add new features:
1. Create feature branch
2. Update backend (`src/`) and/or frontend (`frontend-react/src/`)
3. Test locally
4. Update this README
5. Submit PR

---

## 📝 License

Educational project - free to use and modify

---

## 🆘 Support

- **Logs:** `az webapp log tail` (Azure) or check console (local)
- **API Docs:** http://localhost:8000/docs or https://your-app.azurewebsites.net/docs
- **Issues:** Check console errors, verify auth tokens, check CORS settings

---

## ✅ Quick Commands Reference

```bash
# Local Development
python -m uvicorn src.fastapi_test:app --reload    # Start backend
cd frontend-react && npm run dev                    # Start frontend
python init_db.py                                   # Initialize DB
python load_remedies.py                             # Load data

# Azure Deployment
az login                                            # Login to Azure
.\deploy-azure.ps1 -ResourceGroupName "rg" -Location "eastus" -AppName "app"
az webapp log tail --resource-group rg --name app   # View logs
az webapp stop --resource-group rg --name app       # Stop (save money)
az webapp start --resource-group rg --name app      # Start

# Database
python add_username_migration.py                    # Add username column
createdb vanaspati_db                               # Create PostgreSQL DB

# Testing
curl http://localhost:8000/docs                     # API documentation
curl -X POST http://localhost:8000/auth/signup      # Test signup
```

---

**Built with ❤️ for plant health monitoring**
