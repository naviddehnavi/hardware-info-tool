@echo off
python -c "import pkgutil, sys; req=['psutil','GPUtil','wmi','cpuinfo','requests']; missing=[r for r in req if not pkgutil.find_loader(r)]; sys.exit(len(missing))" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
)
python main.py
pause
