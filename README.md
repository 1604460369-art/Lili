# 🔍 公文校对助手

轻量级 AI 校对工具，专为政务/媒体用户设计。一键检查公文、新闻稿中的错别字、语病和敏感词。

**技术栈：Python + Flask + DeepSeek API**

---

## 快速开始

### 1. 配置 API Key
- 注册 [DeepSeek](https://platform.deepseek.com/)，获取 API Key
- 打开 `config.json`，将 Key 填入 `api_key` 字段

### 2. 安装依赖
```bash
pip install flask requests
```

### 3. 启动
- 双击 `start.bat`，或者
- 在项目目录下运行 `python src/app.py`
- 浏览器打开 `http://127.0.0.1:5000`

---

## 功能

| 功能 | 说明 |
|------|------|
| 🔍 一键校对 | 粘贴文本，点一下，自动检查 |
| ✨ 错误高亮 | 问题位置用颜色标注，悬停看建议 |
| ✅ 一键修正 | 确认后自动替换，支持撤销 |
| 📋 敏感词匹配 | 离线扫描本地清单，不联网也能跑 |
| 💬 用户反馈 | 👍👎 一键评价，记录到本地 |

---

## 项目结构

```
├── start.bat                  # 启动脚本
├── config.json                # 配置文件（API Key）
├── sensitive-words.txt        # 敏感词清单
├── requirements.txt           # Python 依赖
├── README.md                  # 本文件
├── docs/                      # 项目文档
├── dev-journal/               # 开发日志
└── src/
    ├── app.py                 # Flask 后端
    └── static/
        └── index.html         # 前端界面
```

---

## 修改敏感词清单

编辑 `sensitive-words.txt`，每行一个词。支持 `错误写法 -> 正确写法` 格式。保存后重启服务生效。

---

## 常见问题

**Q: 启动后浏览器打不开？**
A: 确认 PowerShell 窗口显示 `Running on http://127.0.0.1:5000`，然后手动浏览器输入这个地址。

**Q: AI 服务不可用？**
A: 检查 `config.json` 中的 API Key 是否填写正确，以及 DeepSeek 账户是否有余额。

**Q: 如何更新依赖？**
A: `pip install -r requirements.txt`

---

## 许可

个人使用，自由修改。
