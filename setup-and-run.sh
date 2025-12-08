#!/bin/bash
# setup-and-run.sh
# macOS script to set up virtual environment, install dependencies, pull updates, and launch the app

set -e

echo "--------------------------------------------"
echo "Neubond Dashboard Setup and Run Script"
echo "--------------------------------------------"

# 1. Check Python 3 installation
if ! command -v python3 &>/dev/null
then
    echo "Python3 could not be found. Please install Python 3 first."
    exit 1
fi

# 2. Check Git installation
if ! command -v git &>/dev/null
then
    echo "Git could not be found. Please install Git first."
    exit 1
fi

# 3. Clone repo if it doesn't exist
if [ ! -d "neubond_dashboard" ]; then
    echo "Cloning Neubond Dashboard repository..."
    git clone https://github.com/your-username/neubond_dashboard.git
fi

cd neubond_dashboard

# 4. Pull latest changes
echo "Pulling latest updates from Git..."
git pull origin main

# 5. Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# 6. Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# 7. Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# 8. Install/update dependencies
echo "Installing/updating dependencies..."
pip install -r requirements.txt

# 9. Ensure .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your Supabase credentials or other settings if needed."
fi

# 10. Run the app
echo "Launching Streamlit app..."
streamlit run app.py
