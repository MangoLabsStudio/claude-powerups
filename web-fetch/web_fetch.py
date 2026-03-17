#!/usr/bin/env python3
"""
web_fetch.py — Universal web page fetcher with 3-tier fallback.

Strategies (tried in order for 'auto' mode):
  1. static    — aiohttp GET + BeautifulSoup (fast, no JS)
  2. crawl4ai  — Crawl4AI with playwright-stealth (JS + anti-bot fingerprint evasion)
  3. cf-render — Cloudflare Browser Rendering API /markdown endpoint (bypasses CF protection)

Usage:
    # Auto mode (tries cheapest first, escalates on failure)
    python3 web_fetch.py "https://example.com"

    # Force a specific strategy
    python3 web_fetch.py "https://example.com" --strategy cf-render

    # Save to file
    python3 web_fetch.py "https://example.com" -o output.md

    # Wait for specific element (cf-render only)
    python3 web_fetch.py "https://example.com" --strategy cf-render --wait-for "main"

    # Multiple URLs
    python3 web_fetch.py "https://a.com" "https://b.com" -o output.md

Env vars (for cf-render):
    CF_ACCOUNT_ID — Cloudflare account ID
    CF_API_TOKEN  — Cloudflare API token

As a library:
    from web_fetch import fetch_page
    md = await fetch_page("https://example.com", strategy="auto")
"""
import argparse
import asyncio
import os
import re
import sys
import time
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup
from markdownify import markdownify as md_convert

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
MIN_CONTENT_LEN = 50  # below this, consider the fetch failed

