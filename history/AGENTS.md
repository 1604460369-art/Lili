# 公文校对助手 — 项目总指引

## 项目简介
一款运行在 Windows 上的轻量级 AI 校对工具，面向政务/媒体用户，提供公文、稿件错敏词的一键校对、错误高亮定位和修改建议生成。

- **用户身份**：不懂代码的小白用户
- **AI 方案**：调用云端 DeepSeek API
- **使用范围**：单机个人使用

---

## 标准文档路径

| 文档 | 路径 | 说明 |
|------|------|------|
| 需求规格 | [docs/requirements.md](docs/requirements.md) | 功能需求、用户场景、验收标准 |
| 技术方案 | [docs/technical.md](docs/technical.md) | 技术选型、架构设计、API 设计 |
| 设计规范 | [docs/design.md](docs/design.md) | 配色、布局、交互规范 |
| 执行步骤 | [docs/execution-steps.md](docs/execution-steps.md) | 用户可操作的逐步执行指南 |

---

## 项目结构

```
d:\history\
├── AGENTS.md                  # 本文件 — 项目总指引
├── docs/                      # 标准文档
│   ├── requirements.md
│   ├── technical.md
│   ├── design.md
│   └── execution-steps.md
├── dev-journal/               # 开发日志（每天一条）
│   └── YYYY-MM-DD.md
├── sensitive-words.txt        # 敏感词清单（一行一词）
├── src/                       # 源代码
│   ├── app.py                 # Flask 后端主程序
│   ├── static/                # 前端静态文件
│   │   └── index.html         # 单页前端界面
│   └── templates/             # Flask 模板（如需要）
├── requirements.txt           # Python 依赖清单
├── start.bat                  # Windows 启动脚本（双击运行）
└── config.json                # 配置文件（API Key 等）
```

---

## 开发工作原则

### 1. 逐步推进，每步确认
- 将开发分为 6 个阶段（详见 [docs/execution-steps.md](docs/execution-steps.md)）
- 每个阶段完成后**暂停**，等用户确认没问题再继续
- 不要一口气写大量代码后再给用户看

### 2. 稳定安全优先
- 优先保证能用，再考虑优化
- 代码尽量简单、注释充分
- API Key 等敏感信息不硬编码，放在 config.json 中（不提交到 git）
- 所有外部调用做好错误处理，给用户友好的提示

### 3. 面向小白的沟通方式
- 避免使用技术黑话
- 每步操作给出具体的、可操作的动作描述（"打开这个文件"、"复制粘贴这段"、"双击运行"）
- 出现问题时，先解释原因再给解决方案

### 4. 开发日志维护
- 每天工作结束后更新 `dev-journal/` 下的当日日志
- 记录：完成了什么、待办事项、遇到的问题、给用户的备注
- 格式参考 [dev-journal/2026-06-01.md](dev-journal/2026-06-01.md)

---

## 当前状态

- **当前阶段**：第一阶段 — 项目骨架搭建
- **下一阶段**：第二阶段 — 环境搭建与 API 验证
- **最近更新**：2026-06-01 — 初始化项目结构
