"""
公文校对助手 — Flask 后端主程序

启动方式：在项目目录下运行 python src/app.py
访问地址：http://127.0.0.1:5000
"""

import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from flask import Flask, jsonify, render_template, request

# ============================================
# 初始化
# ============================================

app = Flask(__name__, static_folder="static", template_folder="templates")

# 项目根目录
ROOT = Path(__file__).parent.parent

# 加载配置
with open(ROOT / "config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

API_KEY = config.get("api_key", "")
API_URL = config.get("api_url", "https://api.deepseek.com/v1/chat/completions")
MODEL = config.get("model", "deepseek-chat")
MAX_TEXT_LENGTH = config.get("max_text_length", 5000)

# 加载敏感词清单
SENSITIVE_WORDS = []
sensitive_path = ROOT / "sensitive-words.txt"
if sensitive_path.exists():
    with open(sensitive_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # 跳过空行和注释行
            if not line or line.startswith("#"):
                continue
            # 支持 "错误写法 -> 正确写法" 格式
            if "->" in line:
                parts = line.split("->", 1)
                wrong = parts[0].strip()
                correct = parts[1].strip()
                if wrong:
                    SENSITIVE_WORDS.append((wrong, correct))
            else:
                word = line.strip()
                if word:
                    SENSITIVE_WORDS.append((word, ""))

print(f"[OK] 已加载 {len(SENSITIVE_WORDS)} 条敏感词")

# ============================================
# 校对 Prompt
# ============================================

PROOFREAD_PROMPT = """你是一位资深的政务公文校对专家。请仔细检查以下文本，找出所有问题。

检查范围：
1. 错别字：同音字、形近字误用（特别注意"的/地/得"、"做/作"、"即/既"等）
2. 语病：搭配不当、句式杂糅、成分残缺、重复啰嗦
3. 用词规范：不符合政务公文/新闻稿件写作规范的表述
4. 标点错误：中英文标点混用、引号不匹配等

要求：
- 只标注确实有问题的部分，不要过度纠正
- 对于不确定的问题可以不标注
- 如果文本没有任何问题，返回空列表

请严格按照以下JSON格式返回（只返回JSON，不要其他内容）：
{
  "issues": [
    {
      "type": "typo",
      "original": "原文中有问题的片段（10个字以内）",
      "replace_with": "修改后的文字",
      "reason": "简要说明为什么这样修改（15字以内）"
    }
  ]
}

type 可选值：typo（错别字）、grammar（语病）、wording（用词不当）、punctuation（标点错误）

注意：
- original 必须是原文中实际出现的文字片段，不要自己概括
- 如果同一个错误跨多个字，original 中要包含连续的错误文字
- 保持 original 尽可能短且唯一，方便精确定位"""


# ============================================
# 核心功能：本地敏感词匹配
# ============================================

def match_sensitive_words(text):
    """在文本中查找敏感词，返回问题列表"""
    issues = []
    seen_positions = set()  # 避免同一位置重复标记

    for wrong, correct in SENSITIVE_WORDS:
        # 用正则忽略大小写做全词匹配
        try:
            pattern = re.compile(re.escape(wrong), re.IGNORECASE)
            for match in pattern.finditer(text):
                start = match.start()
                end = match.end()

                # 检查是否与已有问题重叠
                positions = set(range(start, end))
                if positions & seen_positions:
                    continue

                seen_positions.update(positions)
                issues.append({
                    "type": "sensitive",
                    "original": text[start:end],
                    "replace_with": correct if correct else f"（请确认此表述）",
                    "reason": f"敏感词：{wrong}" + (f"，建议改为「{correct}」" if correct else "，请核实"),
                    "position": {"start": start, "end": end},
                })
        except re.error:
            # 如果有正则特殊字符，退化为简单查找
            idx = text.find(wrong)
            if idx >= 0:
                positions = set(range(idx, idx + len(wrong)))
                if not (positions & seen_positions):
                    seen_positions.update(positions)
                    issues.append({
                        "type": "sensitive",
                        "original": wrong,
                        "replace_with": correct if correct else f"（请确认此表述）",
                        "reason": f"敏感词：{wrong}" + (f"，建议改为「{correct}」" if correct else "，请核实"),
                        "position": {"start": idx, "end": idx + len(wrong)},
                    })

    return issues


# ============================================
# 核心功能：调用 DeepSeek API 校对
# ============================================

def call_ai_proofread(text):
    """调用 DeepSeek API 做智能校对"""
    if not API_KEY or API_KEY == "在此填入你的DeepSeek-API-Key":
        return None, "未配置 API Key，请在 config.json 中填写"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": PROOFREAD_PROMPT},
            {"role": "user", "content": text},
        ],
        "temperature": 0.1,
        "max_tokens": 4096,
    }

    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    except requests.exceptions.ConnectionError:
        return None, "网络连接失败，请检查网络"
    except requests.exceptions.Timeout:
        return None, "API 响应超时，请重试"
    except Exception as e:
        return None, f"请求异常: {str(e)}"

    if resp.status_code != 200:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text[:300]
        return None, f"API 返回错误 (HTTP {resp.status_code}): {detail}"

    try:
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return None, "API 返回格式异常"

    return parse_ai_response(content, text)


