@echo off
REM setup.bat - Create venv and install dependencies (Windows cmd)
SETLOCAL ENABLEDELAYEDEXPANSION




































exit /b 0echo    .\.venv\Scripts\activateecho To activate the virtual environment run:
necho Setup complete.)  %PIP% install -e . || echo Editable install failed - install manually.  echo Attempting editable install (pip install -e .)
nIF EXIST pyproject.toml ()  echo No requirements.txt found, skipping.) ELSE (  %PIP% install -r requirements.txt  echo Installing requirements.txt...
nIF EXIST requirements.txt (%PIP% install --upgrade pip
necho Upgrading pip...)  exit /b 3  echo pip not found in .venv. Please check virtualenv creation.
nSET PIP=.venv\Scripts\pip.exe
nIF NOT EXIST %PIP% ()  exit /b 2  echo Failed to create venv or Python version too low.print('venv ready')" || (    venv.create('.venv', with_pip=True)if not os.path.exists('.venv'):    raise SystemExit('Python >= 3.12 required')if sys.version_info < (3,12):python -c "import sys,os,venv
necho Ensuring Python >= 3.12 and creating virtualenv (if needed)...)  exit /b 1  echo Python not found on PATH. Please install Python >= 3.12.python -V >nul 2>&1 || (necho Checking for Python...