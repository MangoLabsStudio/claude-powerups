## 网页抓取规则

**禁止使用内置 WebFetch 工具。** 所有网页抓取走本地 `web_fetch.py`（三层 fallback：static → crawl4ai → Cloudflare Browser Rendering）：

```bash
{TOOLS_DIR}/web-fetch/venv/bin/python {TOOLS_DIR}/web-fetch/web_fetch.py "<url>"
```

支持多 URL、`-o` 输出到文件、`-s` 指定策略（auto/static/crawl4ai/cf-render）。

### Cloudflare Browser Rendering（可选，Tier 3）

如需启用第三层 fallback，设置环境变量：
```bash
export CF_ACCOUNT_ID="your-account-id"
export CF_API_TOKEN="your-api-token"
```

没有配置时，前两层（static + crawl4ai）仍然可用，覆盖 95% 场景。
