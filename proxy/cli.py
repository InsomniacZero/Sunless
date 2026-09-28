#!/usr/bin/env python3
"""
Janitor AI x Gemini Proxy - Interactive Terminal CLI & Control Center
=====================================================================
A clean, self-contained terminal interface for managing the Janitor AI proxy,
stacking multiple Google accounts, inspecting live requests, and toggling tunnels.
Designed for effortless sharing with friends on Windows, Mac, Linux, and Android.
"""

import asyncio
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure parent directory is in sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from proxy import db, gemini, server, tunnel

# -------------------------------------------------------------------
# ANSI Colors & Formatting
# -------------------------------------------------------------------
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RED = "\033[91m"
BLUE = "\033[94m"
WHITE = "\033[97m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    print(f"{CYAN}{BOLD}")
    print(" ╔═══════════════════════════════════════════════════════════════════╗")
    print(" ║                         🌌 SUNLESS                                ║")
    print(" ║        High-Speed Gemini Roleplay Gateway • 100% Free             ║")
    print(" ╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{RESET}")


def get_current_port() -> int:
    val = db.get_setting("port", "5000")
    try:
        return int(val)
    except Exception:
        return 5000


def get_current_model() -> str:
    return db.get_setting("default_model", "gemini-3.8-flash")


# -------------------------------------------------------------------
# Views & Submenus
# -------------------------------------------------------------------

def show_cookie_guide():
    """Step-by-step walkthrough for non-technical users."""
    clear_screen()
    print_banner()
    print(f"{YELLOW}{BOLD}📖 HOW TO GET YOUR GEMINI COOKIE IN 30 SECONDS:{RESET}\n")
    print(f" {BOLD}1.{RESET} Open {CYAN}https://gemini.google.com{RESET} in your browser and sign into Google.")
    print(f" {BOLD}2.{RESET} Press {BOLD}F12{RESET} (or right-click anywhere -> {BOLD}Inspect{RESET}) to open Developer Tools.")
    print(f" {BOLD}3.{RESET} Click on the {BOLD}Network{RESET} tab at the top.")
    print(f" {BOLD}4.{RESET} In Gemini chat, send any quick message (e.g. \"hi\").")
    print(f" {BOLD}5.{RESET} In the Network tab list, click on {CYAN}StreamGenerate{RESET} or {CYAN}batchexecute{RESET}.")
    print(f" {BOLD}6.{RESET} In the panel that opens, look under {BOLD}Request Headers{RESET} for {BOLD}Cookie{RESET}.")
    print(f" {BOLD}7.{RESET} Right-click on the {BOLD}Cookie{RESET} line -> {BOLD}Copy value{RESET}.\n")
    print(f" {DIM}💡 Tip: You can stack multiple free Google accounts so you never hit rate limits!{RESET}\n")
    input(f"{DIM}Press Enter to return to menu...{RESET}")


