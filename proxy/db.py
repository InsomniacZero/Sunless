#!/usr/bin/env python3
"""
Janitor AI x Gemini Proxy - SQLite Credential & Configuration Vault
===================================================================
Zero-dependency local database for stacking Google Gemini accounts,
managing rotation, and saving proxy configurations.
"""

import json
import os
import re
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

MODULE_DIR = Path(__file__).resolve().parent
ROOT_DIR = MODULE_DIR.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "sunless.db"


def get_db_connection() -> sqlite3.Connection:
    """Ensure data directory exists and return an SQLite connection."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database tables and indexes."""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                cookie TEXT NOT NULL,
                has_psid INTEGER DEFAULT 0,
                has_psidts INTEGER DEFAULT 0,
                has_sapisid INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                last_used TIMESTAMP,
                error_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(cookie)
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()


def parse_gemini_cookie(raw: str) -> Dict[str, Any]:
    """Inspect and analyze raw Gemini cookie string or DevTools header."""
    c = raw.strip()
    if c.startswith('"') and c.endswith('"'):
        c = c[1:-1].strip()

    # If full JSON dump or key-value object was pasted
    if c.startswith("{") and c.endswith("}"):
        try:
            data = json.loads(c)
            # Check for cookie string or object
            if "cookie" in data:
                c = data["cookie"]
            elif "value" in data:
                c = data["value"]
            elif any("__Secure" in k for k in data.keys()):
                c = "; ".join(f"{k}={v}" for k, v in data.items())
        except Exception:
            pass

    has_psid = 1 if re.search(r'__Secure-1PSID=([^;]+)', c) else 0
    has_psidts = 1 if re.search(r'__Secure-1PSIDTS=([^;]+)', c) else 0
    has_sapisid = 1 if re.search(r'(?:SAPISID|__Secure-1PAPISID|__Secure-3PAPISID)=([^;]+)', c) else 0

    return {
        "clean_cookie": c,
        "has_psid": has_psid,
        "has_psidts": has_psidts,
        "has_sapisid": has_sapisid,
        "is_valid": bool(has_psid or "SID=" in c or len(c) > 20),
    }


def add_account(raw_cookie: str, name: Optional[str] = None) -> Dict[str, Any]:
    """Add a new Gemini account to the vault."""
    parsed = parse_gemini_cookie(raw_cookie)
    if not parsed["clean_cookie"]:
        return {"success": False, "error": "Empty cookie provided"}

    clean_cookie = parsed["clean_cookie"]
    init_db()

    with get_db_connection() as conn:
        count = conn.execute("SELECT COUNT(*) as c FROM accounts").fetchone()["c"]
        acc_name = name.strip() if name and name.strip() else f"Account #{count + 1}"

        try:
            conn.execute("""
                INSERT INTO accounts (name, cookie, has_psid, has_psidts, has_sapisid, status)
                VALUES (?, ?, ?, ?, ?, 'active')
                ON CONFLICT(cookie) DO UPDATE SET
                    name = excluded.name,
                    has_psid = excluded.has_psid,
                    has_psidts = excluded.has_psidts,
                    has_sapisid = excluded.has_sapisid,
                    status = 'active',
                    error_count = 0
            """, (
                acc_name,
                clean_cookie,
                parsed["has_psid"],
                parsed["has_psidts"],
                parsed["has_sapisid"],
            ))
            conn.commit()
            return {"success": True, "name": acc_name, "parsed": parsed}
        except Exception as e:
            return {"success": False, "error": str(e)}


def get_accounts(only_active: bool = False) -> List[Dict[str, Any]]:
    """Retrieve all stacked accounts ordered by most recently added first."""
    init_db()
    with get_db_connection() as conn:
        q = "SELECT * FROM accounts"
        if only_active:
            q += " WHERE status = 'active'"
        q += " ORDER BY id DESC"
        rows = conn.execute(q).fetchall()
        return [dict(r) for r in rows]


def get_account_by_id(acc_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single account by ID."""
    init_db()
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM accounts WHERE id = ?", (acc_id,)).fetchone()
        return dict(row) if row else None


def delete_account(acc_id: int) -> bool:
    """Remove an account by ID."""
    init_db()
    with get_db_connection() as conn:
        cur = conn.execute("DELETE FROM accounts WHERE id = ?", (acc_id,))
        conn.commit()
        return cur.rowcount > 0


def mark_account_used(acc_id: int) -> None:
    """Update last_used timestamp for an account."""
    try:
        with get_db_connection() as conn:
            conn.execute("UPDATE accounts SET last_used = CURRENT_TIMESTAMP WHERE id = ?", (acc_id,))
            conn.commit()
    except Exception:
        pass


def mark_account_error(acc_id: int, status: str = "rate_limited") -> None:
    """Increment error count and optionally flag account status."""
    try:
        with get_db_connection() as conn:
            conn.execute("""
                UPDATE accounts 
                SET error_count = error_count + 1, status = ?
                WHERE id = ?
            """, (status, acc_id))
            conn.commit()
    except Exception:
        pass


def reset_account_errors() -> None:
    """Reactivate all stacked accounts."""
    try:
        with get_db_connection() as conn:
            conn.execute("UPDATE accounts SET status = 'active', error_count = 0")
            conn.commit()
    except Exception:
        pass


def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve a persistent setting value."""
    init_db()
    try:
        with get_db_connection() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else default
    except Exception:
        return default


def set_setting(key: str, value: str) -> None:
    """Set or update a persistent setting."""
    init_db()
    try:
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
            """, (key, str(value)))
            conn.commit()
    except Exception:
        pass


def get_stats() -> Dict[str, Any]:
    """Get high level vault summary."""
    init_db()
    with get_db_connection() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM accounts").fetchone()["c"]
        active = conn.execute("SELECT COUNT(*) as c FROM accounts WHERE status = 'active'").fetchone()["c"]
        return {
            "total_accounts": total,
            "active_accounts": active,
            "db_path": str(DB_PATH),
        }
