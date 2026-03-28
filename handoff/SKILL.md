# `/handoff` — Session 交接工具

> 保存当前会话的关键上下文到 memory，并生成一段 prompt 让新 session 无缝衔接。两步完成：记忆持久化 + 交接 prompt 生成。

---

## 触发词

以下任一输入触发此工作流：

- `/handoff`
- `/handoff {简要说明下一步要做什么}`
- "交接" "保存进度" "换个对话继续" "save progress"
- "生成交接 prompt" "handoff" "session handoff"

---

## 工作流：3 步

### Step 1：Analyze — 提取当前会话上下文

回顾当前会话，提取以下信息：

| 维度 | 提取内容 |
|------|---------|
| **主题** | 这个 session 主要在做什么（1 句话） |
| **已完成** | 本次 session 完成了哪些具体工作（bullet list） |
| **未完成** | 哪些事情开始了但没做完，或计划要做但还没开始 |
| **关键发现** | 过程中发现的重要信息、数据、决策（非显而易见的） |
| **阻塞项** | 什么在阻塞进度（等人、等数据、技术问题） |
| **下一步** | 紧接着应该做什么（按优先级排序） |
| **关键文件** | 本次 session 涉及的核心文件路径 |

**提取原则：**
- 只记非显而易见的信息 — 代码里能 grep 到的不需要记
- 重点记"为什么"而不是"是什么" — 决策原因比决策本身更重要
- 如果有未部署的代码改动，标注清楚哪些文件改了、在本地还是服务器
- 如果用户提供了 `$ARGUMENTS`，将其作为"下一步"的优先指引

---

### Step 2：Memory — 持久化到 memory 系统

根据 Step 1 的分析，决定 memory 操作：

#### 2A：检查现有 memory

读取 `MEMORY.md` 索引，检查是否有相关的现有 memory 文件需要更新而非新建。

#### 2B：写入/更新 memory

按以下规则决定写什么：

| 情况 | 操作 |
|------|------|
| 涉及正在进行的软件项目 | 更新对应的 `project` memory（如 `orion-mvp-sprint.md`） |
| 发现了新的用户偏好/工作习惯 | 创建/更新 `feedback` memory |
| 产生了新的项目知识（非代码可读的） | 创建/更新 `project` memory |
| 发现了新的外部资源/参考链接 | 创建/更新 `reference` memory |
| 了解到用户新的角色/背景信息 | 更新 `user` memory |

**Memory 写入规则：**
- 绝对日期，不用相对日期（"今天" → "2026-03-28"）
- 写入后更新 `MEMORY.md` 索引
- 不重复已有 memory 内容，优先更新现有文件
- 不保存代码细节（那是 CLAUDE.md 和 git 的职责）
- 项目 memory 的 description 要具体到能判断何时相关

#### 2C：检查项目 CLAUDE.md

如果本次会话产生了应该写入项目 CLAUDE.md 的技术知识（架构决策、部署流程、API 端点等），提醒用户并询问是否要更新。不自动写入。

完成后输出：
```
Memory 操作：
  ✏️ 更新：{file} — {变更摘要}
  ➕ 新建：{file} — {内容摘要}
  ⏭️ 跳过：无需新增 memory（原因）

💡 建议更新 CLAUDE.md：{file}（如果适用）
```

---

### Step 3：Prompt — 生成交接 prompt

生成一段可以直接复制粘贴到新 session 的 prompt。

**Prompt 结构模板：**

```
复制这段给新 session：

继续 {主题简述}。读这些文件了解上下文：

1. {memory 文件路径}（{该文件提供什么上下文}）
2. {关键项目文件}（{该文件提供什么上下文}）
3. ...（按重要性排序，最多 5 个）

上次停在：{精确描述停在哪里，包含具体的文件名、函数名、数据状态}

下一步：
1. {最高优先级任务}
2. {次优先级任务}
...

{如果有阻塞项：阻塞：{具体阻塞描述}}
{如果有关键数据/发现需要带到新 session：关键数据：{数据}}
```

**Prompt 生成规则：**
- 文件引用使用相对于工作目录的路径（不用绝对路径）
- "上次停在"要具体到可操作的程度 — 新 session 的 Claude 读完后应该能立即动手
- 不要放完整的代码片段（新 session 会自己读文件）
- 如果有未提交的代码改动，在 prompt 里标注
- 如果涉及服务器状态，标注服务器当前状态
- "下一步"按优先级排序，每条 1 行，可操作
- 整个 prompt 控制在 30 行以内 — 太长反而降低信噪比

**输出格式：**

用代码块包裹最终的 prompt，方便用户一键复制：

```
📋 复制以下内容到新 session：
```

然后输出 prompt 代码块。

---

## 设计原则

1. **Memory 是跨 session 的**，prompt 是给下一个 session 的。两者互补：memory 提供背景，prompt 提供即时指令
2. **Prompt 要自包含**：新 session 的 Claude 只需要读 prompt 里指定的文件就能开始工作，不需要额外搜索
3. **不过度记忆**：临时的调试过程、已修复的 bug、一次性的数据查询不需要记忆
4. **版本快照**：如果项目有未提交的改动，prompt 里要标注，防止新 session 基于过时代码工作

---

## 前置要求

此 skill 依赖 Claude Code 的 auto memory 系统。确保你的 CLAUDE.md 已配置 memory 路径和读写规则。如果没有 memory 系统，Step 2 将跳过，只生成交接 prompt。

---

## 示例输出

```
Memory 操作：
  ✏️ 更新：orion-mvp-sprint.md — LH-DAO schema 已拉取，5 个 mutation 映射关系确认
  ⏭️ 跳过：无需新建 memory

📋 复制以下内容到新 session：
```

````
继续 Orion LH-DAO 集成。读这些文件了解上下文：

1. memory 里的 orion-mvp-sprint.md（完整进度）
2. Projects/orion/src/data_hub/lhdao_client.py（需要重写的 5 个 push 方法）
3. Projects/orion/TODOS.md（待办清单）

上次停在：已从 LH-DAO GraphQL introspection 拉到完整 mutation schema。5 个 push 方法的映射已确认：
- updateOrderStatus → updateOrder(where: OrderWhereUniqueInput, data: OrderUpdateInput)
- notifyRewardSettlement → submitPayHash(id, transaction, payMethond, transactionAddress)
- syncContentUrls → submitPost(orderId, content: JSON)
- syncQCResults → updateSubmissionStatus + confirmSubmissions
- updateKOLCredit → updateTier(userId: String, tier: String)

下一步：
1. 拿到 LH-DAO auth token → 配 .env
2. 重写 lhdao_client.py 的 5 个 push 方法（用真实 mutation 名）
3. 部署到服务器测试
4. 历史数据回填
````
