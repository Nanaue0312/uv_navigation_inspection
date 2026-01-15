#!/usr/bin/env bash
set -euo pipefail

# setup.sh - 创建虚拟环境并安装依赖
# Usage: ./setup.sh [--with-uv] [--run-tests]

WITH_UV=false
RUN_TESTS=false
ALLOW_OLDER=false
RECREATE_VENV=false
CUSTOM_PYTHON=""

usage() {
  cat <<EOF
Usage: $0 [--with-uv] [--run-tests] [--allow-older-python] [--python <path>] [--recreate-venv]

--with-uv    Install the optional "uv" package (recommended for running with uv)
--run-tests  Run test suite after installing dependencies (uses pytest)
--allow-older-python  Proceed even if system Python < 3.12 (not recommended)
--python <path>  Use a specific Python executable to create the virtualenv (e.g. /opt/homebrew/bin/python3.14)
--recreate-venv  If .venv exists, remove it and create a new virtualenv using the selected Python
EOF
}  

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-uv) WITH_UV=true; shift ;;
    --run-tests) RUN_TESTS=true; shift ;;
    --allow-older-python) ALLOW_OLDER=true; shift ;;
    --recreate-venv) RECREATE_VENV=true; shift ;;
    --python) if [[ -z "${2-}" ]]; then echo "--python requires an argument"; usage; exit 1; fi; CUSTOM_PYTHON="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown option: $1"; usage; exit 1;;
  esac
done

# Prefer python3.14, otherwise fallback to common names and pick the first available
CANDIDATES=("python3.14" "python3.14m" "python3" "python")
PYTHON_CMD=""

if [[ -n "$CUSTOM_PYTHON" ]]; then
  if command -v "$CUSTOM_PYTHON" >/dev/null 2>&1 || [[ -x "$CUSTOM_PYTHON" ]]; then
    PYTHON_CMD="$CUSTOM_PYTHON"
  else
    echo "Custom python '$CUSTOM_PYTHON' not found or not executable." >&2
    exit 1
  fi
else
  for c in "${CANDIDATES[@]}"; do
    if command -v "$c" >/dev/null 2>&1; then
      PYTHON_CMD="$c"
      # Prefer a candidate that meets the minimum version
      if "$c" -c 'import sys; sys.exit(0) if sys.version_info >= (3,12) else sys.exit(2)' >/dev/null 2>&1; then
        break
      fi
    fi
  done
fi

if [ -z "$PYTHON_CMD" ]; then
  echo "Python is not found on PATH. Please install Python >= 3.12." >&2
  exit 1
fi

# Validate version
if ! "$PYTHON_CMD" -c "import sys; sys.exit(0) if sys.version_info >= (3,12) else sys.exit(2)"; then
  if [ "$ALLOW_OLDER" = true ]; then
    echo "Warning: Proceeding with older Python: $($PYTHON_CMD -V 2>&1). This is not recommended." >&2
  else
    echo "Python >= 3.12 is required. Detected: $($PYTHON_CMD -V 2>&1)" >&2
    cat <<'INSTR' >&2

Recommended ways to install Python 3.14 on macOS:

1) Homebrew:
   brew install python@3.14
   echo 'export PATH="/opt/homebrew/opt/python@3.14/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc

2) pyenv (per-project, recommended):
   brew install pyenv
   pyenv install 3.14.2
   pyenv local 3.14.2
   exec $SHELL

3) If you use mambaforge/conda, create or activate a 3.14 env:
   mamba create -n uvsim python=3.14.2
   mamba activate uvsim

After installing, re-run: ./setup.sh

If you truly want to continue with the current Python, re-run with:
  ./setup.sh --allow-older-python

INSTR
    exit 2
  fi
fi

# If .venv exists, optionally recreate it
if [[ -d ".venv" ]]; then
  if [[ "$RECREATE_VENV" == "true" ]]; then
    echo "Removing existing .venv..."
    rm -rf .venv
  else
    echo ".venv already exists. To recreate with a different Python, run: ./setup.sh --recreate-venv --python <path>"
    echo "Using existing .venv (skip creation)."
    # Activate existing venv and continue
    # shellcheck source=/dev/null
    source .venv/bin/activate
    echo "Activated existing .venv with $(python -V 2>&1)"
    # Continue to install packages into existing venv
    SKIP_VENV_CREATION=true
  fi
fi


echo "Creating virtual environment in .venv..."
$PYTHON_CMD -m venv .venv

# shellcheck source=/dev/null
source .venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

if [[ -f requirements.txt ]]; then
  echo "Installing requirements.txt..."
  pip install -r requirements.txt
else
  echo "No requirements.txt found, skipping.";
fi

# Attempt editable install if project metadata exists
if [[ -f pyproject.toml || -f setup.py ]]; then
  echo "Attempting editable install (pip install -e .)"
  pip install -e . || echo "Editable install failed — you can install manually."
fi

if [[ "$WITH_UV" == true ]]; then
  echo "Installing 'uv' package..."
  pip install uv || echo "Failed to install uv (you can install it manually)."
fi

if [[ "$RUN_TESTS" == true ]]; then
  echo "Running tests (pytest)..."
  if command -v pytest >/dev/null 2>&1; then
    pytest -q || echo "Some tests failed.";
  else
    echo "pytest not found, installing pytest...";
    pip install pytest
    pytest -q || echo "Some tests failed.";
  fi
fi

echo "Setup complete. To activate the environment, run:"
echo "  source .venv/bin/activate"

echo "Tip: make script executable with 'chmod +x setup.sh' if needed."
