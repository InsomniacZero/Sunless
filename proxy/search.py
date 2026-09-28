"""
Live Web Search Grounding Engine for Sunless (Janitor AI Proxy).
Provides zero-dependency, ultra-low-latency web search grounding
via DuckDuckGo HTML endpoint with automatic intent detection.
"""
import re
import html
import urllib.parse
from typing import List, Dict, Optional, Tuple
import httpx

# Trigger keywords for automatic web search intent detection
SEARCH_INTENT_PATTERNS = [
    r'\b(?:web\s*search|search\s*(?:the\s*)?web|google|search\s*online|look\s*up|browse\s*(?:the\s*)?web)\b',
    r'\b(?:latest|current|recent|today(?:\'s)?|news|updates?|who\s*is|what\s*happened\s*to)\b',
    r'\b(?:release\s*date|schedule|patch\s*notes|scores?|weather|stock\s*price)\b',
]

CLEAN_QUERY_PREFIXES = [
    r'^(?:yo,?\s*)?(?:sheesh,?\s*)?(?:please\s*)?(?:can\s*you\s*)?(?:web\s*search\s*(?:about|for)?|search\s*(?:the\s*)?web\s*(?:for|about)?|search\s*(?:google\s*)?(?:for|about)?|google\s*|look\s*up\s*(?:online\s*)?)\s*',
    r'^(?:who\s*is|what\s*is|tell\s*me\s*about)\s*',
]


def detect_search_intent(text: str) -> Tuple[bool, str]:
    """
    Detect if the user prompt has search intent, and extract the clean search query.
    Returns (should_search, extracted_query).
    """
    if not text or len(text.strip()) < 3:
        return False, ""

    text_clean = text.strip()
    # Check explicit search keywords
    matched = False
    for pat in SEARCH_INTENT_PATTERNS:
        if re.search(pat, text_clean, re.IGNORECASE):
            matched = True
            break

    if not matched:
        return False, ""

    # Clean query for search engine
    q = text_clean
    for pat in CLEAN_QUERY_PREFIXES:
        q = re.sub(pat, '', q, flags=re.IGNORECASE).strip()

    # Strip trailing punctuation
    q = re.sub(r'[\?\.!\s]+$', '', q).strip()
    return True, q or text_clean


async def search_duckduckgo(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Perform a live web search on DuckDuckGo HTML endpoint without external dependencies.
    Returns list of dicts with 'title', 'snippet', 'url'.
    """
    if not query:
        return []

    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Referer": "https://html.duckduckgo.com/",
    }

    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            resp = await client.post(url, data={"q": query}, headers=headers)
            if resp.status_code != 200:
                return []

            raw_html = resp.text
            # Extract snippets and URLs with robust regex patterns
            snippets_raw = re.findall(r'<a\s+class="result__snippet[^"]*"[^>]*>(.*?)</a>', raw_html, re.DOTALL)
            urls_raw = re.findall(r'<a\s+class="result__url[^"]*"[^>]*>(.*?)</a>', raw_html, re.DOTALL)
            titles_raw = re.findall(r'<a\s+class="result__a[^"]*"[^>]*>(.*?)</a>', raw_html, re.DOTALL)

            results = []
            count = min(len(snippets_raw), max_results)
            for i in range(count):
                snip = html.unescape(re.sub(r'<[^>]+>', '', snippets_raw[i])).strip()
                link = html.unescape(re.sub(r'<[^>]+>', '', urls_raw[i])).strip() if i < len(urls_raw) else ""
                title = html.unescape(re.sub(r'<[^>]+>', '', titles_raw[i])).strip() if i < len(titles_raw) else ""
                if snip:
                    results.append({
                        "title": title or f"Source {i+1}",
                        "snippet": snip,
                        "url": link,
                    })
            return results
    except Exception:
        return []


async def get_search_grounding(query: str, max_results: int = 4) -> str:
    """
    Execute live search and format as a structured grounding block for LLM prompts.
    """
    results = await search_duckduckgo(query, max_results=max_results)
    if not results:
        return ""

    lines = [f"[Live Web Search Grounding for: \"{query}\"]"]
    for r in results:
        url_part = f" (Source: {r['url']})" if r.get('url') else ""
        title_part = f"**{r['title']}**: " if r.get('title') else ""
        lines.append(f"- {title_part}{r['snippet']}{url_part}")

    lines.append(
        "[Grounding Instructions: Use the verified live web search findings above to answer the user accurately. "
        "Maintain the requested character tone, narrative immersion, or roleplay persona.]"
    )
    return "\n".join(lines)
