#!/usr/bin/env python3
"""
Sunless (Janitor AI x Gemini Proxy) - Universal REST & Streaming Gateway
========================================================================
Full Singularity API parity, serving the authentic Claude-style Sunless Web UI,
OpenAI-compatible `/v1/chat/completions`, and multi-account cookie stacker.
Default port: 5000
"""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional

import uvicorn
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response, StreamingResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

from . import db, gemini, tunnel

MODULE_DIR = Path(__file__).resolve().parent
ROOT_DIR = MODULE_DIR.parent
STATIC_DIR = ROOT_DIR / "static"

# ANSI Terminal Colors for sleek telemetry
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def log_telemetry(method: str, path: str, model: str = "", tokens: int = 0, status: str = "200 OK", is_err: bool = False):
    """Print high-visibility terminal log for active Janitor AI requests."""
    t_str = time.strftime("%H:%M:%S")
    stat_color = RED if is_err else GREEN
    m_info = f" {MAGENTA}{model}{RESET}" if model else ""
    tok_info = f" {DIM}(~{tokens} tokens){RESET}" if tokens else ""
    print(f" {DIM}[{t_str}]{RESET} {CYAN}{BOLD}{method}{RESET} {path}{m_info}{tok_info} -> {stat_color}{BOLD}{status}{RESET}")


# -------------------------------------------------------------------
# Static File Handlers
# -------------------------------------------------------------------

async def root_handler(request: Request) -> Response:
    """Serve frontend Web UI index.html, or JSON if requested via API."""
    index_file = STATIC_DIR / "index.html"
    accept = request.headers.get("accept", "")
    if "application/json" in accept and not ("text/html" in accept):
        stats = db.get_stats()
        return JSONResponse({
            "status": "online",
            "service": "Sunless (Janitor AI x Gemini Proxy)",
            "version": "1.0.0",
            "purpose": "Janitor AI Roleplay Reverse Proxy",
            "models": list(gemini.GEMINI_MODELS.keys()),
            "accounts_stacked": stats["total_accounts"],
            "active_accounts": stats["active_accounts"],
            "endpoint": "/v1/chat/completions",
        })

    if index_file.exists():
        return FileResponse(str(index_file))

    stats = db.get_stats()
    return JSONResponse({
        "status": "online",
        "service": "Sunless",
        "version": "1.0.0",
        "models": list(gemini.GEMINI_MODELS.keys()),
    })


async def logo_handler(request: Request) -> Response:
    """Serve authentic brand logo.svg."""
    logo_file = STATIC_DIR / "logo.svg"
    if logo_file.exists():
        return FileResponse(str(logo_file), media_type="image/svg+xml")
    root_logo = ROOT_DIR / "logo.svg"
    if root_logo.exists():
        return FileResponse(str(root_logo), media_type="image/svg+xml")
    return Response(status_code=404)


async def healthz_handler(request: Request) -> Response:
    """Health check for clients & uptime monitors."""
    port = int(db.get_setting("port", "5000"))
    return JSONResponse({"status": "ok", "app": "Sunless", "version": "1.0.0", "port": port})


# -------------------------------------------------------------------
# OpenAI Compatible Endpoints (/v1)
# -------------------------------------------------------------------

async def list_models(request: Request) -> Response:
    """OpenAI-compatible models catalog for Janitor AI."""
    now = int(time.time())
    data = []
    for m_id, cfg in gemini.GEMINI_MODELS.items():
        data.append({
            "id": m_id,
            "object": "model",
            "created": now,
            "owned_by": "google",
            "permission": [],
            "root": m_id,
            "parent": None,
            "name": cfg["name"],
            "description": cfg["description"],
            "context_window": cfg["context"],
            "capabilities": ["chat", "roleplay", "streaming"] + (["reasoning"] if "thinking" in m_id else []),
        })
    log_telemetry("GET", "/v1/models", status="200 OK")
    return JSONResponse({"object": "list", "data": data})


