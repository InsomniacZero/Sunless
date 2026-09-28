<p align="center">
  <img src="logo.svg" width="120" alt="Sunless Logo">
</p>

<h1 align="center">🌌 Sunless</h1>

<p align="center">
  <strong>Unlimited, free Gemini Roleplay gateway for Janitor AI.</strong><br/>
  Zero API keys. Zero subscriptions. Multi-account stacking. Runs anywhere in 5 seconds.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux%20%7C%20Android-green" alt="Cross-Platform">
  <img src="https://img.shields.io/badge/license-MIT-orange" alt="MIT License">
</p>

---

## ✨ Features

- **🎭 Built for Janitor AI Roleplay** — Seamlessly parses character definitions, lorebooks, scenarios, and multi-turn dialogue.
- **⚡ Frontier Gemini Models** — Including 3.8 Flash, 3.7 Flash, 3.5 Flash, 3.1 Pro, and their thinking variants.
- **🧠 Thinking Mode** — Reasoning models output `<think>` tags showing their internal chain-of-thought before responding.
- **🔍 Live Web Search** — Toggle real-time DuckDuckGo search grounding for up-to-date world knowledge in roleplay.
- **🍪 Multi-Account Stacking** — Add multiple free Google accounts. Auto-rotates when one gets rate-limited.
- **✨ Glassmorphic Web UI** — Beautiful Claude-style control center at `http://localhost:5000` with cookie stacker, model selector, and tunnel manager.
- **📱 Phone & Remote Access** — Integrated 1-click cloud tunnel (ngrok) for phone/tablet access.
- **🧹 Clean Output** — Filters Google's citation chips, search artifacts, and placeholder tags automatically.
- **🚀 Lightweight & Instant** — Pure Python, zero Rust compilation. Installs in ~5 seconds everywhere.

---

## ⚡ Quick Start

### 🪟 Windows
1. Install [Python 3.10+](https://www.python.org/downloads/) — **check "Add python.exe to PATH"** during install.
2. Double-click **`start.bat`**.

### 🍏 macOS
Double-click **`start.command`** in Finder, or run:
```bash
./start.command
```

### 🐧 Linux
```bash
./start.sh
```

### 📱 Android (Termux)
```bash
pkg update && pkg install python -y
cd Sunless
bash start.sh
```

---

### 🌟 Global `nephis` Command
After the first launch, Sunless registers a global **`nephis`** command. From any directory:
```bash
nephis
```
Boots the proxy instantly without navigating to the project folder.

---

## 🔑 Getting Your Gemini Cookie (30 Seconds)

1. Open [gemini.google.com](https://gemini.google.com) and sign in.
2. Press **F12** → open Developer Tools → **Network** tab.
3. Send any message in Gemini (e.g. *"hello"*).
4. Click on **`StreamGenerate`** or **`batchexecute`** in the request list.
5. Under **Request Headers**, find **`Cookie:`** → right-click → **Copy value**.
6. Paste into the proxy:
   - **Terminal**: Select `[2] Account Manager` → `[1] Add New Account`
   - **Web UI**: Open `http://localhost:5000` → Cookie Stacker panel

> 💡 **Pro-Tip**: Paste cookies from 2–3 different Google accounts. The proxy auto-rotates if one hits a cooldown!

---

## 🤖 Connecting to Janitor AI

1. Start the proxy (`./start.sh` or `start.bat`)
2. Open [janitorai.com](https://janitorai.com) → any character → **API Settings**

| Setting | Value |
|---|---|
| **API Architecture** | `OpenAI` |
| **Reverse Proxy URL** | `http://localhost:5000/v1` |
| **API Key** | `anything` (e.g. `gemini-rp`) |
| **Model** | `gemini-3.8-flash` (recommended) |
| **Context Size** | `16384` – `32768` |
| **Max Output Tokens** | `800` – `1200` |
| **Temperature** | `0.85` – `1.05` |

---

## 🌐 Phone / Tablet Access

1. In the proxy terminal, choose **`[5] Cloud Tunnel Control`** → **`[1] Start Public Tunnel`**.
2. Copy the generated URL (e.g. `https://xxxx-xx-xx.ngrok-free.app/v1`).
3. Paste it into Janitor AI's **Reverse Proxy URL** on your phone.

> Requires a free [ngrok account](https://dashboard.ngrok.com/signup) and authtoken (set via menu option `[2]`).

---

## 🛠️ Model Reference

| Model ID | Best For | Context | Notes |
|---|---|---|---|
| **`gemini-3.8-flash`** | 🏆 **Recommended**. Ultra-fast agentic reasoning, vivid prose. | 1M tokens | Default model |
| `gemini-3.8-flash-thinking` | Complex multi-character scenarios with reasoning reflection. | 1M tokens | Outputs `<think>` tags |
| `gemini-3.7-flash` | Fast frontier inference for low-latency dialogue. | 1M tokens | |
| `gemini-3.7-flash-thinking` | CoT reasoning for intricate world scenarios. | 1M tokens | Outputs `<think>` tags |
| `gemini-3.5-flash` | Reliable fast dialogue. | 1M tokens | |
| `gemini-3.5-flash-lite` | Sub-second responses for quick chat turns. | 1M tokens | Lightweight |
| `gemini-3.1-pro` | Deepest reasoning, immaculate prose, richest worldbuilding. | 2M tokens | Slowest but best quality |
| `gemini-3.1-pro-thinking` | Flagship thinking for multi-layer storytelling. | 2M tokens | Outputs `<think>` tags |

---

## 🗂️ Project Structure

```
Sunless/
├── start.sh             ← Linux / macOS / Termux launcher
├── start.bat            ← Windows 1-click launcher
├── start.command        ← macOS Finder double-click launcher
├── nephis               ← Global CLI shortcut (Unix)
├── requirements.txt     ← Pure Python dependencies
├── proxy/               ← Core Python package
│   ├── cli.py           ← Terminal interactive menu & server launcher
│   ├── server.py        ← Starlette gateway (OpenAI-compatible API)
│   ├── gemini.py        ← Gemini Web2API engine (batchexecute RPC)
│   ├── db.py            ← SQLite credential vault & settings
│   ├── tunnel.py        ← ngrok tunnel manager (cross-platform)
│   └── search.py        ← DuckDuckGo live search grounding
├── static/              ← Web UI assets (glassmorphic control center)
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   └── tokens.css
├── data/                ← Runtime data (auto-created, gitignored)
│   └── ngrok.yml        ← Tunnel config (set your authtoken here)
└── bin/                 ← ngrok binary (auto-downloaded)
```

---

## ❓ FAQ

**Can Google ban my account?**
> No. Google does not ban accounts for web chat usage. At worst, an account may receive a temporary cooldown (minutes to an hour). Having 2+ stacked accounts prevents any downtime.

**Can I use this without a cookie?**
> Yes — the proxy has guest-mode fallback, but Google heavily restricts guest sessions. Adding a cookie takes 30 seconds and gives full access.

**Can I run this directly on my Android phone?**
> Yes! Install [Termux](https://termux.dev), run `bash start.sh`, and use `http://localhost:5000/v1` as your API URL.

**What's the `<think>` output in thinking models?**
> Thinking models show their internal reasoning inside `<think>...</think>` tags before the actual response. This helps produce more nuanced roleplay for complex scenarios.

---

## 📄 License

MIT License — Free to use, share, and modify.
