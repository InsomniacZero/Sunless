#!/usr/bin/env python3
"""
Janitor AI x Gemini Proxy - Cloud Tunnel Manager
================================================
Exposes local port 5000 securely to the public internet (HTTPS) so friends
can use Janitor AI on their phone, tablet, or browser without localhost limits.
Supports Android (Termux), Linux, macOS, and Windows with architecture self-healing.
"""

import io
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Dict, Optional, Union

import httpx

MODULE_DIR = Path(__file__).resolve().parent
ROOT_DIR = MODULE_DIR.parent
BIN_DIR = ROOT_DIR / "bin"
DATA_DIR = ROOT_DIR / "data"
NGROK_CONFIG_PATH = DATA_DIR / "ngrok.yml"
NGROK_PID_FILE = DATA_DIR / "tunnel.pid"
NGROK_WEB_PORT = 4041
NGROK_INSPECT_URL = f"http://127.0.0.1:{NGROK_WEB_PORT}/api/tunnels"
DEFAULT_PORT = 5000


def is_termux() -> bool:
    """Return True if running inside Termux on Android."""
    prefix = os.environ.get("PREFIX", "")
    return "termux" in prefix.lower() or os.path.isdir("/data/data/com.termux")


def is_binary_runnable(bin_path: Union[str, Path]) -> bool:
    """Verify that a binary can actually be executed without [Errno 8] Exec format error."""
    try:
        res = subprocess.run([str(bin_path), "version"], capture_output=True, text=True, timeout=4)
        return res.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def get_device_arch() -> str:
    """Detect CPU and userland architecture (64-bit vs 32-bit)."""
    is_64bit = sys.maxsize > 2**32
    machine = platform.machine().lower()

    if is_termux():
        try:
            res = subprocess.run(["dpkg", "--print-architecture"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0:
                darch = res.stdout.strip().lower()
                if darch in ("arm64", "aarch64"):
                    return "arm64"
                elif darch in ("arm", "armhf", "armeabi", "armeabi-v7a"):
                    return "arm"
                elif darch in ("amd64", "x86_64"):
                    return "amd64"
                elif darch in ("i686", "x86", "i386"):
                    return "386"
        except Exception:
            pass

    if "aarch64" in machine or "arm64" in machine or "armv8" in machine:
        return "arm64" if is_64bit else "arm"
    elif "arm" in machine:
        return "arm"
    elif "x86_64" in machine or "amd64" in machine:
        return "amd64" if is_64bit else "386"
    return "arm64" if (is_64bit and ("arm" in machine or "aarch" in machine)) else machine


def get_ngrok_bin_path() -> Optional[str]:
    """Find a verified, runnable ngrok binary on the system or in local bin/."""
    bin_name = "ngrok.exe" if sys.platform == "win32" else "ngrok"
    candidates = []

    # 1. System PATH
    found = shutil.which("ngrok") or shutil.which("ngrok.exe")
    if found:
        candidates.append(found)

    # 2. Termux prefix
    prefix = os.environ.get("PREFIX")
    if prefix:
        candidates.append(str(Path(prefix) / "bin" / bin_name))

    # 3. Local proxy bin/ directory
    candidates.append(str(BIN_DIR / bin_name))

    # 4. User home directories
    home = Path.home()
    candidates.append(str(home / ".local" / "bin" / bin_name))
    candidates.append(str(home / "bin" / bin_name))

    for cand in candidates:
        if cand and os.path.isfile(cand):
            if is_binary_runnable(cand):
                return cand
    return None


def download_and_extract_ngrok(target_dir: Union[str, Path]) -> Optional[str]:
    """Auto-download official ngrok binary for current OS and architecture."""
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    bin_name = "ngrok.exe" if sys.platform == "win32" else "ngrok"
    out_bin = target_dir / bin_name

    plat = sys.platform
    arch = get_device_arch()

    # Determine archive URL
    if plat == "win32":
        ngrok_arch = "windows-amd64" if (arch == "amd64" or sys.maxsize > 2**32) else "windows-386"
        url = f"https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-{ngrok_arch}.zip"
        is_zip = True
    elif plat == "darwin":
        ngrok_arch = "darwin-arm64" if ("arm" in arch or "aarch" in arch) else "darwin-amd64"
        url = f"https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-{ngrok_arch}.zip"
        is_zip = True
    else:  # Linux / Android
        ngrok_arch = "linux-arm64" if arch == "arm64" else ("linux-arm" if arch == "arm" else "linux-amd64")
        url = f"https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-{ngrok_arch}.tgz"
        is_zip = False

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 JanitorProxy/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()

        if is_zip:
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                for member in zf.namelist():
                    if member.endswith(bin_name):
                        with zf.open(member) as sf, open(out_bin, "wb") as df:
                            shutil.copyfileobj(sf, df)
                        break
        else:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
                for member in tf.getmembers():
                    if member.name.endswith(bin_name) or member.name == "ngrok":
                        f = tf.extractfile(member)
                        if f:
                            with open(out_bin, "wb") as df:
                                shutil.copyfileobj(f, df)
                            break

        if out_bin.exists():
            out_bin.chmod(0o755)
            if is_binary_runnable(out_bin):
                return str(out_bin)
    except Exception:
        pass
    return None


def get_public_url() -> Optional[str]:
    """Query local ngrok client API to retrieve active public HTTPS URL."""
    try:
        with httpx.Client(timeout=2.0) as client:
            res = client.get(NGROK_INSPECT_URL)
            if res.status_code == 200:
                data = res.json()
                tunnels = data.get("tunnels", [])
                for t in tunnels:
                    url = t.get("public_url", "")
                    if url.startswith("https://"):
                        return url
                if tunnels:
                    return tunnels[0].get("public_url")
    except Exception:
        pass
    return None


def is_tunnel_running() -> bool:
    """Check if ngrok tunnel daemon is active and responsive."""
    return get_public_url() is not None


def set_authtoken(token: str) -> bool:
    """Save ngrok authtoken into Sunless isolated config."""
    clean_tok = token.strip()
    if not clean_tok:
        return False
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cfg_content = f'version: "2"\nauthtoken: {clean_tok}\nweb_addr: 127.0.0.1:{NGROK_WEB_PORT}\n'
    try:
        with open(NGROK_CONFIG_PATH, "w") as f:
            f.write(cfg_content)
        return True
    except Exception:
        return False


def start_tunnel(port: int = DEFAULT_PORT) -> Dict[str, Any]:
    """Start background ngrok tunnel process forwarding port on dedicated web port 4041."""
    existing_url = get_public_url()
    if existing_url:
        return {"running": True, "url": existing_url, "already_running": True}

    ngrok_bin = get_ngrok_bin_path()
    if not ngrok_bin:
        ngrok_bin = download_and_extract_ngrok(BIN_DIR)

    if not ngrok_bin or not os.path.isfile(ngrok_bin):
        return {
            "running": False,
            "error": "Ngrok binary not found. Run 'Install Ngrok' in the menu or install ngrok on your system.",
        }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [ngrok_bin, "http", str(port), "--log=stdout"]
    if NGROK_CONFIG_PATH.exists():
        cmd.extend(["--config", str(NGROK_CONFIG_PATH)])

    try:
        if sys.platform == "win32":
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
        else:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

        try:
            with open(NGROK_PID_FILE, "w") as f:
                f.write(str(proc.pid))
        except Exception:
            pass

        # Wait up to 6 seconds for tunnel to register
        for _ in range(12):
            time.sleep(0.5)
            url = get_public_url()
            if url:
                return {"running": True, "url": url, "pid": proc.pid}

        return {"running": False, "error": "Tunnel process started but timed out waiting for public URL."}
    except Exception as e:
        return {"running": False, "error": str(e)}


def stop_tunnel() -> bool:
    """Stop active Sunless ngrok tunnel process without touching Singularity."""
    stopped = False
    if NGROK_PID_FILE.exists():
        try:
            pid = int(NGROK_PID_FILE.read_text().strip())
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, timeout=5)
            else:
                os.kill(pid, 15)
            stopped = True
        except Exception:
            pass
        finally:
            try:
                NGROK_PID_FILE.unlink(missing_ok=True)
            except Exception:
                pass

    if not sys.platform == "win32":
        try:
            subprocess.run(["pkill", "-f", f"127.0.0.1:{NGROK_WEB_PORT}"], capture_output=True, timeout=5)
            stopped = True
        except Exception:
            pass
    return stopped
