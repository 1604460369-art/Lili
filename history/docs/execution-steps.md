# 逐步执行步骤 — 公文校对助手

本文档是面向用户的**可操作执行指南**。每一步都有具体操作说明，按顺序做即可。

---

## 第一阶段：环境准备 ✅ 当前阶段

### 步骤 1：检查 Python 是否已安装
1. 按 `Win + R`，输入 `cmd`，回车
2. 在黑色窗口中输入 `python --version`，回车
3. 如果显示 `Python 3.x.x` → 跳到步骤 3
4. 如果显示"不是内部命令" → 继续步骤 2

### 步骤 2：安装 Python
1. 打开浏览器，访问 <https://www.python.org/downloads/>
2. 点击黄色 "Download Python" 按钮
3. 运行下载的安装程序
4. ⚠️ **重要**：安装界面第一页，勾选底部的 **"Add Python to PATH"**
5. 点击 "Install Now"，等待完成
6. 关闭安装界面，重复步骤 1 确认安装成功

### 步骤 3：安装项目依赖
1. 在 `d:\history\` 目录下，按住 Shift 键，在文件夹空白处右键
2. 选择"在此处打开 PowerShell"（或"在此处打开命令窗口"）
3. 输入以下命令，回车：
   ```
   pip install flask requests
   ```
4. 等待安装完成，看到 "Successfully installed..." 即为成功

### 步骤 4：获取 DeepSeek API Key
1. 打开 <https://platform.deepseek.com/>
2. 注册账号（用手机号或邮箱）
3. 登录后，进入"API Keys"页面
4. 点击"创建 API Key"，复制生成的密钥（以 `sk-` 开头）
5. 打开 `d:\history\config.json`，将密钥填入 `api_key` 字段

### 步骤 5：验证环境
1. 在 PowerShell 中运行：
   ```
   python src/test_api.py
   ```
2. 如果看到"API 连接成功"，说明环境搭建完成
3. 如果报错，查看 [故障排查](#故障排查) 章节

---

## 第二阶段：启动应用

### 步骤 1：启动后端服务
1. 在 `d:\history\` 目录下打开 PowerShell
2. 运行：
   ```
   python src/app.py
   ```
3. 看到 "Running on http://127.0.0.1:5000" 表示启动成功
4. **不要关闭这个窗口**

### 步骤 2：打开前端界面
1. 打开 Chrome 或 Edge 浏览器
2. 访问 <http://127.0.0.1:5000>
3. 看到校对界面即为成功

或者直接双击 `d:\history\start.bat`，自动完成以上两步。

---

## 第三阶段：日常使用

### 校对流程
1. 打开校对页面
2. 将待校对文本粘贴到左侧输入区
3. 点击 **🔍 一键校对**
4. 等待 3-8 秒，结果自动显示
5. 在原文中查看高亮标注，悬停看建议
6. 点击 **采纳** 逐条修正，或点击 **✅ 全部修正** 一次性修改
7. 修改后如有不满，点击 **↩ 撤销**
8. 校对完成，点击 👍 或 👎 留下评价

### 修改敏感词清单
1. 打开 `d:\history\sensitive-words.txt`
2. 每行添加一个词或短语
3. 保存文件
4. 重启后端服务（关闭 PowerShell 窗口，重新运行 `python src/app.py`）

---

## 故障排查

| 问题 | 可能原因 | 解决方法 |
|------|---------|---------|
| "pip 不是内部命令" | Python 未正确安装 | 重装 Python，确保勾选 "Add Python to PATH" |
| "ModuleNotFoundError" | 依赖未安装 | 重新运行 `pip install -r requirements.txt` |
| API 返回错误 | API Key 不正确 | 检查 config.json 中的 api_key |
| 浏览器打不开 | 后端未启动 | 确保 PowerShell 窗口显示 "Running on..." |
| 端口被占用 | 其他程序用了 5000 端口 | 修改 config.json 中的 port 值 |

---

## 版本历史

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-06-01 | v0.1 | 项目初始化，文档创建 |