def account_manager_menu():
    """Interactive management for stacking multiple Google accounts."""
    while True:
        clear_screen()
        print_banner()
        print(f"{BOLD}🔐 GOOGLE GEMINI ACCOUNT VAULT{RESET}\n")

        accounts = db.get_accounts()
        if not accounts:
            print(f" {YELLOW}⚠️  No accounts currently stacked.{RESET}")
            print(f" {DIM}The proxy will attempt guest mode, which has strict rate limits.{RESET}\n")
        else:
            print(f" {BOLD}{'ID':<4} {'Name':<18} {'Status':<14} {'Full Bundle':<14} {'Errors':<8}{RESET}")
            print(f" {DIM}{'-'*62}{RESET}")
            for acc in accounts:
                stat_col = GREEN if acc['status'] == 'active' else RED
                bundle_str = f"{GREEN}Yes (Full){RESET}" if (acc['has_psid'] and acc['has_psidts']) else f"{YELLOW}Partial{RESET}"
                print(f" {acc['id']:<4} {acc['name']:<18} {stat_col}{acc['status']:<14}{RESET} {bundle_str:<14} {acc['error_count']:<8}")
            print()

        print(f" {CYAN}[1]{RESET} Add New Google Account (Paste Cookie)")
        print(f" {CYAN}[2]{RESET} Delete an Account")
        print(f" {CYAN}[3]{RESET} Reactivate All Accounts (Reset error counts)")
        print(f" {CYAN}[4]{RESET} Cookie Extraction Guide")
        print(f" {CYAN}[0]{RESET} Back to Main Menu\n")

        choice = input(f"{BOLD}Select an option [0-4]: {RESET}").strip()
        if choice == "0":
            break
        elif choice == "1":
            print(f"\n{BOLD}Paste your Gemini Cookie Header below:{RESET}")
            print(f"{DIM}(Right-click to paste in terminal, then press Enter):{RESET}")
            raw = input().strip()
            if not raw:
                print(f"{RED}Empty input cancelled.{RESET}")
                time.sleep(1)
                continue
            name_input = input(f"{BOLD}Optional Account Nickname (e.g. 'Main Google', 'Alt #1'): {RESET}").strip()
            res = db.add_account(raw, name=name_input)
            if res.get("success"):
                p = res.get("parsed", {})
                print(f"\n{GREEN}✓ Successfully saved {res.get('name')}!{RESET}")
                if not (p.get("has_psid") and p.get("has_psidts")):
                    print(f"{YELLOW}Notice: For zero-interruption RP, ensure you copy the entire Cookie header including __Secure-1PSIDTS.{RESET}")
            else:
                print(f"\n{RED}✗ Failed to add account: {res.get('error')}{RESET}")
            time.sleep(2)
        elif choice == "2":
            if not accounts:
                continue
            del_id = input(f"{BOLD}Enter the ID of the account to delete: {RESET}").strip()
            try:
                if db.delete_account(int(del_id)):
                    print(f"{GREEN}✓ Account #{del_id} deleted.{RESET}")
                else:
                    print(f"{RED}Account ID not found.{RESET}")
            except Exception:
                print(f"{RED}Invalid ID.{RESET}")
            time.sleep(1.5)
        elif choice == "3":
            db.reset_account_errors()
            print(f"{GREEN}✓ All accounts reactivated to 'active' status.{RESET}")
            time.sleep(1.5)
        elif choice == "4":
            show_cookie_guide()


def test_roleplay_chat():
    """Live interactive chat test in terminal."""
    clear_screen()
    print_banner()
    model = get_current_model()
    print(f"{YELLOW}{BOLD}🧪 TEST ROLEPLAY COMPLETION{RESET}")
    print(f" Active Model: {CYAN}{model}{RESET}\n")

    default_prompt = "*smiles warmly, leaning across the counter* Good evening. What brings you to this quiet corner of the realm tonight?"
    print(f"{DIM}Enter a test roleplay action or press Enter for default:{RESET}")
    print(f"{DIM}Default: \"{default_prompt}\"{RESET}\n")
    user_input = input(f"{BOLD}Your input: {RESET}").strip()
    if not user_input:
        user_input = default_prompt

    messages = [
        {"role": "system", "content": "You are Lyra, a charismatic tavern keeper in a fantasy realm. Respond in vivid narrative roleplay with dialogue in quotes and actions in asterisks."},
        {"role": "user", "content": user_input},
    ]

    print(f"\n{CYAN}Streaming response from Gemini Web...{RESET}\n")
    print(f"{MAGENTA}{BOLD}[Lyra]:{RESET} ", end="", flush=True)

    async def run_test():
        count = 0
        async for chunk in gemini.stream_gemini_chat(model=model, messages=messages, stream=True):
            choices = chunk.get("choices", [])
            if choices:
                delta = choices[0].get("delta", {})
                c = delta.get("content")
                if c:
                    print(c, end="", flush=True)
                    count += 1
        print("\n")
        return count

    try:
        toks = asyncio.run(run_test())
        if toks > 0:
            print(f"{GREEN}✓ Test successful! Your Gemini session is active and roleplay-ready.{RESET}\n")
        else:
            print(f"{RED}✗ Received empty response. Check if your account cookie is valid.{RESET}\n")
    except Exception as e:
        print(f"\n{RED}✗ Error during test: {str(e)}{RESET}\n")

    input(f"{DIM}Press Enter to return to menu...{RESET}")


