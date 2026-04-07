# claude-powerups ⚡

Claude Code 增强装备点 — 团队共用的工具和配置，让 Claude Code 更能打。

## 装备列表

| 装备 | 解决什么 | 安装 |
|------|---------|------|
| [web-fetch](./web-fetch/) | 内置 WebFetch 抓取失败（Cloudflare、JS 页面、反爬） | `cd web-fetch && bash setup.sh` |
| [handoff](./handoff/) | 换 session 时上下文丢失，要重新解释 | `cd handoff && bash setup.sh` |
| [memory-system](./memory-system/) | 让 Claude 跨 session 记住项目、偏好和踩过的坑 | 读 README + 贴 CLAUDE-SNIPPET |

## 怎么用

每个装备是一个独立目录，包含：
- `README.md` — 说明
- `setup.sh` — 一键安装
- `CLAUDE-SNIPPET.md` — 贴到你 CLAUDE.md 的配置片段

通用流程：
1. Clone 这个 repo
2. 进入你要装的装备目录
3. 跑 `bash setup.sh`
4. 把 `CLAUDE-SNIPPET.md` 内容贴到你项目的 `CLAUDE.md`

## 贡献新装备

新建一个目录，包含上面三个文件即可。
