# handoff — Session 交接工具

保存当前会话的关键上下文到 memory 系统，并生成一段可直接复制粘贴到新 session 的 prompt，实现无缝衔接。

## 特点

- **纯 Prompt 驱动**：无脚本、无依赖，Claude Code 原生执行
- **Memory + Prompt 双通道**：memory 提供跨 session 背景，prompt 提供即时指令，两者互补不重复
- **30 行以内**：交接 prompt 控制在 30 行，保持高信噪比

## 三步流程

| 步骤 | 做什么 |
|------|--------|
| **Analyze** | 从当前会话提取：主题、已完成、未完成、关键发现、阻塞项、下一步、关键文件 |
| **Memory** | 检查现有 memory → 更新/新建相关 memory 文件 → 更新 MEMORY.md 索引 |
| **Prompt** | 生成 ≤ 30 行交接 prompt（文件引用 + 停在哪里 + 下一步），代码块包裹方便复制 |

## 安装

```bash
# 1. 复制 skill 文件
mkdir -p ~/.claude/skills/handoff
cp SKILL.md ~/.claude/skills/handoff/SKILL.md

# 2. 把 CLAUDE-SNIPPET.md 的内容贴到你项目的 CLAUDE.md
```

没有依赖，没有 setup 脚本，复制即用。

## 触发方式

- `/handoff` 或 `/handoff {下一步说明}`
- 自然语言："交接" "保存进度" "换个对话继续" "save progress" "session handoff"

## 设计原则

1. **只记非显而易见的** — 代码里能 grep 到的不记
2. **重"为什么"轻"是什么"** — 决策原因比决策本身重要
3. **Prompt 自包含** — 新 session 只需读 prompt 指定的文件就能开工
4. **不过度记忆** — 临时调试、已修复 bug、一次性查询不记
