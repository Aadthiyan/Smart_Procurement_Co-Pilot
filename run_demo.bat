@echo off
echo ===================================================
echo 🚀 Starting Smart Procurement Co-Pilot Demo
echo ===================================================

echo.
echo [1/3] Initializing Backend Server...
start "Backend Server" cmd /k "python src/backend/server.py"

echo.
echo [2/3] Waiting for backend to initialize (5 seconds)...
timeout /t 5 >nul

echo.
echo [3/3] Launching Frontend Interface...
start "Frontend UI" cmd /k "streamlit run src/frontend/app.py"

echo.
echo ===================================================
echo 🎉 Demo Started Successfully!
echo 📱 Access the UI at: http://localhost:8501
echo 🔧 Backend API at:   http://localhost:5000
echo ===================================================
pause
