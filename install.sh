#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}NVIDIA Stability for All Linux - Installer${NC}"
echo ""

if [[ "$1" == "--python" ]] || [[ "$1" == "-p" ]]; then
    echo "Running Python version..."
    exec sudo python3 "$SCRIPT_DIR/src/nvidia_stability.py"
elif [[ "$1" == "--bash" ]] || [[ "$1" == "-b" ]]; then
    echo "Running Bash version..."
    exec sudo bash "$SCRIPT_DIR/bin/nvidia-stability.sh"
elif [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -p, --python    Run Python version"
    echo "  -b, --bash      Run Bash version"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "If no option is specified, the Python version will be used."
    exit 0
else
    if command -v python3 &> /dev/null; then
        echo "Running Python version..."
        exec sudo python3 "$SCRIPT_DIR/src/nvidia_stability.py"
    else
        echo "Python3 not found, running Bash version..."
        exec sudo bash "$SCRIPT_DIR/bin/nvidia-stability.sh"
    fi
fi
