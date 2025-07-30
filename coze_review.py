import time
import requests
import markdown
import os

# === 配置区 ===
COZE_BOT_ID = "7413241467499692073"
COZE_USER_ID = "123456789"
COZE_API_KEY = "Bearer pat_e95xHsN1KhMT0DQZ5ehaxbF6HkrSWRkR46r3YI4MFsbzdBn9hMJhpQWZQqAvu0Jh"
HEADERS = {
    'Authorization': COZE_API_KEY,
    'Content-Type': 'application/json'
}

# === 请求 Coze 主函数 ===
def coze_query(prompt: str, content: str, wait_time=40) -> str:
    url = 'https://api.coze.cn/v3/chat'

    data = {
        "bot_id": COZE_BOT_ID,
        "user_id": COZE_USER_ID,
        "stream": False,
        "auto_save_history": True,
        "additional_messages": [{
            "role": "user",
            "content": prompt + f"【{content}】",
            "content_type": "text"
        }]
    }

    try:
        response = requests.post(url, headers=HEADERS, json=data)
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        print(f"[错误] 请求失败：{e}")
        return ""

    time.sleep(wait_time)

    try:
        chat_id = result['data']['id']
        conversation_id = result['data']['conversation_id']
    except Exception:
        print("[错误] 无法获取 conversation_id 或 chat_id")
        return ""

    try:
        msg_url = 'https://api.coze.cn/v3/chat/message/list'
        params = {'chat_id': chat_id, 'conversation_id': conversation_id}
        res = requests.post(msg_url, headers=HEADERS, params=params)
        res.raise_for_status()
        messages = res.json().get('data', [])
        return messages[0].get('content', '') if messages else ''
    except Exception as e:
        print(f"[错误] 获取消息失败：{e}")
        return ""

# === Markdown ➜ HTML 转换 ===
def md_to_html(input_path: str):
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    html = markdown.markdown(text, extensions=['extra', 'codehilite', 'toc'])

    html_page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Coze Review</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.1.0/github-markdown.min.css">
  <style>
    body {{ max-width: 800px; margin: 2rem auto; padding: 0 1rem; }}
    .markdown-body {{ box-sizing: border-box; }}
  </style>
</head>
<body class="markdown-body">
{html}
</body>
</html>
"""
    print(f"✅ 已生成 HTML 文本")
    return html_page

# === 生成批改报告主入口 ===
def generate_review_html(input_md_path: str):
    # 读取原始 Markdown
    with open(input_md_path, 'r', encoding='utf-8') as f:
        input_markdown = f.read()

    # 临时批改报告 Markdown 文件路径
    base_name = os.path.splitext(os.path.basename(input_md_path))[0]
    md_output_path = os.path.join("uploads", base_name + "_review.md")

    overview_prompt = '''（同上）'''
    review_prompt = '''（同上）'''

    # 写入批改报告 Markdown
    with open(md_output_path, 'w', encoding='utf-8') as f:
        print("📋 正在生成总评...")
        summary = coze_query(overview_prompt, input_markdown)
        f.write(summary + '\n\n')

        print("📋 开始分段批改...")
        for i, para in enumerate(input_markdown.split('---'), 1):
            print(f"⏳ 正在处理段落 {i}...")
            result = coze_query(review_prompt, para.strip())
            if result.strip():
                f.write(f"\n\n### 段落 {i} 批改\n\n")
                f.write(result)
            else:
                print(f"⚠️ 段落 {i} 无有效回复，已跳过")

    # 生成 HTML 内容
    return md_to_html(md_output_path)
