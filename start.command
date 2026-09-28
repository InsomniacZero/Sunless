#!/usr/bin/env bash
# ==============================================================================
# Sunless - macOS 1-Click Interactive Terminal Launcher
# Double-clickable .command script for macOS
# ==============================================================================

set -e

# Always change to the script's directory when launched from Finder
cd "$(dirname "$0")"

# Execute the main start script
exec bash ./start.sh "$@"
