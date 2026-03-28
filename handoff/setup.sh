#!/bin/bash
# handoff — 纯 prompt skill，无依赖安装
# 只需复制 SKILL.md 到 Claude Code skills 目录

set -e

SKILL_DIR="${HOME}/.claude/skills/handoff"

echo "📦 安装 handoff skill..."

mkdir -p "$SKILL_DIR"
cp SKILL.md "$SKILL_DIR/SKILL.md"

echo "✅ 已安装到 ${SKILL_DIR}"
echo ""
echo "下一步："
echo "  把 CLAUDE-SNIPPET.md 的内容贴到你项目的 CLAUDE.md"
echo "  然后在 Claude Code 里说 /handoff 就能用了"
