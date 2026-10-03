#!/usr/bin/env bash
# ==============================================================================
# Janitor AI x Gemini Proxy - Unified Terminal Launcher
# Compatible with Linux, macOS, and Android (Termux)
# ==============================================================================

set -e

# Move to the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Text styles
CYAN='\033[96m'
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

echo -e "${CYAN}${BOLD}"
echo " ╔═══════════════════════════════════════════════════════════════════╗"
echo " ║                         🌌 SUNLESS                                ║"
echo " ║              Gemini Gateway for Janitor AI Roleplay               ║"
echo " ╚═══════════════════════════════════════════════════════════════════╝"
echo -e "${RESET}"

# ── Auto-Update from GitHub ──────────────────────────────────────────────────
# Silently pulls latest changes every startup. Fails gracefully if offline.
if [ -d ".git" ] && command -v git &>/dev/null; then
    # Stash any local runtime changes (e.g. ngrok.yml token edits)
    git stash -q 2>/dev/null || true
    BEFORE=$(git rev-parse HEAD 2>/dev/null)
    git pull --ff-only origin main -q 2>/dev/null || true
    AFTER=$(git rev-parse HEAD 2>/dev/null)
    # Restore user's local changes on top
    git stash pop -q 2>/dev/null || true
    if [ "$BEFORE" != "$AFTER" ]; then
        echo -e "${GREEN}${BOLD} ✓ Auto-updated to latest version!${RESET}"
        echo -e "${DIM}   Changelog: https://github.com/InsomniacZero/Sunless/commits/main${RESET}\n"
    fi
fi

# Check for Python 3
if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null; then
    PY_CMD="python"
else
    echo -e "${RED}✗ Error: Python 3 was not found on your system.${RESET}"
    echo -e "Please install Python 3 (https://www.python.org/downloads/) and retry."
    exit 1
fi

# Detect Termux on Android
IS_TERMUX=false
if [ -n "$PREFIX" ] && [[ "$PREFIX" == *"com.termux"* ]]; then
    IS_TERMUX=true
fi

# Setup Virtual Environment if not inside Termux (Termux manages pure python packages globally)
if [ "$IS_TERMUX" = false ]; then
    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}Creating clean Python virtual environment (.venv)...${RESET}"
        $PY_CMD -m venv .venv || {
            echo -e "${RED}Warning: Could not create venv. Using system Python.${RESET}"
        }
    fi

    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        PY_CMD="python3"
    fi
fi

# Check and install minimal dependencies (pure Python: starlette, uvicorn, httpx)
NEED_INSTALL=false
$PY_CMD -c "import starlette, uvicorn, httpx" 2>/dev/null || NEED_INSTALL=true

if [ "$NEED_INSTALL" = true ]; then
    echo -e "${CYAN}Installing required lightweight packages (takes ~5 seconds)...${RESET}"
    $PY_CMD -m pip install -q -r requirements.txt || {
        echo -e "${YELLOW}Retrying package installation with pip...${RESET}"
        $PY_CMD -m pip install starlette uvicorn httpx
    }
    echo -e "${GREEN}✓ Dependencies verified.${RESET}\n"
fi

# Register global 'nephis' command so user can launch from anywhere
install_global_nephis() {
    local abs_dir="$SCRIPT_DIR"

    # 1. Termux Android
    if [ "$IS_TERMUX" = true ] && [ -d "$PREFIX/bin" ]; then
        cat <<EOF > "$PREFIX/bin/nephis"
#!/usr/bin/env bash
cd "$abs_dir"
exec ./start.sh "\$@"
EOF
        chmod +x "$PREFIX/bin/nephis" 2>/dev/null || true
    fi

    # 2. Linux & macOS ~/.local/bin
    mkdir -p "$HOME/.local/bin" 2>/dev/null || true
    if [ -d "$HOME/.local/bin" ]; then
        cat <<EOF > "$HOME/.local/bin/nephis"
#!/usr/bin/env bash
cd "$abs_dir"
exec ./start.sh "\$@"
EOF
        chmod +x "$HOME/.local/bin/nephis" 2>/dev/null || true
    fi

    # Ensure ~/.local/bin is in PATH for future sessions
    if [ "$IS_TERMUX" = false ]; then
        for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
            if [ -f "$rc" ]; then
                if ! grep -q '.local/bin' "$rc" 2>/dev/null; then
                    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$rc" 2>/dev/null || true
                fi
            fi
        done
    fi
}
install_global_nephis 2>/dev/null || true

# Launch the proxy
exec $PY_CMD -m proxy.cli "$@"