async def chat_completions(request: Request) -> Response:
    """Universal OpenAI router for chat completions."""
    try:
        body = await request.json()
    except Exception:
        body = {}

    model = body.get("model", "gemini-3.8-flash")
    messages = body.get("messages", [])
    is_stream = body.get("stream", False)
    thinking_budget = body.get("thinking_budget")

    web_search = body.get("web_search", False)

    # Check model settings from db
    try:
        m_cfg = json.loads(db.get_setting(f"model_cfg_{model}", "{}"))
        if thinking_budget is None and "thinking_budget" in m_cfg:
            thinking_budget = m_cfg.get("thinking_budget")
    except Exception:
        pass

    custom_cookie = request.headers.get("x-gemini-cookie")

    if is_stream:
        async def stream_generator() -> AsyncIterator[bytes]:
            emitted_tokens = 0
            try:
                async for chunk in gemini.stream_gemini_chat(
                    model=model,
                    messages=messages,
                    cookie_str=custom_cookie,
                    stream=True,
                    thinking_budget=thinking_budget,
                    web_search=web_search,
                ):
                    choices = chunk.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        if "content" in delta:
                            emitted_tokens += len(delta["content"]) // 4
                    yield f"data: {json.dumps(chunk)}\n\n".encode("utf-8")
                yield b"data: [DONE]\n\n"
                log_telemetry("POST", "/v1/chat/completions", model=model, tokens=emitted_tokens, status="200 (Stream Complete)")
            except Exception as e:
                err_chunk = {
                    "id": f"chatcmpl-err-{int(time.time())}",
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "delta": {},
                        "finish_reason": "error",
                    }],
                    "error": {
                        "message": f"Sunless Proxy Stream Error: {str(e)}",
                        "type": "proxy_error",
                    },
                }
                yield f"data: {json.dumps(err_chunk)}\n\n".encode("utf-8")
                yield b"data: [DONE]\n\n"
                log_telemetry("POST", "/v1/chat/completions", model=model, status=f"Error: {str(e)[:30]}", is_err=True)

        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "Access-Control-Allow-Origin": "*",
            },
        )
    else:
        try:
            res = await gemini.generate_gemini_chat(
                model=model,
                messages=messages,
                cookie_str=custom_cookie,
                thinking_budget=thinking_budget,
                web_search=web_search,
            )
            out_tokens = res.get("usage", {}).get("completion_tokens", 0)
            log_telemetry("POST", "/v1/chat/completions", model=model, tokens=out_tokens, status="200 OK")
            return JSONResponse(status_code=200, content=res)
        except Exception as e:
            log_telemetry("POST", "/v1/chat/completions", model=model, status=f"Error: {str(e)[:30]}", is_err=True)
            return JSONResponse(
                status_code=500,
                content={"error": {"message": f"Proxy Error: {str(e)}", "type": "gemini_proxy_error"}},
            )


# -------------------------------------------------------------------
# Singularity Parity Management APIs (/api)
# -------------------------------------------------------------------

async def api_get_services(request: Request) -> Response:
    """Return fleet daemons (Sunless Hub and Gemini)."""
    port = int(db.get_setting("port", "5000"))
    stats = db.get_stats()
    
    services = [
        {
            "id": "gemini",
            "name": "Gemini",
            "port": port,
            "host": "127.0.0.1",
            "badge": "Google DeepMind",
            "color": "#4285F4",
            "running": True,
            "latency_ms": 12.0,
            "health_path": "/v1/models",
            "cookie_label": "Google __Secure-1PSID Cookie",
            "cookie_placeholder": "Paste raw cookie string containing __Secure-1PSID=... and __Secure-1PSIDTS=...",
            "accounts_count": stats["total_accounts"],
            "active_accounts": stats["active_accounts"],
        }
    ]
    hub = {
        "id": "sunless",
        "name": "Sunless Hub",
        "badge": "Gemini Gateway",
        "port": port,
        "color": "#D97757",
        "pid": os.getpid(),
        "running": True,
        "latency_ms": 0.5,
        "health_path": "/healthz",
        "cookie_label": "System Master Gateway",
    }
    return JSONResponse({"services": services, "hub": hub})


async def api_get_limits(request: Request) -> Response:
    """Return live quotas & limits for Gemini."""
    stats = db.get_stats()
    return JSONResponse({
        "gemini": {
            "provider": "gemini",
            "name": "Google Gemini",
            "badge": "Google DeepMind",
            "color": "#4285F4",
            "authenticated": stats["active_accounts"] > 0,
            "plan": "Free / Web Session",
            "accounts_count": stats["total_accounts"],
            "limits": [
                {"label": "Model Capability", "value": "Gemini 3.8 Flash & Thinking", "status": "ok"},
                {"label": "Context Window", "value": "1,000,000 Tokens (1M)", "status": "ok"},
                {"label": "Stacked Accounts", "value": f"{stats['active_accounts']} Active Accounts", "status": "ok"},
                {"label": "Reasoning & Thinking", "value": "Thinking Budget Supported", "status": "ok"},
                {"label": "Hourly Rate Limit", "value": "Auto-Rotates across Stacked Accounts", "status": "ok"},
            ]
        }
    })


