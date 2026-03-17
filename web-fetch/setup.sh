#!/bin/bash
# web-fetch setup — run once after copying to your machine
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Setting up web-fetch in $DIR ..."

python3 -m venv "$DIR/venv"
"$DIR/venv/bin/pip" install -q --upgrade pip
"$DIR/venv/bin/pip" install -q -r "$DIR/requirements.txt"

# crawl4ai needs playwright browsers
"$DIR/venv/bin/crawl4ai-setup" 2>/dev/null || "$DIR/venv/bin/playwright" install chromium 2>/dev/null || true

echo ""
echo "✅ Done. Add this to your CLAUDE.md:"
echo ""
cat "$DIR/CLAUDE-SNIPPET.md"
