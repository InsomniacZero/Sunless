<p align="center">
  <img src="logo.svg" width="120" alt="Sunless Logo">
</p>

<h1 align="center">🌌 Sunless</h1>

<p align="center">
  <strong>Unlimited, free Gemini Roleplay gateway for Janitor AI.</strong><br/>
  Zero API keys. Zero subscriptions. Runs anywhere in 5 seconds.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux%20%7C%20Android-green" alt="Cross-Platform">
  <img src="https://img.shields.io/badge/license-MIT-orange" alt="MIT License">
</p>

---

## ✨ Features

- **🎭 Built for Janitor AI Roleplay** — Seamlessly parses character definitions, lorebooks, scenarios, and multi-turn dialogue.
- **⚡ Frontier Gemini Models** — 3.8 Flash, 3.7 Flash, 3.5 Flash, 3.1 Pro, and all thinking variants.
- **🧠 Thinking Mode** — Reasoning models output `<think>` tags showing internal chain-of-thought before responding.
- **🔍 Live Web Search** — Toggle real-time search grounding for up-to-date world knowledge in roleplay.
- **✨ Glassmorphic Web UI** — Beautiful control center at `http://localhost:5000` with model selector and tunnel manager.
- **📱 Phone & Remote Access** — Integrated 1-click cloud tunnel (ngrok) for phone/tablet access.
- **🧹 Clean Output** — Filters Google's citation chips, search artifacts, and placeholder tags automatically.
- **🚀 Lightweight & Instant** — Pure Python, zero Rust compilation. Installs in ~5 seconds everywhere.

---

## ⚡ 1-Click Install & Run

Copy-paste **one command** — it downloads Sunless, installs dependencies, and launches the server:

### 🪟 Windows (PowerShell)
```powershell
git clone https://github.com/InsomniacZero/Sunless.git && cd Sunless && .\start.bat
```

### 🍏 macOS
```bash
git clone https://github.com/InsomniacZero/Sunless.git && cd Sunless && ./start.command
```

### 🐧 Linux
```bash
git clone https://github.com/InsomniacZero/Sunless.git && cd Sunless && ./start.sh
```

### 📱 Android (Termux)
```bash
pkg update && pkg install python git -y && git clone https://github.com/InsomniacZero/Sunless.git && cd Sunless && bash start.sh
```

> 🌟 After the first run, just type **`nephis`** from anywhere to start Sunless instantly!

---

## 🤖 Connecting to Janitor AI

1. Start Sunless (see above)
2. Open [janitorai.com](https://janitorai.com) → any character → **API Settings**

| Setting | Value |
|---|---|
| **API Architecture** | `OpenAI` |
| **Reverse Proxy URL** | `http://localhost:5000/v1/chat/completions` |
| **API Key** | `anything` (e.g. `gemini-rp`) |
| **Model** | `gemini-3.8-flash-thinking` (recommended) |
| **Context Size** | `16384` – `32768` |
| **Max Output Tokens** | `0` (unrestricted) |
| **Temperature** | `0.85` – `1.05` |

---

## 🌐 Playing on Your Phone / Tablet (Ngrok Tunnel)

By default, Sunless runs on `localhost` — that means it only works on the same computer. If you want to use Janitor AI on your **phone, tablet, or a different device**, you need to create a **public tunnel** using ngrok. Here's how:

### Step 1: Get a Free Ngrok Account (1 minute, one-time only)
1. Go to **[dashboard.ngrok.com/signup](https://dashboard.ngrok.com/signup)** and sign up (Google/GitHub login works).
2. After signing in, go to **[Your Authtoken](https://dashboard.ngrok.com/get-started/your-authtoken)**.
3. Copy your authtoken (it looks like `2abc123def456_xxxxxxxxx`).

### Step 2: Set Your Authtoken in Sunless (one-time only)
1. Open Sunless terminal menu: run `nephis --menu` (or `./start.sh menu`).
2. Select **`[5] Cloud Tunnel Control`**.
3. Select **`[2] Set Ngrok Authtoken`**.
4. Paste your token and press Enter.

### Step 3: Start the Tunnel
1. In the same Cloud Tunnel menu, select **`[1] Start Public Tunnel`**.
2. Sunless will give you a public URL like:
   ```
   https://abcd-12-34-56.ngrok-free.app
   ```

### Step 4: Use It on Your Phone
1. On your phone, open [janitorai.com](https://janitorai.com) → any character → **API Settings**.
2. Set **Reverse Proxy URL** to your tunnel URL + the path:
   ```
   https://abcd-12-34-56.ngrok-free.app/v1/chat/completions
   ```
3. Set everything else the same as the table above (API Key: `anything`, Model: `gemini-3.8-flash-thinking`, Max Tokens: `0`).
4. Start chatting! 🎉

> ⚠️ **Note**: The ngrok URL changes every time you restart the tunnel. Just copy the new one and update Janitor AI's settings.
> 
> 💡 **Tip**: Keep Sunless running on your PC while you play on your phone. Your phone connects to your PC through the tunnel.

---

## 🛠️ Model Reference

| Model ID | Best For | Context | Notes |
|---|---|---|---|
| **`gemini-3.8-flash-thinking`** | 🏆 **Recommended**. Agentic reasoning with `<think>` reflection. | 1M tokens | Default |
| `gemini-3.8-flash` | Ultra-fast prose, no thinking overhead. | 1M tokens | |
| `gemini-3.7-flash` | Fast frontier inference. | 1M tokens | |
| `gemini-3.7-flash-thinking` | CoT reasoning for intricate scenarios. | 1M tokens | `<think>` tags |
| `gemini-3.5-flash` | Reliable fast dialogue. | 1M tokens | |
| `gemini-3.5-flash-lite` | Sub-second responses for quick turns. | 1M tokens | Lightweight |
| `gemini-3.1-pro` | Deepest reasoning, richest worldbuilding. | 2M tokens | Slowest but best |
| `gemini-3.1-pro-thinking` | Flagship thinking for multi-layer storytelling. | 2M tokens | `<think>` tags |

---

## ❓ FAQ

**Can Google ban my account?**
> No. At worst, an account may receive a temporary cooldown (minutes to an hour). The proxy works in guest mode by default.

**Can I run this directly on my Android phone?**
> Yes! Install [Termux](https://termux.dev), paste the 1-click command above, and use `http://localhost:5000/v1/chat/completions` as your API URL.

**What's the `<think>` output in thinking models?**
> Thinking models show their internal reasoning inside `<think>...</think>` tags before the actual response. This produces more nuanced roleplay for complex scenarios.

---

## 📄 License

MIT License — Free to use, share, and modify.
