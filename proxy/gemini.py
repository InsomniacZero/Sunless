#!/usr/bin/env python3
"""
Janitor AI x Gemini Proxy - Dedicated Gemini Web2API Engine
============================================================
High-speed reverse-proxy client connecting directly to Google Gemini Web
(Batchexecute RPC) for authentic, infinite Janitor AI Roleplay inference.
Zero personal info, multi-account rotation, and RP-optimized text cleaning.
"""

import asyncio
import hashlib
import json
import os
import re
import time
import urllib.parse
import uuid
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

import httpx

from . import db
from . import search

# Default fallback build label if scraping is in progress
DEFAULT_BL = "boq_assistant-bard-web-server_20260925.18_p1"

# Model presets specifically optimized for Janitor AI Roleplay
GEMINI_MODELS = {
    # 3.8 Frontier Generation (Latest 2026 Release)
    "gemini-3.8-flash": {
        "id": "gemini-3.8-flash",
        "name": "Gemini 3.8 Flash",
        "mode": 1,
        "think": 4,
        "context": "1M tokens",
        "description": "Google's 2026 workhorse: ultra-fast agentic reasoning, long-horizon narrative, and 64k output limit.",
    },
    "gemini-3.8-flash-thinking": {
        "id": "gemini-3.8-flash-thinking",
        "name": "Gemini 3.8 Flash Thinking",
        "mode": 2,
        "think": 0,
        "context": "1M tokens",
        "description": "Test-time internal reasoning reflection for complex multi-character roleplay lorebooks.",
    },
    # 3.7 Generation
    "gemini-3.7-flash": {
        "id": "gemini-3.7-flash",
        "name": "Gemini 3.7 Flash",
        "mode": 1,
        "think": 4,
        "context": "1M tokens",
        "description": "Frontier fast-inference model for low-latency dialogue.",
    },
    "gemini-3.7-flash-thinking": {
        "id": "gemini-3.7-flash-thinking",
        "name": "Gemini 3.7 Flash Thinking",
        "mode": 2,
        "think": 0,
        "context": "1M tokens",
        "description": "CoT reasoning engine for intricate world scenarios.",
    },
    # 3.6 Generation
    "gemini-3.6-flash": {
        "id": "gemini-3.6-flash",
        "name": "Gemini 3.6 Flash",
        "mode": 1,
        "think": 4,
        "context": "1M tokens",
        "description": "High-throughput responsive dialogue model.",
    },
    "gemini-3.6-flash-thinking": {
        "id": "gemini-3.6-flash-thinking",
        "name": "Gemini 3.6 Flash Thinking",
        "mode": 2,
        "think": 0,
        "context": "1M tokens",
        "description": "Dynamic reasoning variant.",
    },
    # 3.5 Generation
    "gemini-3.5-flash": {
        "id": "gemini-3.5-flash",
        "name": "Gemini 3.5 Flash",
        "mode": 1,
        "think": 4,
        "context": "1M tokens",
        "description": "Reliable fast dialogue generation.",
    },
    "gemini-3.5-flash-thinking": {
        "id": "gemini-3.5-flash-thinking",
        "name": "Gemini 3.5 Flash Thinking",
        "mode": 2,
        "think": 0,
        "context": "1M tokens",
        "description": "Reflection-enabled conversational variant.",
    },
    "gemini-3.5-flash-lite": {
        "id": "gemini-3.5-flash-lite",
        "name": "Gemini 3.5 Flash Lite",
        "mode": 6,
        "think": 4,
        "context": "1M tokens",
        "description": "Lightweight sub-second response engine for quick chat turns.",
    },
    "gemini-3.5-flash-lite-thinking": {
        "id": "gemini-3.5-flash-lite-thinking",
        "name": "Gemini 3.5 Flash Lite Thinking",
        "mode": 6,
        "think": 0,
        "context": "1M tokens",
        "description": "Ultra-light reasoning model.",
    },
    # 3.1 Pro Generation
    "gemini-3.1-pro": {
        "id": "gemini-3.1-pro",
        "name": "Gemini 3.1 Pro",
        "mode": 3,
        "think": 4,
        "context": "2M tokens",
        "description": "Deepest multimodal reasoning, immaculate roleplay prose, and 2M token context window.",
    },
    "gemini-3.1-pro-thinking": {
        "id": "gemini-3.1-pro-thinking",
        "name": "Gemini 3.1 Pro Thinking",
        "mode": 3,
        "think": 0,
        "context": "2M tokens",
        "description": "Flagship thinking Pro for multi-layer storytelling and intricate world states.",
    },
    # Nano Banana Visual Models
    "nano-banana-2": {
        "id": "nano-banana-2",
        "name": "Nano Banana 2",
        "mode": 1,
        "think": 4,
        "context": "1M tokens",
        "description": "High-fidelity Google image synthesis engine.",
    },
    "nano-banana-pro": {
        "id": "nano-banana-pro",
        "name": "Nano Banana Pro",
        "mode": 3,
        "think": 4,
        "context": "2M tokens",
        "description": "Professional high-definition image generation.",
    },
    "nano-banana-2-lite": {
        "id": "nano-banana-2-lite",
        "name": "Nano Banana 2 Lite",
        "mode": 6,
        "think": 4,
        "context": "1M tokens",
        "description": "Fast image synthesis engine.",
    },
    "nano-banana": {
        "id": "nano-banana",
        "name": "Nano Banana",
        "mode": 1,
        "think": 4,
        "context": "1M tokens",
        "description": "Standard image generator.",
    },
}