def tunnel_menu():
    """Configure public ngrok tunnel for phone/remote Janitor AI usage."""
    port = get_current_port()
    while True:
        clear_screen()
        print_banner()
        print(f"{BOLD}🌐 CLOUD TUNNEL (FOR PHONE / TABLET / REMOTE JANITOR AI){RESET}\n")

        is_running = tunnel.is_tunnel_running()
        url = tunnel.get_public_url()

        if is_running and url:
            print(f" Tunnel Status: {GREEN}{BOLD}● ACTIVE & FORWARDING{RESET}")
            print(f" Public URL:    {CYAN}{BOLD}{url}{RESET}")
            print(f" Janitor URL:   {MAGENTA}{BOLD}{url}/v1{RESET}\n")
        else:
            print(f" Tunnel Status: {DIM}○ Inactive (Local-only mode){RESET}\n")

        print(f" {CYAN}[1]{RESET} {'Stop Tunnel' if is_running else 'Start Public Tunnel'}")
        print(f" {CYAN}[2]{RESET} Set Ngrok Authtoken")
        print(f" {CYAN}[3]{RESET} Check / Re-download Ngrok Binary")
        print(f" {CYAN}[0]{RESET} Back to Main Menu\n")

        choice = input(f"{BOLD}Select an option [0-3]: {RESET}").strip()
        if choice == "0":
            break
        elif choice == "1":
            if is_running:
                tunnel.stop_tunnel()
                print(f"{YELLOW}Tunnel stopped.{RESET}")
                time.sleep(1)
            else:
                print(f"{CYAN}Starting public tunnel on port {port}...{RESET}")
                res = tunnel.start_tunnel(port=port)
                if res.get("running"):
                    print(f"\n{GREEN}✓ Public tunnel online!{RESET}")
                    print(f"Janitor AI URL: {MAGENTA}{res.get('url')}/v1{RESET}")
                else:
                    print(f"\n{RED}✗ Failed to start tunnel: {res.get('error')}{RESET}")
                    print(f"{DIM}Note: Ngrok requires a free account authtoken. Select [2] to set one.{RESET}")
                time.sleep(3)
        elif choice == "2":
            print(f"\n{BOLD}Enter your Ngrok Authtoken:{RESET}")
            print(f"{DIM}(Get one free at https://dashboard.ngrok.com/get-started/your-authtoken){RESET}")
            tok = input(f"Token: ").strip()
            if tok:
                if tunnel.set_authtoken(tok):
                    print(f"{GREEN}✓ Authtoken saved successfully!{RESET}")
                else:
                    print(f"{RED}✗ Failed to save authtoken.{RESET}")
            time.sleep(2)
        elif choice == "3":
            print(f"{CYAN}Validating ngrok binary for current OS & architecture...{RESET}")
            path = tunnel.get_ngrok_bin_path()
            if path:
                print(f"{GREEN}✓ Found runnable ngrok binary: {path}{RESET}")
            else:
                print(f"{YELLOW}Downloading official ngrok binary...{RESET}")
                dl = tunnel.download_and_extract_ngrok(tunnel.BIN_DIR)
                if dl:
                    print(f"{GREEN}✓ Successfully installed ngrok!{RESET}")
                else:
                    print(f"{RED}✗ Could not auto-download. Please install ngrok manually.{RESET}")
            time.sleep(2)


