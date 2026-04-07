# memory-system — Claude Code 持久化记忆系统

让 Claude Code 跨 session 记住你的项目、偏好和踩过的坑，不用每次重新解释。

## 前置条件

- 已安装 Claude Code
- 已有至少一个项目在用 Claude Code

## 核心概念

Claude Code 每次新对话都是白纸。解决方案是两层持久化：

| 层 | 文件 | 作用 | 谁读 |
|----|------|------|------|
| **项目指令** | `CLAUDE.md` | 告诉 Claude 这个项目是什么、怎么开发、有什么规矩 | 所有用这个 repo 的人 |
| **个人记忆** | `~/.claude/projects/.../memory/` | 你个人的偏好、踩过的坑、项目状态、API keys | 只有你 |

判断标准：新同事 clone 这个 repo 也需要知道的 → 写 CLAUDE.md；只有你关心的 → 写 memory。

---

## 第一层：CLAUDE.md — 项目级指令

放在项目根目录的 markdown 文件，Claude Code 每次启动自动读取。

### 写什么

```markdown
# CLAUDE.md

## 项目概述
一句话说清楚这个项目干什么、给谁用。

## 技术栈
语言、框架、包管理器、数据库。
Claude 需要这个信息来写对代码。

## 开发命令
npm run dev / build / test / lint
部署流程（git push? scp? CI/CD?）

## 架构要点
目录结构、核心模块、数据流。
不需要写完整架构文档，写 Claude 在改代码时需要知道的关键信息。

## 项目规矩
代码风格、命名规范、禁止事项。
比如：不用 any、必须写测试、部署前跑 lint。
```

### 好 vs 差

**好：** 具体、可执行
```markdown
## 部署
git push origin main → 服务器 git pull → systemctl restart app
禁止 scp 部署，会导致本地和服务器不同步。
```

**差：** 抽象、废话
```markdown
## 部署
本项目采用现代化 CI/CD 流程，确保代码质量和部署一致性。
```

### 加载顺序

Claude Code 按层级加载所有 `CLAUDE.md`：
1. `~/.claude/CLAUDE.md` — 全局（所有项目生效）
2. 项目根目录 `CLAUDE.md` — 项目级
3. 子目录 `CLAUDE.md` — 模块级（可选）

层级越深越具体，不冲突就叠加。

---

## 第二层：Memory — 个人持久记忆

一组 markdown 文件，存在 `~/.claude/projects/{项目路径hash}/memory/` 下。`MEMORY.md` 是索引文件，Claude 每次启动自动读取索引，按需读取具体文件。

### Memory 的四种类型

| 类型 | 存什么 | 什么时候存 |
|------|--------|------------|
| `user` | 你的角色、技术背景、偏好 | Claude 需要了解你才能更好配合时 |
| `feedback` | 你纠正过 Claude 的行为 | Claude 做错了事，你不想它再犯 |
| `project` | 项目状态、进度、背景决策 | 项目有代码/git 里看不到的重要 context |
| `reference` | 外部资源的指针 | "bug 在 Linear 的 XXX 项目里追踪" |

### Memory 文件格式

每个 memory 是一个单独的 markdown 文件：

```markdown
---
name: 部署禁止 scp
description: 不能用 scp 部署到服务器，必须走 git push + git pull
type: feedback
---

服务器部署必须走 git push → 服务器 git pull，不能用 scp。

**Why:** 之前 scp 过一次，导致服务器代码和 git 历史不同步，排查了两小时。

**How to apply:** 任何涉及部署的操作，直接 git push，然后 SSH 上去 git pull。
```

### MEMORY.md 索引

索引文件每行一条，保持简短：

```markdown
# Memory Index

## Feedback
- [feedback_no_scp.md](feedback_no_scp.md) — 部署走 git 不走 scp

## Project
- [project_auth_rewrite.md](project_auth_rewrite.md) — 认证模块重写中，ETA 下周
```

**索引限制 200 行。** 超过会被截断。不要把 memory 当笔记本用。

### 怎么让 Claude 存 memory

直接说：
- "记住这个：部署不能用 scp"
- "以后别再用 any 类型了，记一下"
- "这个项目的背景是…帮我存到 memory"

Claude 会自动创建 memory 文件 + 更新索引。你也可以手动创建/编辑，格式对就行。

### 什么该存、什么不该存

**该存：**
- Claude 做错被你纠正的事 → 不存的话下次还会犯同样的错
- 项目背景中代码/git 里看不到的决策原因 → "为什么用 SQLite 不用 Postgres"
- 你的技术偏好和工作习惯 → Claude 需要知道才能配合你
- 外部资源指针 → "bug tracker 在 Linear 的 XXX 项目"

**不该存：**
- 代码里能看到的东西（架构、文件结构）→ Claude 自己会读代码
- git log 能查到的东西（谁改了什么）→ 用 git blame
- 临时调试信息 → 修完就没用了
- CLAUDE.md 已经写过的内容 → 不重复

### 最重要的一条：及时 handoff

当你一个 session 干了很多事准备换对话时，跟 Claude 说 "handoff"。它会把当前进度、关键发现、下一步存到 memory，并生成一段交接 prompt 让你粘贴到新 session。

不做这一步，session 一关，所有没落盘的 context 就丢了。这是整套系统里最容易忽略、也最影响体验的一个动作。

> 配合 [handoff](../handoff/) 装备使用效果更好 — 它提供了结构化的交接流程。

---

## 实际工作流

### Day 1：初始化

1. 在项目根目录创建 `CLAUDE.md`，写清技术栈、开发命令、项目规矩（20 行就够）
2. 把 `CLAUDE-SNIPPET.md` 的 memory 配置贴到你的 `CLAUDE.md`
3. 第一次对话时，Claude 会自动创建 memory 目录
4. 对话中遇到值得记住的事，直接说"记住这个"

### 日常使用

- **Claude 做错了** → 纠正它，然后说"记一下，以后别这样"（存 feedback）
- **项目有重要背景** → "这个模块在重构，背景是…帮我存一下"（存 project）
- **换 session 继续工作** → Claude 自动读取 CLAUDE.md + MEMORY.md，大部分 context 自动恢复
- **如果 context 不够** → 告诉 Claude "读一下 memory 里关于 XXX 的文件"
- **准备关对话** → 说 "handoff"，保存进度

### 定期维护

memory 会随时间膨胀。建议每月花 10 分钟：

1. 删掉过时的 project memory（已关闭的项目、已修复的 bug）
2. 合并重复条目
3. 确认 MEMORY.md 索引在 200 行以内

---

## 常见问题

**Q: memory 和 CLAUDE.md 写重复了怎么办？**
不写重复。团队共享的写 CLAUDE.md，个人的写 memory。问自己"新来的同事需要知道这个吗？"

**Q: memory 文件会被 git 追踪吗？**
不会。memory 在 `~/.claude/` 下，不在项目目录里。

**Q: Claude 会主动存 memory 吗？**
默认不会。需要你说"记住"或 Claude 判断这个信息对未来有用时会问你。

**Q: context window 不够长怎么办？**
这就是为什么 memory 要精简。200 行索引 + 按需加载，已经是在 context 限制下的最优设计。存太多反而挤占当前对话的思考空间。

---

## 快速开始

1. 给你当前主力项目写一个 `CLAUDE.md`（先写技术栈 + 开发命令 + 部署流程）
2. 下次 Claude 做错事时，纠正它并说"记一下" — 体验一次 memory 写入
3. 第二天开新 session，故意问上次的事 — 验证 memory 是否生效
