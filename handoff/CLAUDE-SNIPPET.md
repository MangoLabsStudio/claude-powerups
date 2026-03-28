## Skill: `/handoff`

When the user says `/handoff`, `/handoff {下一步说明}`, "交接", "保存进度", "换个对话继续", "save progress", "生成交接 prompt", or "session handoff", execute the workflow defined in `.claude/skills/handoff/SKILL.md`.

**What it does:** 保存当前会话的关键上下文到 memory 系统，并生成一段可直接复制粘贴到新 session 的 prompt，实现无缝衔接。纯 Prompt 驱动，无脚本。

**Quick reference — 3 steps:**

1. **Analyze**: 回顾当前会话，提取主题、已完成、未完成、关键发现、阻塞项、下一步、关键文件
2. **Memory**: 检查现有 memory → 更新/新建相关 memory 文件 → 更新 MEMORY.md 索引。如有项目 CLAUDE.md 需更新则提醒
3. **Prompt**: 生成 ≤ 30 行的交接 prompt（文件引用 + 停在哪里 + 下一步），用代码块包裹方便复制

Key design: memory 提供跨 session 背景，prompt 提供即时指令。两者互补，不重复。

**前置要求：** 依赖 Claude Code auto memory 系统（memory 路径 + MEMORY.md 索引）。无 memory 时只生成 prompt。

For full instructions, read `.claude/skills/handoff/SKILL.md`.
