# web-fetch — 三层 Fallback 网页抓取工具

解决 Claude Code 内置 WebFetch 被 Cloudflare 挡、JS 页面抓不到的问题。

## 三层策略

| 层级 | 引擎 | 适用场景 | 成本 |
|------|------|---------|------|
| Tier 1 | aiohttp + BS4 | 静态页面（90% 场景） | 0 |
| Tier 2 | Crawl4AI (Playwright) | JS 渲染 + 反爬 | 本地 CPU |
| Tier 3 | Cloudflare Browser Rendering | CF 保护页面 | CF 额度 |

Auto 模式从最便宜的开始试，失败才升级到下一层。

## 安装

```bash
# 1. 把这个目录复制到你的 .claude/tools/
cp -r web-fetch ~/.claude/tools/web-fetch

# 2. 运行 setup
cd ~/.claude/tools/web-fetch && bash setup.sh

# 3. 把 CLAUDE-SNIPPET.md 的内容贴到你项目的 CLAUDE.md
#    记得把 {TOOLS_DIR} 替换成你的实际路径
```

## 用法

```bash
# 基本用法
venv/bin/python web_fetch.py "https://example.com"

# 保存到文件
venv/bin/python web_fetch.py "https://example.com" -o output.md

# 强制指定策略
venv/bin/python web_fetch.py "https://example.com" -s cf-render

# 多个 URL
venv/bin/python web_fetch.py "https://a.com" "https://b.com" -o output.md
```

## Cloudflare Tier 3（可选）

需要 Cloudflare 账号，设置环境变量：
```bash
export CF_ACCOUNT_ID="xxx"
export CF_API_TOKEN="xxx"
```

不配也能用，Tier 1 + 2 覆盖绝大多数场景。