def select_model_menu():
    """Switch default roleplay model."""
    clear_screen()
    print_banner()
    curr = get_current_model()
    print(f"{BOLD}🎭 CHOOSE DEFAULT GEMINI ROLEPLAY MODEL:{RESET}\n")

    models_list = list(gemini.GEMINI_MODELS.items())
    for idx, (m_id, cfg) in enumerate(models_list, 1):
        active_tag = f" {GREEN}(Active){RESET}" if m_id == curr else ""
        print(f" {CYAN}[{idx}]{RESET} {BOLD}{cfg['name']}{RESET}{active_tag}")
        print(f"     {DIM}{cfg['description']} • {cfg['context']}{RESET}")

    print(f"\n {CYAN}[0]{RESET} Cancel\n")
    choice = input(f"{BOLD}Select model [1-{len(models_list)}]: {RESET}").strip()
    try:
        idx = int(choice)
        if 1 <= idx <= len(models_list):
            selected = models_list[idx - 1][0]
            db.set_setting("default_model", selected)
            print(f"\n{GREEN}✓ Default model set to: {selected}{RESET}")
            time.sleep(1.5)
    except Exception:
        pass


def change_port_menu():
    """Configure server port."""
    clear_screen()
    print_banner()
    curr = get_current_port()
    print(f"{BOLD}⚙️  PROXY PORT CONFIGURATION{RESET}\n")
    print(f" Current Port: {CYAN}{curr}{RESET}")
    print(f"{DIM}Standard Janitor AI proxy port is 5000.{RESET}\n")
    new_p = input(f"Enter new port (or press Enter to keep {curr}): ").strip()
    if new_p:
        try:
            p_int = int(new_p)
            if 1000 <= p_int <= 65535:
                db.set_setting("port", str(p_int))
                print(f"{GREEN}✓ Port updated to {p_int}. Restart server to apply.{RESET}")
            else:
                print(f"{RED}Invalid port range (1000-65535).{RESET}")
        except Exception:
            print(f"{RED}Invalid port number.{RESET}")
        time.sleep(1.5)


# -------------------------------------------------------------------
# Server Runner
# -------------------------------------------------------------------

def start_server_foreground():
    """Launch the proxy gateway with live telemetry logging."""
    clear_screen()
    print_banner()
    port = get_current_port()
    model = get_current_model()
    stats = db.get_stats()
    tunnel_url = tunnel.get_public_url()

    print(f" {GREEN}{BOLD}● GATEWAY SERVER IS ONLINE{RESET}\n")

    print(" ┌─────────────────────────────────────────────────────────────────┐")
    print(f" │ {BOLD}Janitor AI Configuration Settings:{RESET}                              │")
    print(" ├─────────────────────────────────────────────────────────────────┤")
    print(f" │ • {BOLD}API URL (Local PC):{RESET}   {CYAN}http://localhost:{port}/v1{RESET}               │")
    if tunnel_url:
        print(f" │ • {BOLD}API URL (Phone/Web):{RESET}  {MAGENTA}{tunnel_url}/v1{RESET}       │")
    print(f" │ • {BOLD}Web UI Dashboard:{RESET}    {GREEN}http://localhost:{port}{RESET}                  │")
    print(f" │ • {BOLD}API Key:{RESET}              {YELLOW}any string (e.g. gemini-rp){RESET}            │")
    print(f" │ • {BOLD}Recommended Model:{RESET}    {WHITE}{BOLD}{model}{RESET}                         │")
    print(" └─────────────────────────────────────────────────────────────────┘\n")

    status_tag = f"{stats['active_accounts']} Active" if stats['active_accounts'] > 0 else "Guest Mode (0 Accounts)"
    print(f" {DIM}Mode: {status_tag} • Press Ctrl+C anytime to stop.{RESET}")
    print(f" {DIM}{'─'*65}{RESET}\n")

    try:
        server.run_server(host="0.0.0.0", port=port, log_level="warning")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Server stopped.{RESET}")


