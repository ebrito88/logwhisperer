#!/bin/bash

set -e

# ------------------------------
# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
# ------------------------------

# Defaults
DEFAULT_MODEL="mistral"
INSTALL_MODEL="$DEFAULT_MODEL"

# Parse CLI args
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --model) INSTALL_MODEL="$2"; shift ;;
        *) echo -e "${RED}Unknown option: $1${NC}"; exit 1 ;;
    esac
    shift
done

echo -e "${GREEN}Starting LogWhisperer installer...${NC}"
echo "Model to install: $INSTALL_MODEL"

# OS Check
OS_TYPE="$(uname)"
echo "Detected OS: $OS_TYPE"
if [[ "$OS_TYPE" != "Linux" && "$OS_TYPE" != "Darwin" ]]; then
    echo -e "${RED}Unsupported OS: $OS_TYPE${NC}"
    exit 1
fi

# Prerequisite checks
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install it and rerun this script.${NC}"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    echo -e "${RED}curl is not installed. Please install it and rerun this script.${NC}"
    exit 1
fi

# Create venv if not present
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

# Check for pip
if ! command -v pip &> /dev/null; then
    echo -e "${RED}pip is not installed in venv.${NC}"
    exit 1
fi

# Install Python deps
echo "Installing Python dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Ollama if not present
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Installing..."
    if [[ "$OS_TYPE" == "Darwin" ]]; then
        if ! command -v brew &> /dev/null; then
            echo -e "${RED}Homebrew not found. Please install Homebrew or install Ollama manually.${NC}"
            exit 1
        fi
        brew install ollama
    else
        curl -fsSL https://ollama.com/install.sh | sh
    fi
else
    echo "Ollama already installed."
fi

# Wait for Ollama API
echo "Waiting for Ollama to start..."
MAX_ATTEMPTS=10
for i in $(seq 1 $MAX_ATTEMPTS); do
    if curl --silent http://localhost:11434 >/dev/null 2>&1; then
        echo "Ollama is up!"
        break
    fi
    echo "Ollama not ready yet... (${i}/${MAX_ATTEMPTS})"
    sleep 2
done

if ! curl --silent http://localhost:11434 >/dev/null 2>&1; then
    echo -e "${RED}Ollama did not start in time. Please check the installation or service status.${NC}"
    exit 1
fi

# Pull model
echo "Pulling model: $INSTALL_MODEL..."
ollama pull "$INSTALL_MODEL"

# Create default config.yaml if needed
CONFIG_FILE="config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating default config.yaml..."
    cat <<EOF > $CONFIG_FILE
model: $INSTALL_MODEL
source: journalctl
log_file_path: /var/log/syslog
priority: err
entries: 500
timeout: 90
docker_container: my_container
ollama_host: http://localhost:11434
prompt: |
  You are a helpful Linux operations assistant. Analyze the following logs:
  - Identify root causes
  - Summarize key issues
  - Recommend next steps

  LOGS:
  {{LOGS}}
EOF
fi

# Create reports dir
mkdir -p reports
echo "Ensured reports/ directory exists."

# Done
echo ""
echo -e "${GREEN}LogWhisperer installation complete!${NC}"
echo ""
echo "Run 'python3 logwhisperer.py --help' to see CLI options"
echo ""
echo "To activate your environment and run:"
echo "   source venv/bin/activate && python3 logwhisperer.py"
echo ""