# ---------------------------------------------------------------------------
# Strategy 1: Static fetch (aiohttp + BeautifulSoup)
# ---------------------------------------------------------------------------
async def _fetch_static(url: str, timeout: int = 15) -> str | None:
    """Fast static fetch. Works for server-rendered pages, fails on JS SPAs."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={"User-Agent": USER_AGENT},
                timeout=aiohttp.ClientTimeout(total=timeout),
                allow_redirects=True,
            ) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        # Remove noise
        for tag in soup.select("nav, aside, header, footer, script, style, "
                               "[class*='sidebar'], [class*='navigation']"):
            tag.decompose()

        # Try content selectors in order
        content = None
        for sel in ["article", "main", "[role='main']", ".content",
                    "[class*='page-body']", ".markdown-body"]:
            el = soup.select_one(sel)
            if el and len(el.get_text(strip=True)) > MIN_CONTENT_LEN:
                content = str(el)
                break
        if not content:
            body = soup.find("body")
            content = str(body) if body else str(soup)

        result = md_convert(content, heading_style="ATX", strip=["script", "style", "img"])
        result = re.sub(r'\n{3,}', '\n\n', result).strip()
        return result if len(result) > MIN_CONTENT_LEN else None
    except Exception as e:
        print(f"  [static] failed: {e}", file=sys.stderr)
        return None

# ---------------------------------------------------------------------------
# Strategy 2: Crawl4AI with stealth mode (JS + anti-bot evasion)
# ---------------------------------------------------------------------------
async def _fetch_crawl4ai(url: str, timeout: int = 30) -> str | None:
    """JS-capable fetch with playwright-stealth fingerprint evasion via Crawl4AI."""
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    except ImportError:
        print("  [crawl4ai] not installed, skipping", file=sys.stderr)
        return None

    try:
        browser_config = BrowserConfig(
            enable_stealth=True,
            headless=True,
        )
        run_config = CrawlerRunConfig(
            wait_until="networkidle",
            delay_before_return_html=2.0,
            page_timeout=timeout * 1000,
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            if not result.success:
                print(f"  [crawl4ai] crawl failed: {result.error_message}", file=sys.stderr)
                return None

            md = result.markdown
            if hasattr(md, "raw_markdown"):
                md = md.raw_markdown
            md = re.sub(r'\n{3,}', '\n\n', md).strip()
            return md if len(md) > MIN_CONTENT_LEN else None
    except Exception as e:
        print(f"  [crawl4ai] failed: {e}", file=sys.stderr)
        return None

# ---------------------------------------------------------------------------
# Strategy 3: Cloudflare Browser Rendering API
# ---------------------------------------------------------------------------
async def _fetch_cf_render(
    url: str,
    wait_for: str | None = None,
    timeout: int = 30,
) -> str | None:
    """Fetch via Cloudflare Browser Rendering /markdown endpoint.
    Bypasses CF protection. Requires CF_ACCOUNT_ID and CF_API_TOKEN env vars."""
    account_id = os.environ.get("CF_ACCOUNT_ID")
    api_token = os.environ.get("CF_API_TOKEN")
    if not account_id or not api_token:
        print("  [cf-render] CF_ACCOUNT_ID or CF_API_TOKEN not set, skipping", file=sys.stderr)
        return None

    api_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/browser-rendering/markdown"
    payload = {"url": url}
    if wait_for:
        payload["waitForSelector"] = wait_for

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json",
                },
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as resp:
                if resp.status == 429:
                    print("  [cf-render] rate limited, waiting 3s...", file=sys.stderr)
                    await asyncio.sleep(3)
                    # Retry once
                    async with session.post(
                        api_url, json=payload,
                        headers={"Authorization": f"Bearer {api_token}",
                                 "Content-Type": "application/json"},
                        timeout=aiohttp.ClientTimeout(total=timeout),
                    ) as retry_resp:
                        if retry_resp.status != 200:
                            return None
                        data = await retry_resp.json()
                elif resp.status != 200:
                    text = await resp.text()
                    print(f"  [cf-render] HTTP {resp.status}: {text[:200]}", file=sys.stderr)
                    return None
                else:
                    data = await resp.json()

        if not data.get("success", False):
            errors = data.get("errors", [])
            print(f"  [cf-render] API error: {errors}", file=sys.stderr)
            return None

        result = data.get("result", "").strip()
        return result if len(result) > MIN_CONTENT_LEN else None
    except Exception as e:
        print(f"  [cf-render] failed: {e}", file=sys.stderr)
        return None

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
STRATEGIES = {
    "static": _fetch_static,
    "crawl4ai": _fetch_crawl4ai,
    "cf-render": _fetch_cf_render,
}

# Auto mode order: cheapest → most capable
AUTO_ORDER = ["static", "crawl4ai", "cf-render"]


async def fetch_page(
    url: str,
    strategy: str = "auto",
    wait_for: str | None = None,
) -> tuple[str | None, str]:
    """Fetch a URL and return (markdown_content, strategy_used).

    Args:
        url: The URL to fetch
        strategy: "auto", "static", "crawl4ai", or "cf-render"
        wait_for: CSS selector to wait for (cf-render only)

    Returns:
        (markdown_string, strategy_name) or (None, "") if all failed
    """
    if strategy != "auto":
        fn = STRATEGIES.get(strategy)
        if not fn:
            print(f"Unknown strategy: {strategy}", file=sys.stderr)
            return None, ""
        kwargs = {"url": url}
        if strategy == "cf-render" and wait_for:
            kwargs["wait_for"] = wait_for
        result = await fn(**kwargs)
        return result, strategy if result else (None, "")

    # Auto mode: try each strategy in order
    for name in AUTO_ORDER:
        fn = STRATEGIES[name]
        print(f"  trying [{name}]...", file=sys.stderr)
        kwargs = {"url": url}
        if name == "cf-render" and wait_for:
            kwargs["wait_for"] = wait_for
        result = await fn(**kwargs)
        if result:
            print(f"  ✓ [{name}] got {len(result)} chars", file=sys.stderr)
            return result, name
        print(f"  ✗ [{name}] failed or empty", file=sys.stderr)

    return None, ""


async def fetch_pages(
    urls: list[str],
    strategy: str = "auto",
    wait_for: str | None = None,
    delay: float = 1.0,
) -> list[tuple[str, str | None, str]]:
    """Fetch multiple URLs sequentially (to avoid rate limits).

    Returns: list of (url, markdown_content, strategy_used)
    """
    results = []
    for i, url in enumerate(urls):
        if i > 0:
            await asyncio.sleep(delay)
        print(f"\n[{i+1}/{len(urls)}] {url}", file=sys.stderr)
        content, strat = await fetch_page(url, strategy=strategy, wait_for=wait_for)
        results.append((url, content, strat))
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Universal web page fetcher → markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Strategies: auto (default), static, crawl4ai, cf-render",
    )
    parser.add_argument("urls", nargs="+", help="URL(s) to fetch")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument("-s", "--strategy", default="auto",
                        choices=["auto", "static", "crawl4ai", "cf-render"])
    parser.add_argument("--wait-for", help="CSS selector to wait for (cf-render)")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Delay between requests in seconds (default: 1.0)")
    args = parser.parse_args()

    async def run():
        results = await fetch_pages(
            args.urls, strategy=args.strategy,
            wait_for=args.wait_for, delay=args.delay,
        )

        parts = []
        for url, content, strat in results:
            if content:
                domain = urlparse(url).netloc
                parts.append(f"# {domain}\n\nSource: {url}\n\n{content}")
            else:
                parts.append(f"# FAILED: {url}\n\nAll strategies failed for this URL.")

        output = "\n\n---\n\n".join(parts)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            ok = sum(1 for _, c, _ in results if c)
            print(f"\n✅ {ok}/{len(results)} pages saved → {args.output}", file=sys.stderr)
        else:
            print(output)

    asyncio.run(run())


if __name__ == "__main__":
    main()