async def api_get_models(request: Request) -> Response:
    """Return catalog for model picker dropdown."""
    catalog = []
    for m_id, cfg in gemini.GEMINI_MODELS.items():
        catalog.append({
            "id": m_id,
            "name": cfg["name"],
            "provider": "gemini",
            "context": cfg["context"],
            "description": cfg["description"],
            "capabilities": ["chat", "roleplay", "streaming"] + (["reasoning"] if "thinking" in m_id else []),
            "locked": False,
        })
    return JSONResponse({"models": catalog})


async def api_get_cookies(request: Request) -> Response:
    """Return stored accounts grouped by provider for Singularity UI."""
    accounts = db.get_accounts()
    gemini_accs = []
    for a in accounts:
        gemini_accs.append({
            "id": a["id"],
            "name": a["name"],
            "token": a["cookie"],
            "identifier": str(a["id"]),
            "plan": "free",
            "status": a["status"],
            "has_psid": bool(a["has_psid"]),
            "has_psidts": bool(a["has_psidts"]),
            "error_count": a.get("error_count", 0),
        })
    return JSONResponse({"gemini": gemini_accs})


async def api_save_cookies(request: Request) -> Response:
    """Save stacked cookies for provider."""
    provider_id = request.path_params.get("provider_id", "gemini")
    try:
        body = await request.json()
    except Exception:
        body = {}
    accounts = body.get("accounts", [])
    if isinstance(accounts, str):
        accounts = [l.strip() for l in accounts.splitlines() if l.strip()]

    added = 0
    for item in accounts:
        cookie_val = item if isinstance(item, str) else item.get("token", "")
        acc_name = None if isinstance(item, str) else item.get("name")
        if cookie_val:
            res = db.add_account(cookie_val, name=acc_name)
            if res.get("success"):
                added += 1

    return JSONResponse({"status": "ok", "provider": "gemini", "saved": added})


async def api_remove_cookie(request: Request) -> Response:
    """Remove stacked account."""
    provider_id = request.path_params.get("provider_id", "gemini")
    try:
        body = await request.json()
    except Exception:
        body = {}
    acc_id = body.get("id") or body.get("identifier") or body.get("index")
    if acc_id is not None:
        try:
            db.delete_account(int(acc_id))
            return JSONResponse({"status": "ok"})
        except Exception:
            pass
    return JSONResponse({"status": "ok"})


async def api_export_cookies(request: Request) -> Response:
    """Export accounts dump."""
    return JSONResponse({"accounts": db.get_accounts()})


async def api_import_cookies(request: Request) -> Response:
    """Import accounts dump."""
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"detail": "Invalid JSON"})
    accs = data.get("accounts", [])
    for a in accs:
        db.add_account(a.get("cookie", ""), name=a.get("name"))
    return JSONResponse({"status": "ok", "imported": len(accs)})


# -------------------------------------------------------------------
# Tunnel Endpoints
# -------------------------------------------------------------------

async def api_get_tunnel(request: Request) -> Response:
    """Inspect ngrok tunnel status."""
    port = int(db.get_setting("port", "5000"))
    url = tunnel.get_public_url()
    is_running = bool(url) and tunnel.is_tunnel_running()
    return JSONResponse({
        "status": "online" if is_running else "offline",
        "installed": tunnel.get_ngrok_bin_path() is not None,
        "running": is_running,
        "url": url,
        "public_url": url,
        "port": port,
        "client_url": url,
    })


async def api_start_tunnel(request: Request) -> Response:
    """Start cloud tunnel."""
    port = int(db.get_setting("port", "5000"))
    res = tunnel.start_tunnel(port=port)
    url = res.get("url") or tunnel.get_public_url()
    is_running = res.get("running", False) or bool(url)
    res["status"] = "online" if is_running else "error"
    res["public_url"] = url
    res["url"] = url
    return JSONResponse(res)