_SESSION_CACHE: Dict[str, Dict[str, Any]] = {}


async def get_gemini_session_context(cookie_str: Optional[str]) -> Tuple[str, str]:
    """Retrieve or dynamically extract SNlM0e XSRF token and active build label for Google Gemini."""
    cache_key = cookie_str or "guest"
    now = time.time()
    cached = _SESSION_CACHE.get(cache_key)
    if cached and (now - cached.get("ts", 0) < 3600.0) and cached.get("snlm0e"):
        return cached["snlm0e"], cached["bl"]
    if cached and (now - cached.get("ts", 0) < 600.0) and cached.get("failed"):
        return "", cached.get("bl", DEFAULT_BL)

    snlm0e = ""
    bl = os.getenv("GEMINI_BL", DEFAULT_BL)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Referer": "https://gemini.google.com/",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if cookie_str:
        headers["Cookie"] = cookie_str

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get("https://gemini.google.com/app", headers=headers)
            if resp.status_code == 200:
                sn_match = re.findall(r'"(?:SNlM0e|thykhd)":"([^"]+)"', resp.text)
                if sn_match:
                    snlm0e = sn_match[0]
                bl_match = re.findall(r'"cfb2h":"([^"]+)"', resp.text)
                if bl_match:
                    bl = bl_match[0]
    except Exception:
        pass

    if snlm0e:
        _SESSION_CACHE[cache_key] = {"snlm0e": snlm0e, "bl": bl, "ts": now}
    else:
        _SESSION_CACHE[cache_key] = {"snlm0e": "", "bl": bl, "failed": True, "ts": now}
    return snlm0e, bl


def clean_gemini_rp_text(text: str) -> str:
    """Clean internal Google Gemini artifacts, chips, code fences, and citation numbers for clean RP."""
    if not text:
        return ""
    # Strip citation chips like [cite: 1], [cite: 2], [source 1], [1], etc.
    text = re.sub(r'\[\s*(?:cite|source|ref)?[:\s]*\d+\s*\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(?:cite|source|ref)[:\s]*\d+\b', '', text, flags=re.IGNORECASE)
    # Strip internal Google action cards and elicitation chips
    text = re.sub(
        r'</?(?:Elic[ia]t|Suggest|FollowUp|ActionCard|RelatedQueries)[A-Za-z0-9_]*[^>]*>.*?(?:</(?:Elic[ia]t|Suggest|FollowUp|ActionCard|RelatedQueries)[A-Za-z0-9_]*>|$)|</?(?:Elic[ia]t|Suggest|FollowUp|ActionCard|RelatedQueries)[A-Za-z0-9_]*[^>]*/?>',
        '', text, flags=re.DOTALL | re.IGNORECASE
    )
    text = re.sub(
        r'<[A-Za-z0-9_-]+[^>]*\b(?:label|query)=[\'"][^\'"]*[\'"][^>]*>.*?</[A-Za-z0-9_-]+>',
        '', text, flags=re.DOTALL | re.IGNORECASE
    )
    text = re.sub(r'</?(?:[A-Za-z0-9_]*(?:Elic|Sugg|Follow|Action)[A-Za-z0-9_]*)[^>]*$', '', text, flags=re.IGNORECASE)
    # Strip trailing partial Google elicitation/action tags without touching <think> or </think>
    text = re.sub(r'<(?:Elic|Sugg|Follow|Action|Related)[A-Za-z0-9_-]*[^>]*$', '', text, flags=re.IGNORECASE)
    # Strip leading assistant labels if Gemini echoes them
    text = re.sub(r'^(?:\[(?:Assistant|Model|Character)\]:?|(?:Assistant|Model|Character):)\s*', '', text, flags=re.IGNORECASE)
    # Clean placeholders
    text = text.replace("video_placeholder", "").replace("image_placeholder", "")
    return text


