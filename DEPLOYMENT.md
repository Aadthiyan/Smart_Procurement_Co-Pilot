# Deployment Guide - Smart Procurement Co-Pilot

## Overview

This guide provides instructions for deploying the Smart Procurement Co-Pilot in different environments.

---

## 🚀 Quick Start (Local Demo)

### Prerequisites
- Python 3.9 or higher
- Git
- 2GB RAM minimum

### Installation (5 minutes)

```bash
# Clone the repository
git clone https://github.com/Aadthiyan/Smart_Procurement_Co-Pilot.git
cd Smart_Procurement_Co-Pilot

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional - works without IBM Cloud)
cp src/config/cloud.env.example src/config/cloud.env
# Edit cloud.env with your IBM Cloud credentials (optional)
```

### Running the Demo

**Option 1: One-Click Launch (Windows)**
```bash
run_demo.bat
```

**Option 2: Manual Launch**
```bash
# Terminal 1: Start Backend
python src/backend/server.py

# Terminal 2: Start Frontend
streamlit run src/frontend/app.py
```

### Access the Application
- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

---

## ☁️ Cloud Deployment (IBM Cloud)

### Option 1: IBM Cloud Code Engine (Recommended)

#### Prerequisites
- IBM Cloud account
- IBM Cloud CLI installed
- Docker installed

#### Step 1: Prepare Docker Container

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501 5000

CMD ["sh", "-c", "python src/backend/server.py & streamlit run src/frontend/app.py --server.port=8501 --server.address=0.0.0.0"]
```

#### Step 2: Build and Push to IBM Container Registry

```bash
# Login to IBM Cloud
ibmcloud login

# Set region
ibmcloud target -r us-south

# Create namespace (if not exists)
ibmcloud cr namespace-add procurement-copilot

# Build and push image
docker build -t us.icr.io/procurement-copilot/smart-procurement:latest .
docker push us.icr.io/procurement-copilot/smart-procurement:latest
```

#### Step 3: Deploy to Code Engine

```bash
# Create Code Engine project
ibmcloud ce project create --name procurement-copilot

# Deploy application
ibmcloud ce application create \
  --name smart-procurement-copilot \
  --image us.icr.io/procurement-copilot/smart-procurement:latest \
  --port 8501 \
  --min-scale 1 \
  --max-scale 3 \
  --cpu 1 \
  --memory 2G \
  --env CLOUDANT_URL=$CLOUDANT_URL \
  --env CLOUDANT_APIKEY=$CLOUDANT_APIKEY \
  --env WATSONX_APIKEY=$WATSONX_APIKEY \
  --env WATSONX_URL=$WATSONX_URL

# Get application URL
ibmcloud ce application get --name smart-procurement-copilot
```

Your application will be available at: `https://smart-procurement-copilot.xxxxxx.us-south.codeengine.appdomain.cloud`

---

### Option 2: Streamlit Community Cloud (Free, No IBM Services)

#### Prerequisites
- GitHub account
- Streamlit Community Cloud account (free at share.streamlit.io)

#### Steps

1. **Push code to GitHub** (already done ✅)
   ```bash
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your repository: `Aadthiyan/Smart_Procurement_Co-Pilot`
   - Main file path: `src/frontend/app.py`
   - Click "Deploy"

3. **Configure Secrets** (in Streamlit Cloud dashboard):
   ```toml
   # .streamlit/secrets.toml
   CLOUDANT_URL = "your-cloudant-url"
   CLOUDANT_APIKEY = "your-api-key"
   WATSONX_APIKEY = "your-watsonx-key"
   WATSONX_URL = "your-watsonx-url"
   ```

4. **Access your app**:
   - URL: `https://[your-app-name].streamlit.app`

**Note**: Streamlit Cloud only hosts the frontend. Backend API won't be available, but the app will work in demo mode.

---

### Option 3: Heroku Deployment

#### Prerequisites
- Heroku account
- Heroku CLI installed

#### Steps

1. **Create Heroku app**:
   ```bash
   heroku create smart-procurement-copilot
   ```

2. **Add Procfile**:
   ```
   web: sh -c 'python src/backend/server.py & streamlit run src/frontend/app.py --server.port=$PORT --server.address=0.0.0.0'
   ```

3. **Configure environment variables**:
   ```bash
   heroku config:set CLOUDANT_URL=your-url
   heroku config:set CLOUDANT_APIKEY=your-key
   heroku config:set WATSONX_APIKEY=your-key
   heroku config:set WATSONX_URL=your-url
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

5. **Access**:
   - URL: `https://smart-procurement-copilot.herokuapp.com`

---

## 🔐 Environment Configuration

### Required Environment Variables

For full functionality with IBM Cloud services:

```bash
# IBM Cloudant (Database)
CLOUDANT_URL=https://your-instance.cloudantnosqldb.appdomain.cloud
CLOUDANT_APIKEY=your-cloudant-api-key

# IBM watsonx.ai (LLM Reasoning)
WATSONX_APIKEY=your-watsonx-api-key
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# IBM Natural Language Understanding (Optional)
NLU_APIKEY=your-nlu-api-key
NLU_URL=https://api.us-south.natural-language-understanding.watson.cloud.ibm.com

# IBM Secrets Manager (Optional)
SECRETS_MANAGER_URL=your-secrets-manager-url
SECRETS_MANAGER_APIKEY=your-api-key
```

### Demo Mode (No IBM Cloud Required)

The application works in **demo mode** without any IBM Cloud credentials:
- Uses local JSON file storage instead of Cloudant
- Uses mock LLM responses instead of watsonx.ai
- All features functional for demonstration

---

## 🧪 Testing the Deployment

### Health Check

```bash
# Check backend health
curl http://your-deployment-url:5000/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-11-23"
}
```

### Component Status

```bash
# Check all components initialized
curl http://your-deployment-url:5000/api/init-status

# Expected response:
{
  "status": "initialized",
  "components": {
    "security": "ready",
    "audit_logging": "ready",
    "session_management": "ready",
    "agent_communication": "ready",
    "watsonx_orchestration": "ready",
    "skill_framework": "ready"
  }
}
```

### Functional Test

1. Open the frontend URL in browser
2. Try the demo scenarios:
   - "Add vendor: TestCorp, Tax ID: 12-3456789"
   - "I need to buy 5 laptops"
   - "Check status of REQ-001"

---

## 📊 Monitoring & Logs

### View Application Logs

**Local Deployment**:
```bash
# View audit logs
cat logs/audit.log

# View workflow logs
cat logs/workflow_execution.log
```

**IBM Cloud Code Engine**:
```bash
# View logs
ibmcloud ce application logs --name smart-procurement-copilot --follow
```

**Streamlit Cloud**:
- View logs in the Streamlit Cloud dashboard

---

## 🔒 Security Considerations

### For Production Deployment

1. **Enable HTTPS**: Always use SSL/TLS in production
2. **Set Strong Secrets**: Use IBM Secrets Manager for credentials
3. **Enable RBAC**: Configure role-based access control
4. **Audit Logging**: Ensure all logs are sent to IBM Log Analysis
5. **Network Security**: Use VPC and security groups
6. **Rate Limiting**: Implement API rate limiting

### For Demo/Hackathon

- ✅ Demo mode is safe (no real credentials needed)
- ✅ Local storage only (no sensitive data)
- ✅ RBAC is mocked (for demonstration)
- ⚠️ Not suitable for production use

---

## 🐛 Troubleshooting

### Issue: Port Already in Use

```bash
# Kill process on port 8501
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8501 | xargs kill -9
```

### Issue: Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Cloudant Connection Failed

- Check if `CLOUDANT_URL` and `CLOUDANT_APIKEY` are set correctly
- Application will fall back to local storage automatically
- Check `logs/workflow_execution.log` for details

### Issue: Streamlit Not Starting

```bash
# Clear Streamlit cache
streamlit cache clear

# Run with verbose logging
streamlit run src/frontend/app.py --logger.level=debug
```

---

## 📈 Scaling Considerations

### IBM Cloud Code Engine Auto-Scaling

```bash
# Update scaling configuration
ibmcloud ce application update smart-procurement-copilot \
  --min-scale 1 \
  --max-scale 10 \
  --concurrency 100
```

### Performance Optimization

1. **Enable Caching**: Use Redis for session caching
2. **Database Indexing**: Create indexes on Cloudant for faster queries
3. **CDN**: Use IBM Cloud CDN for static assets
4. **Load Balancing**: Use IBM Cloud Load Balancer for multiple instances

---

## 💰 Cost Estimation

### IBM Cloud Code Engine

- **Free Tier**: 100,000 vCPU-seconds/month
- **Estimated Cost** (for hackathon demo):
  - 1 instance × 1 vCPU × 24 hours = ~$5/month
  - Cloudant Lite: Free (1GB storage)
  - watsonx.ai: Pay-as-you-go (~$0.01 per request)

**Total Estimated Cost**: $5-10/month for demo

---

## 🎯 Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Health check passing
- [ ] Frontend accessible
- [ ] Backend API responding
- [ ] Demo scenarios tested
- [ ] Logs are being generated
- [ ] Security audit passed
- [ ] Documentation updated

---

## 📞 Support

For deployment issues:
1. Check the troubleshooting section above
2. Review logs in `logs/` directory
3. Check GitHub Issues: https://github.com/Aadthiyan/Smart_Procurement_Co-Pilot/issues
4. Contact: [your-email@example.com]

---

## 🔗 Useful Links

- **GitHub Repository**: https://github.com/Aadthiyan/Smart_Procurement_Co-Pilot
- **IBM Cloud Console**: https://cloud.ibm.com
- **Streamlit Cloud**: https://share.streamlit.io
- **Documentation**: See `README.md` and `docs/` folder

---

**Last Updated**: November 23, 2025
**Version**: 1.0.0
