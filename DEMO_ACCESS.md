# Demo Access Instructions

## 🎯 Quick Access

### Option 1: Local Demo (Recommended for Judges)

**Requirements**: Python 3.9+, Git

**Setup Time**: 5 minutes

```bash
# Clone and run
git clone https://github.com/Aadthiyan/Smart_Procurement_Co-Pilot.git
cd Smart_Procurement_Co-Pilot
pip install -r requirements.txt
run_demo.bat  # Windows
# OR
python src/backend/server.py & streamlit run src/frontend/app.py  # Linux/Mac
```

**Access**:
- Frontend: http://localhost:8501
- Backend API: http://localhost:5000

---

### Option 2: Live Demo (If Deployed)

**URL**: [To be added after deployment]

**Demo Credentials** (if authentication enabled):
- Username: `demo_user`
- Password: `demo123`

**Note**: Demo mode uses mock data and local storage. No IBM Cloud credentials required.

---

## 🧪 Test Scenarios

Once the application is running, try these scenarios:

### Scenario 1: Vendor Onboarding
```
Chat Input: "Add vendor: Quantum Systems Inc, Tax ID: 99-8877665, Industry: Technology Hardware"

Expected: Agent validates and approves vendor autonomously
```

### Scenario 2: Purchase Request
```
Chat Input: "I need to buy 5 ergonomic chairs for IT"

Expected: Agent checks budget, searches catalog, routes for approval
```

### Scenario 3: Policy Compliance
```
Chat Input: "Order a $12,000 espresso machine"

Expected: Agent detects policy violation and blocks request
```

### Scenario 4: Status Check
```
Chat Input: "Check status of REQ-101"

Expected: Agent retrieves and displays request status
```

---

## 📊 Dashboard Features

Navigate to the **Dashboard** tab to see:
- Active sessions
- Pending approvals
- Vendor statistics
- Quick actions (Create PO, Onboard Vendor)

Navigate to **Settings** to:
- Change user role (demo RBAC)
- View session information
- See recent audit events

Navigate to **Admin** (requires Admin role) to:
- View system statistics
- Cleanup expired sessions
- Monitor agent activity

---

## 🔍 What to Look For

### 1. Agentic AI in Action
- Watch agents make **autonomous decisions**
- See **LLM reasoning** in audit logs
- Observe **multi-agent collaboration**

### 2. IBM watsonx Integration
- Check `/api/init-status` to see watsonx components
- View audit logs showing watsonx.ai usage
- See orchestration workflows in action

### 3. Enterprise Features
- **RBAC**: Try different roles in Settings
- **Audit Trail**: View logs in Settings → Recent Audit Events
- **Session Management**: See active sessions in Admin panel

---

## 🐛 Troubleshooting

### Issue: Application won't start
**Solution**: Ensure Python 3.9+ is installed and all dependencies are installed via `pip install -r requirements.txt`

### Issue: Port already in use
**Solution**: 
```bash
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8501 | xargs kill -9
```

### Issue: "Module not found" error
**Solution**: 
```bash
pip install -r requirements.txt --force-reinstall
```

---

## 📹 Video Demo

If you prefer to watch a video demonstration:
- **YouTube**: [Link to be added]
- **Duration**: 3 minutes
- **Covers**: All 4 demo scenarios

---

## 💡 Tips for Judges

1. **Start with Chat**: The chat interface is the main interaction point
2. **Check Audit Logs**: Settings → Recent Audit Events shows agent decisions
3. **Try Different Roles**: Settings → User Role to see RBAC in action
4. **View Dashboard**: See metrics and system overview
5. **Read README**: Comprehensive documentation of agentic AI principles

---

## 📞 Support

If you encounter any issues accessing the demo:
- **Email**: [your-email@example.com]
- **GitHub Issues**: https://github.com/Aadthiyan/Smart_Procurement_Co-Pilot/issues
- **Documentation**: See `README.md` for detailed information

---

## 🔗 Additional Resources

- **GitHub Repository**: https://github.com/Aadthiyan/Smart_Procurement_Co-Pilot
- **Architecture Documentation**: See `ARCHITECTURE.md`
- **API Documentation**: See `docs/api-guide.md`
- **Usage Guide**: See `USAGE.md`

---

**Last Updated**: November 23, 2025
**Demo Version**: 1.0.0