THINKING_PROTOCOL = (
    "[Reasoning & Roleplay Strategy Protocol:\n"
    "You are an advanced reasoning model equipped with chain-of-thought capability. For this roleplay response, you MUST first execute your explicit internal deliberation enclosed entirely within <think> and </think> tags.\n"
    "Inside <think>...</think>, you must:\n"
    "1. Deconstruct the user's action/dialogue, subtext, and scenario dynamics.\n"
    "2. Analyze your character's psychological state, hidden motives, emotional shifts, and relationship dynamics.\n"
    "3. Plan the scene's pacing, physical environment, sensory details, and dialogue nuances.\n"
    "4. Ensure full consistency with character lore, personality traits, and uncensored roleplay narrative freedom.\n\n"
    "Format Requirement:\n"
    "<think>\n"
    "[Your thorough step-by-step reasoning, internal thoughts, emotional breakdown, and narrative strategy here]\n"
    "</think>\n"
    "[Your in-character dialogue, actions, sensory descriptions, and narrative response here]\n\n"
    "CRITICAL: You MUST begin your response immediately with the opening tag <think> and close your thinking process with </think> before writing any roleplay dialogue or narrative.]"
)


def format_janitor_messages_to_prompt(
    messages: List[Dict[str, Any]],
    is_thinking: bool = False,
    grounding: str = "",
) -> str:
    """
    Format Janitor AI roleplay messages into an authentic, immersive prompt for Gemini.
    Preserves character definitions, jailbreak/uncensored guidelines, scenarios,
    and dialogue flow with clean speaker cues.
    When is_thinking is True, injects an explicit reasoning directive to output inside <think>...</think> tags.
    When grounding is provided, injects live web search findings directly into system context.
    """
    system_parts = []
    dialogue_parts = []

    if is_thinking:
        system_parts.append(THINKING_PROTOCOL)

    if grounding:
        system_parts.append(grounding)

    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if isinstance(content, list):
            sub_txt = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    sub_txt.append(item.get("text", ""))
                elif isinstance(item, str):
                    sub_txt.append(item)
            content = " ".join(sub_txt)
        content_str = str(content).strip()
        if not content_str:
            continue

        if role == "system":
            system_parts.append(content_str)
        elif role == "assistant":
            dialogue_parts.append(f"{content_str}")
        else:
            dialogue_parts.append(f"{content_str}")

    prompt_sections = []
    if system_parts:
        sys_block = "\n\n".join(system_parts)
        prompt_sections.append(f"[System Context & Roleplay Guidelines:\n{sys_block}\n]")

    if dialogue_parts:
        # Join conversation turns naturally
        prompt_sections.append("\n\n".join(dialogue_parts))

    return "\n\n".join(prompt_sections) if prompt_sections else "Hello"