async def api_stop_tunnel(request: Request) -> Response:
    """Stop cloud tunnel."""
    ok = tunnel.stop_tunnel()
    return JSONResponse({"status": "offline", "running": False})


async def api_set_tunnel_token(request: Request) -> Response:
    """Save ngrok authtoken."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    tok = body.get("token") or body.get("authtoken") or ""
    ok = tunnel.set_authtoken(tok)
    return JSONResponse({"status": "ok" if ok else "error"})


async def api_install_tunnel(request: Request) -> Response:
    """Auto-download ngrok binary."""
    dl = tunnel.download_and_extract_ngrok(tunnel.BIN_DIR)
    return JSONResponse({"status": "ok" if dl else "error", "path": dl})


# -------------------------------------------------------------------
# Model Settings Endpoints
# -------------------------------------------------------------------

async def api_get_model_settings(request: Request) -> Response:
    """Retrieve customized settings for models."""
    model = request.query_params.get("model")
    if model:
        raw = db.get_setting(f"model_cfg_{model}", "{}")
        try:
            return JSONResponse({"status": "ok", "model": model, "settings": json.loads(raw)})
        except Exception:
            return JSONResponse({"status": "ok", "model": model, "settings": {}})
    return JSONResponse({"status": "ok", "settings": {}})


async def api_save_model_settings(request: Request) -> Response:
    """Persist settings for model."""
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"detail": "Invalid JSON"})
    model = (data.get("model") or "").strip()
    if not model:
        return JSONResponse(status_code=400, content={"detail": "Missing model name"})
    db.set_setting(f"model_cfg_{model}", json.dumps(data))
    return JSONResponse({"status": "ok", "model": model, "settings": data})


async def api_get_simulation(request: Request) -> Response:
    return JSONResponse({"enabled": False, "mode": "live"})


async def api_get_tavern_status(request: Request) -> Response:
    return JSONResponse({"status": "not_installed"})
# -------------------------------------------------------------------
# Application Initialization
# -------------------------------------------------------------------

routes = [
    Route("/", root_handler, methods=["GET"]),
    Route("/logo.svg", logo_handler, methods=["GET"]),
    Route("/healthz", healthz_handler, methods=["GET"]),
    # OpenAI Gateway
    Route("/v1/models", list_models, methods=["GET"]),
    Route("/v1/chat/completions", chat_completions, methods=["POST"]),
    # Singularity Parity APIs
    Route("/api/services", api_get_services, methods=["GET"]),
    Route("/api/limits", api_get_limits, methods=["GET"]),
    Route("/api/models", api_get_models, methods=["GET"]),
    Route("/api/cookies", api_get_cookies, methods=["GET"]),
    Route("/api/cookies/export", api_export_cookies, methods=["GET"]),
    Route("/api/cookies/import", api_import_cookies, methods=["POST"]),
    Route("/api/cookies/{provider_id}", api_save_cookies, methods=["POST"]),
    Route("/api/cookies/{provider_id}/remove", api_remove_cookie, methods=["POST", "DELETE"]),
    Route("/api/tunnel/status", api_get_tunnel, methods=["GET"]),
    Route("/api/tunnel", api_get_tunnel, methods=["GET"]),
    Route("/api/tunnel/start", api_start_tunnel, methods=["POST"]),
    Route("/api/tunnel/stop", api_stop_tunnel, methods=["POST"]),
    Route("/api/tunnel/authtoken", api_set_tunnel_token, methods=["POST"]),
    Route("/api/tunnel/install", api_install_tunnel, methods=["POST"]),
    Route("/api/model-settings", api_get_model_settings, methods=["GET"]),
    Route("/api/model-settings", api_save_model_settings, methods=["POST"]),
    Route("/api/simulation", api_get_simulation, methods=["GET"]),
    Route("/api/tavern/status", api_get_tavern_status, methods=["GET"]),
]

STATIC_DIR.mkdir(parents=True, exist_ok=True)
routes.append(Mount("/static", app=StaticFiles(directory=str(STATIC_DIR)), name="static"))

app = Starlette(routes=routes)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def run_server(host: str = "0.0.0.0", port: int = 5000, log_level: str = "warning"):
    """Launch uvicorn server."""
    db.init_db()
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level,
        access_log=False,
    )


if __name__ == "__main__":
    port_env = os.getenv("PORT", "5000")
    try:
        p = int(port_env)
    except Exception:
        p = 5000
    run_server(port=p)
