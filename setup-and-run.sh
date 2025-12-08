#!/bin/bash
# setup-and-run-mac.sh
set -e

echo "--------------------------------------------"
echo "Neubond Dashboard Setup and Run Script (macOS)"
echo "--------------------------------------------"

# 1. Check Python
PYTHON_CMD=python3
if ! command -v $PYTHON_CMD &>/dev/null; then
    PYTHON_CMD=python
    if ! command -v $PYTHON_CMD &>/dev/null; then
        echo "Python 3 not found. Please install it."
        exit 1
    fi
fi

# 2. Check Git
if ! command -v git &>/dev/null; then
    echo "Git not found. Please install Git."
    exit 1
fi

REPO_DIR="Neubond-Clinician-Dashboard-Streamlit"
VENV_DIR="venv"

# 3. Clone repo if missing
if [ ! -d "$REPO_DIR" ]; then
    echo "Cloning Neubond Dashboard repository..."
    git clone https://github.com/Ghassan-Elzobier/Neubond-Clinician-Dashboard-Streamlit.git "$REPO_DIR"
fi

cd "$REPO_DIR"

# 4. Pull latest changes
echo "Pulling latest updates..."
git pull origin main

# 5. Create venv if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    $PYTHON_CMD -m venv "$VENV_DIR"
fi

# 6. Activate venv
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 7. Upgrade pip & install dependencies
echo "Upgrading pip and installing dependencies..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements.txt

# 8. Ensure .env exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env. Please edit with credentials if needed."
fi

# 9. Run app
echo "Launching Streamlit app..."
streamlit run app.py