# -------------------------------------------------------------------
# Main Menu & Entry Point
# -------------------------------------------------------------------

def interactive_menu():
    """Interactive management menu."""
    while True:
        clear_screen()
        print_banner()

        port = get_current_port()
        model = get_current_model()
        stats = db.get_stats()
        tunnel_url = tunnel.get_public_url()

        # Status HUD
        print(f"  {BOLD}Local Endpoint:{RESET}  {CYAN}http://127.0.0.1:{port}/v1{RESET}")
        print(f"  {BOLD}Web Dashboard:{RESET}   {GREEN}http://127.0.0.1:{port}{RESET}")
        if tunnel_url:
            print(f"  {BOLD}Public Tunnel:{RESET}   {MAGENTA}{tunnel_url}/v1{RESET} {GREEN}● Online{RESET}")
        else:
            print(f"  {BOLD}Public Tunnel:{RESET}   {DIM}○ Offline (Local-only){RESET}")

        acc_str = f"{GREEN}{stats['active_accounts']} Active{RESET}" if stats['active_accounts'] > 0 else f"{YELLOW}0 Accounts (Guest){RESET}"
        print(f"  {BOLD}Google Vault:{RESET}    {acc_str}")
        print(f"  {BOLD}Active Model:{RESET}    {WHITE}{BOLD}{model}{RESET}\n")

        print(" ┌────────────────────────────────────────────────────────┐")
        print(" │                      MAIN MENU                         │")
        print(" ├────────────────────────────────────────────────────────┤")
        print(f" │  {CYAN}[1]{RESET} {BOLD}Start Proxy Server{RESET} (Live Janitor AI Gateway)       │")
        print(f" │  {CYAN}[2]{RESET} Account Manager (Add/Remove Google Accounts)     │")
        print(f" │  {CYAN}[3]{RESET} How to Get Cookie (30-Second Guide)             │")
        print(f" │  {CYAN}[4]{RESET} Test Roleplay Chat (In-Terminal Verification)   │")
        print(f" │  {CYAN}[5]{RESET} Cloud Tunnel Control (For Phones & Tablets)      │")
        print(f" │  {CYAN}[6]{RESET} Select Gemini Model (2.5 Pro, Flash, Thinking)  │")
        print(f" │  {CYAN}[7]{RESET} Change Port (Current: {port})                       │")
        print(f" │  {CYAN}[0]{RESET} Exit                                             │")
        print(" └────────────────────────────────────────────────────────┘\n")

        choice = input(f"{BOLD}Enter choice [0-7]: {RESET}").strip()
        if choice == "1":
            start_server_foreground()
        elif choice == "2":
            account_manager_menu()
        elif choice == "3":
            show_cookie_guide()
        elif choice == "4":
            test_roleplay_chat()
        elif choice == "5":
            tunnel_menu()
        elif choice == "6":
            select_model_menu()
        elif choice == "7":
            change_port_menu()
        elif choice == "0":
            tunnel.stop_tunnel()
            print(f"\n{CYAN}Goodbye! Enjoy your Janitor AI roleplay! 🌌{RESET}\n")
            sys.exit(0)


def main():
    db.init_db()
    args = sys.argv[1:]
    if not args or args[0] in ("start", "run", "serve"):
        # Typing `nephis` starts the server directly and quickly with zero prompts!
        start_server_foreground()
    elif args[0] in ("menu", "--menu", "-m"):
        interactive_menu()
    elif args[0] in ("tunnel",):
        tunnel_menu()
    elif args[0] in ("accounts", "account"):
        account_manager_menu()
    elif args[0] in ("test", "chat"):
        test_roleplay_chat()
    elif args[0] in ("model", "models"):
        select_model_menu()
    else:
        # Default fallback to server start
        start_server_foreground()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Terminated.{RESET}\n")
        sys.exit(0)