def parse_ai_response(content, original_text):
    """解析 AI 返回的 JSON，并匹配原文位置"""
    # 尝试提取 JSON
    json_str = content.strip()

    # 去掉可能的 markdown 代码块标记
    json_str = re.sub(r'^```(?:json)?\s*', '', json_str)
    json_str = re.sub(r'\s*```$', '', json_str)

    try:
        data = json.loads(json_str)
        raw_issues = data.get("issues", [])
    except json.JSONDecodeError:
        # 尝试用正则从文本中提取 JSON
        match = re.search(r'\{[\s\S]*"issues"[\s\S]*\]\s*\}', content)
        if match:
            try:
                data = json.loads(match.group())
                raw_issues = data.get("issues", [])
            except json.JSONDecodeError:
                return [], f"AI 返回内容无法解析: {content[:200]}"
        else:
            return [], f"AI 返回内容无法解析: {content[:200]}"

    # 为每条问题找到在原文中的位置
    issues = []
    used_ranges = set()

    for item in raw_issues:
        original = item.get("original", "")
        if not original:
            continue

        # 在原文中查找位置
        positions = find_all_positions(original_text, original)
        if not positions:
            continue

        # 选择第一个未被占用的位置
        placed = False
        for start, end in positions:
            pos_range = set(range(start, end))
            if not (pos_range & used_ranges):
                used_ranges.update(pos_range)
                issues.append({
                    "type": item.get("type", "typo"),
                    "original": original,
                    "replace_with": item.get("replace_with", ""),
                    "reason": item.get("reason", ""),
                    "position": {"start": start, "end": end},
                })
                placed = True
                break

        if not placed:
            # 所有位置都被占，跳过
            continue

    return issues, None


def find_all_positions(text, substring):
    """在文本中查找子串的所有位置"""
    positions = []
    start = 0
    sub_lower = substring.lower()
    text_lower = text.lower()
    while True:
        idx = text_lower.find(sub_lower, start)
        if idx == -1:
            break
        positions.append((idx, idx + len(substring)))
        start = idx + 1
    return positions


# ============================================
# API 路由
# ============================================

@app.route("/")
def index():
    """返回前端页面"""
    return app.send_static_file("index.html")


@app.route("/api/check", methods=["POST"])
def check():
    """文本校对接口"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "请求数据为空"}), 400

    text = data.get("text", "").strip()
    if not text:
        return jsonify({"success": False, "error": "文本内容为空"}), 400

    if len(text) > MAX_TEXT_LENGTH:
        return jsonify({
            "success": False,
            "error": f"文本过长（{len(text)}字），单次最多 {MAX_TEXT_LENGTH} 字"
        }), 400

    # 1. 本地敏感词匹配
    local_issues = match_sensitive_words(text)

    # 2. AI 校对
    ai_issues, ai_error = call_ai_proofread(text)

    if ai_error:
        # AI 失败时至少返回本地敏感词结果
        all_issues = local_issues
    else:
        # 合并 AI 结果和本地结果，去重
        occupied = set()
        for issue in local_issues:
            occupied.update(range(issue["position"]["start"], issue["position"]["end"]))

        all_issues = local_issues[:]
        for ai_issue in ai_issues:
            pos_range = set(range(ai_issue["position"]["start"], ai_issue["position"]["end"]))
            if not (pos_range & occupied):
                occupied.update(pos_range)
                all_issues.append(ai_issue)

    # 3. 按位置排序
    all_issues.sort(key=lambda x: x["position"]["start"])

    # 4. 为每个问题分配 ID
    for i, issue in enumerate(all_issues):
        issue["id"] = i + 1

    # 5. 统计
    summary = {
        "total": len(all_issues),
        "typo": sum(1 for i in all_issues if i["type"] == "typo"),
        "grammar": sum(1 for i in all_issues if i["type"] == "grammar"),
        "wording": sum(1 for i in all_issues if i["type"] == "wording"),
        "punctuation": sum(1 for i in all_issues if i["type"] == "punctuation"),
        "sensitive": sum(1 for i in all_issues if i["type"] == "sensitive"),
    }

    return jsonify({
        "success": True,
        "issues": all_issues,
        "summary": summary,
        "ai_error": ai_error,  # 告诉前端 AI 是否有问题
    })


@app.route("/api/feedback", methods=["POST"])
def feedback():
    """用户反馈接口"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "请求数据为空"}), 400

    rating = data.get("rating", "")
    if rating not in ("good", "bad"):
        return jsonify({"success": False, "error": "无效的评价"}), 400

    feedback_entry = {
        "rating": rating,
        "text_length": data.get("text_length", 0),
        "note": data.get("note", ""),
        "timestamp": datetime.now().isoformat(),
    }

    # 追加到反馈文件
    feedback_path = ROOT / "feedback.jsonl"
    with open(feedback_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(feedback_entry, ensure_ascii=False) + "\n")

    return jsonify({"success": True, "message": "感谢反馈！"})


# ============================================
# 启动入口
# ============================================

if __name__ == "__main__":
    port = config.get("port", 5000)
    debug = config.get("debug", False)

    print("=" * 50)
    print("  公文校对助手 -- 后端服务")
    print("=" * 50)
    print()
    print(f"  访问地址: http://127.0.0.1:{port}")
    print(f"  API Key:  {'已配置' if API_KEY and 'sk-' in str(API_KEY) else '未配置'}")
    print(f"  敏感词:  {len(SENSITIVE_WORDS)} 条")
    print()
    print("  在浏览器中打开上面的地址即可使用")
    print("  按 Ctrl+C 停止服务")
    print()

    app.run(host="127.0.0.1", port=port, debug=debug)
