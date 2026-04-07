## Memory 系统

Claude Code 有持久化记忆能力。当用户说"记住这个"、"记一下"、"以后别这样"时，将信息存入 memory 文件。

### Memory 文件规范

- 路径：`~/.claude/projects/{项目路径}/memory/`
- 索引：`MEMORY.md`（每次启动自动加载，限 200 行）
- 每条 memory 一个文件，YAML frontmatter 包含 name、description、type

### 四种类型

| 类型 | 用途 |
|------|------|
| `user` | 用户角色、偏好、技术背景 |
| `feedback` | 用户纠正过的行为（附 Why + How to apply） |
| `project` | 代码/git 里看不到的项目背景和决策 |
| `reference` | 外部资源指针（Linear、Slack、文档链接） |

### 规则

- 存之前先检查是否已有相关 memory，有则更新，无则新建
- feedback 和 project 类型必须写 **Why** 和 **How to apply**
- 不存代码里能看到的、git log 能查到的、临时调试信息
- MEMORY.md 索引每条一行，< 150 字符
