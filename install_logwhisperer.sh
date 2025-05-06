#!/bin/bash

set -e

# Defaults
DEFAULT_MODEL="mistral"
INSTALL_MODEL="$DEFAULT_MODEL"

# Parse --model argument
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --model) INSTALL_MODEL="$2"; shift ;;
        *) echo "Unknown option: $1" && exit 1 ;;
    esac
    shift
done

echo "Starting LogWhisperer installer..."
echo "Model to install: $INSTALL_MODEL"

# 🧪 Check OS
OS_TYPE="$(uname)"
echo "Detected OS: $OS_TYPE"
if [[ "$OS_TYPE" != "Linux" && "$OS_TYPE" != "Darwin" ]]; then
    echo "Unsupported OS: $OS_TYPE"
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it and rerun this script."
    exit 1
fi

# Create venv
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

# Check for pip
if ! command -v pip &> /dev/null; then
    echo "pip is not installed in venv."
    exit 1
fi

# Install Python deps
echo "Installing Python dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Ollama if not present
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama already installed."
fi

# Pull requested model
echo "Pulling model: $INSTALL_MODEL..."
ollama pull "$INSTALL_MODEL"

# Create default config.yaml if needed
CONFIG_FILE="config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating default config.yaml..."
    cat <<EOF > $CONFIG_FILE
source: journalctl
log_file_path: /var/log/syslog
priority: err
entries: 500
EOF
fi

#  Create reports dir
mkdir -p reports
echo "Ensured reports/ directory exists."

#  Done
echo ""
echo "LogWhisperer installation complete!"
echo ""
echo "Run 'python3 logwhisperer.py --help' to see CLI options"
echo ""
echo "To activate your environment and run:"
echo "   source venv/bin/activate && python3 logwhisperer.py"
echo ""