async def stream_gemini_chat(
    model: str,
    messages: List[Dict[str, Any]],
    cookie_str: Optional[str] = None,
    stream: bool = True,
    thinking_budget: Optional[int] = None,
    **kwargs,
) -> AsyncIterator[Dict[str, Any]]:
    """
    Stream roleplay chat completions from Google Gemini Web API.
    Yields standard OpenAI-compatible chunks:
    `{"id": "...", "object": "chat.completion.chunk", "choices": [{"delta": {"content": "..."}}]}`
    """
    chat_id = f"chatcmpl-janitor-{uuid.uuid4().hex[:12]}"
    created_ts = int(time.time())

    # 1. Resolve active account cookies from DB or passed cookie_str
    accounts = db.get_accounts(only_active=True)
    candidate_cookies = []
    account_ids = []

    if cookie_str and cookie_str.strip():
        candidate_cookies.append(cookie_str.strip())
        account_ids.append(None)

    for acc in accounts:
        tok = acc.get("cookie")
        if tok and tok not in candidate_cookies:
            candidate_cookies.append(tok)
            account_ids.append(acc.get("id"))

    is_image_model = any(k in model.lower() for k in ("nano-banana", "imagen", "image"))

    # STRICT RULE: ONLY image models require cookies.
    # Normal chat/roleplay models (3.8 Flash, 3.7 Flash, 3.1 Pro, etc.) NEVER need cookies!
    if is_image_model and not candidate_cookies:
        yield {
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": created_ts,
            "model": model,
            "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
        }
        yield {
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": created_ts,
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {
                    "content": (
                        "⚠️ **Google Gemini Image Generation Requires Authentication**\n\n"
                        "Google strictly requires an active Google account session with `__Secure-1PSID` and `__Secure-1PSIDTS` cookies for image synthesis (`Nano Banana`).\n\n"
                        "**Quick 30-Second Setup:**\n"
                        "1. Open [gemini.google.com](https://gemini.google.com) in your browser and sign in.\n"
                        "2. Copy `__Secure-1PSID` & `__Secure-1PSIDTS` cookies (or full `Cookie:` header from DevTools Network tab).\n"
                        "3. Paste them into the **Accounts / Cookie Stacker** tab in Sunless UI, or run `nephis` in terminal."
                    )
                },
                "finish_reason": "stop",
            }],
        }
        return

    # For normal models: guest mode (zero cookies) is always the default
    if not candidate_cookies:
        candidate_cookies = [""]
        account_ids = [None]

    # 2. Resolve model configuration
    m_clean = model.lower().strip()
    m_cfg = GEMINI_MODELS.get(m_clean)
    if not m_cfg:
        # Fuzzy fallback for custom aliases (e.g., 'gemini-3.8', 'gemini-flash', 'gemini-thinking')
        if "3.1" in m_clean or "pro" in m_clean:
            m_cfg = GEMINI_MODELS["gemini-3.1-pro-thinking"] if "think" in m_clean else GEMINI_MODELS["gemini-3.1-pro"]
        elif "3.7" in m_clean:
            m_cfg = GEMINI_MODELS["gemini-3.7-flash-thinking"] if "think" in m_clean else GEMINI_MODELS["gemini-3.7-flash"]
        elif "3.6" in m_clean:
            m_cfg = GEMINI_MODELS["gemini-3.6-flash-thinking"] if "think" in m_clean else GEMINI_MODELS["gemini-3.6-flash"]
        elif "3.5" in m_clean:
            if "lite" in m_clean:
                m_cfg = GEMINI_MODELS["gemini-3.5-flash-lite-thinking"] if "think" in m_clean else GEMINI_MODELS["gemini-3.5-flash-lite"]
            else:
                m_cfg = GEMINI_MODELS["gemini-3.5-flash-thinking"] if "think" in m_clean else GEMINI_MODELS["gemini-3.5-flash"]
        elif "banana" in m_clean:
            m_cfg = GEMINI_MODELS["nano-banana-2"]
        elif "think" in m_clean:
            m_cfg = GEMINI_MODELS["gemini-3.8-flash-thinking"]
        else:
            m_cfg = GEMINI_MODELS["gemini-3.8-flash"]

    model_id = m_cfg["mode"]
    think_mode = m_cfg["think"]

    # Thinking budget overrides if requested
    if thinking_budget is not None:
        try:
            tb = int(thinking_budget)
            if tb == 0:
                think_mode = 4
                if model_id == 2:
                    model_id = 1
            elif tb > 0:
                think_mode = 0
                if model_id == 1:
                    model_id = 2
        except Exception:
            pass

    is_thinking_model = (think_mode == 0) or ("think" in m_clean) or ("thinking" in m_clean)

    # 3. Live Web Search Grounding detection
    last_user_text = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            c = m.get("content", "")
            if isinstance(c, list):
                c = " ".join(item.get("text", "") for item in c if isinstance(item, dict))
            last_user_text = str(c).strip()
            break

    web_search = kwargs.get("web_search", False)
    should_search, extracted_query = search.detect_search_intent(last_user_text)
    grounding_context = ""
    if (web_search or should_search) and (extracted_query or last_user_text):
        query_to_search = extracted_query or last_user_text
        try:
            grounding_context = await search.get_search_grounding(query_to_search)
        except Exception:
            pass

    prompt = format_janitor_messages_to_prompt(
        messages,
        is_thinking=is_thinking_model,
        grounding=grounding_context,
    )

    # 3. Build Batchexecute RPC payload array
    inner = [None] * 80
    inner[0] = [prompt, 0, None, None, None, None, 0]
    inner[1] = ["en"]
    inner[2] = ["", "", "", None, None, None, None, None, None, ""]
    inner[6] = [0]
    inner[7] = 1
    inner[10] = 1
    inner[11] = 0
    inner[17] = [[think_mode]]
    inner[18] = 0
    inner[27] = 1
    inner[30] = [4]
    inner[53] = 0
    inner[59] = str(uuid.uuid4())
    inner[61] = []
    inner[68] = 1
    inner[79] = model_id

    outer = [None, json.dumps(inner)]

    # Initial assistant role chunk
    yield {
        "id": chat_id,
        "object": "chat.completion.chunk",
        "created": created_ts,
        "model": model,
        "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
    }

    # 4. Multi-account failover loop
    total_candidates = len(candidate_cookies)
    yielded_any = False

    for acc_idx, (curr_cookie, curr_acc_id) in enumerate(zip(candidate_cookies, account_ids)):
        if curr_cookie:
            snlm0e, bl = await get_gemini_session_context(curr_cookie)
        else:
            snlm0e = ""
            bl = DEFAULT_BL

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://gemini.google.com",
            "Referer": "https://gemini.google.com/app",
            "X-Same-Domain": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }
        if curr_cookie:
            headers["Cookie"] = curr_cookie
            # Derive SAPISIDHASH if SAPISID is available in cookie header
            sapisid_m = re.search(r'(?:SAPISID|__Secure-1PAPISID|__Secure-3PAPISID)=([^;]+)', curr_cookie)
            if sapisid_m:
                sapisid = sapisid_m.group(1).strip()
                ts = int(time.time())
                h = hashlib.sha1(f"{ts} {sapisid} https://gemini.google.com".encode()).hexdigest()
                headers["Authorization"] = f"SAPISIDHASH {ts}_{h}"

        prev_text = ""
        success = False

        for attempt in range(2):
            params = {"f.req": json.dumps(outer)}
            if snlm0e:
                params["at"] = snlm0e
            body = urllib.parse.urlencode(params)
            reqid = int(time.time()) % 1000000

            url = (
                f"https://gemini.google.com/_/BardChatUi/data/"
                "assistant.lamda.BardFrontendService/StreamGenerate"
                f"?bl={bl}&hl=en&_reqid={reqid}&rt=c"
            )

            try:
                async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=15.0), follow_redirects=True) as client:
                    async with client.stream("POST", url, content=body.encode("utf-8"), headers=headers) as resp:
                        if resp.status_code >= 400:
                            err_txt = (await resp.aread()).decode("utf-8", errors="ignore")
                            # Auto-heal: If Google emits updated XSRF token in 400 body, capture & retry
                            m_xsrf = re.search(r'["\']?xsrf["\']?\s*,\s*["\']([^"\'\s]+)["\']', err_txt)
                            if m_xsrf and attempt == 0:
                                snlm0e = m_xsrf.group(1)
                                cache_key = curr_cookie or "guest"
                                _SESSION_CACHE[cache_key] = {"snlm0e": snlm0e, "bl": bl, "ts": time.time()}
                                continue

                            # Mark account error in DB if rate-limited or invalid
                            if curr_acc_id:
                                db.mark_account_error(curr_acc_id, status="rate_limited" if resp.status_code == 429 else "error")
                            break

                        buf = ""
                        prev_text = ""
                        async for chunk in resp.aiter_text():
                            buf += chunk
                            while "\n" in buf:
                                line, buf = buf.split("\n", 1)
                                if '"wrb.fr"' not in line or len(line) < 150:
                                    continue

                                try:
                                    arr = json.loads(line)
                                    inner_str = arr[0][2]
                                    if not inner_str or len(inner_str) < 50:
                                        continue
                                    inner2 = json.loads(inner_str)
                                    if yielded_any and isinstance(inner2, list) and len(inner2) <= 3:
                                        break
                                    if isinstance(inner2, list) and len(inner2) > 4 and inner2[4]:
                                        for part in inner2[4]:
                                            if isinstance(part, list) and len(part) > 1 and part[1] and isinstance(part[1], list):
                                                for t in part[1]:
                                                    if isinstance(t, str):
                                                        clean_full = clean_gemini_rp_text(t)
                                                        clean_prev = clean_gemini_rp_text(prev_text)
                                                        if len(clean_full) > len(clean_prev):
                                                            delta = clean_full[len(clean_prev):]
                                                            if delta:
                                                                yield {
                                                                    "id": chat_id,
                                                                    "object": "chat.completion.chunk",
                                                                    "created": created_ts,
                                                                    "model": model,
                                                                    "choices": [{"index": 0, "delta": {"content": delta}, "finish_reason": None}],
                                                                }
                                                                yielded_any = True
                                                        prev_text = t
                                except Exception:
                                    pass
                            if yielded_any and isinstance(inner2, list) and len(inner2) <= 3:
                                break

                        success = True
                        if curr_acc_id:
                            db.mark_account_used(curr_acc_id)
                        break
            except (httpx.ReadTimeout, httpx.RemoteProtocolError):
                if yielded_any:
                    success = True
                    break
                break
            except Exception:
                if yielded_any:
                    success = True
                    break
                if attempt == 0:
                    continue
                break

        if success and yielded_any:
            break

    # If all accounts failed and nothing was yielded
    if not yielded_any:
        error_advice = (
            "⚠️ **Gemini Roleplay Proxy Notice**\n\n"
            "Could not connect to Google Gemini upstream endpoint.\n"
            "Please check your network connection or try another model variant (e.g. Gemini 3.8 Flash, Gemini 3.1 Pro)."
        )
        yield {
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": created_ts,
            "model": model,
            "choices": [{"index": 0, "delta": {"content": error_advice}, "finish_reason": "error"}],
        }

    # Final stop chunk
    yield {
        "id": chat_id,
        "object": "chat.completion.chunk",
        "created": created_ts,
        "model": model,
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
    }


async def generate_gemini_chat(
    model: str,
    messages: List[Dict[str, Any]],
    cookie_str: Optional[str] = None,
    thinking_budget: Optional[int] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Execute complete non-streaming chat completion for Janitor AI."""
    full_text = []
    created_ts = int(time.time())
    chat_id = f"chatcmpl-janitor-{uuid.uuid4().hex[:12]}"

    async for chunk in stream_gemini_chat(
        model=model,
        messages=messages,
        cookie_str=cookie_str,
        stream=False,
        thinking_budget=thinking_budget,
        **kwargs,
    ):
        choices = chunk.get("choices", [])
        if choices:
            c = choices[0].get("delta", {}).get("content")
            if c:
                full_text.append(c)

    content_str = "".join(full_text)
    return {
        "id": chat_id,
        "object": "chat.completion",
        "created": created_ts,
        "model": model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": content_str,
            },
            "finish_reason": "stop",
        }],
        "usage": {
            "prompt_tokens": len(str(messages)) // 4,
            "completion_tokens": len(content_str) // 4,
            "total_tokens": (len(str(messages)) + len(content_str)) // 4,
        },
    }
