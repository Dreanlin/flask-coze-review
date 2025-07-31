import time, requests, markdown, os

# === 配置区（使用环境变量）===
COZE_BOT_ID = "7413241467499692073"
COZE_USER_ID = "123456789"
COZE_API_KEY = os.getenv("COZE_API_KEY", "")
HEADERS = {
    'Authorization': COZE_API_KEY,
    'Content-Type': 'application/json'
}

# def coze_query(prompt: str, content: str, wait_time=40) -> str:
#     url = 'https://api.coze.cn/v3/chat'
#     data = {
#         "bot_id": COZE_BOT_ID,
#         "user_id": COZE_USER_ID,
#         "stream": False,
#         "auto_save_history": True,
#         "additional_messages": [{
#             "role": "user",
#             "content": prompt + f"【{content}】",
#             "content_type": "text"
#         }]
#     }

#     try:
#         response = requests.post(url, headers=HEADERS, json=data)
#         response.raise_for_status()
#         result = response.json()
#     except Exception as e:
#         print(f"[错误] 请求失败：{e}")
#         return ""

#     time.sleep(wait_time)
#     try:
#         chat_id = result['data']['id']
#         conversation_id = result['data']['conversation_id']
#     except Exception:
#         print("[错误] 无法获取会话ID")
#         return ""

#     try:
#         res = requests.post('https://api.coze.cn/v3/chat/message/list',
#                             headers=HEADERS,
#                             params={'chat_id': chat_id, 'conversation_id': conversation_id})
#         res.raise_for_status()
#         messages = res.json().get('data', [])
#         return messages[0].get('content', '') if messages else ''
#     except Exception as e:
#         print(f"[错误] 获取消息失败：{e}")
#         return ""



def md_to_html(input_path: str):
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    html = markdown.markdown(text, extensions=['extra', 'codehilite', 'toc'])
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Coze Review</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.1.0/github-markdown.min.css">
  <style>body {{ max-width: 800px; margin: 2rem auto; }}</style>
</head>
<body class="markdown-body">
{html}
</body>
</html>
"""


def coze_query(prompt: str, content: str, max_wait=6, interval=25) -> str:
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
        chat_id = result['data']['id']
        conversation_id = result['data']['conversation_id']
    except Exception as e:
        print(f"[错误] 请求失败：{e}")
        return ""

    for i in range(0, max_wait, interval):
        try:
            time.sleep(interval)
            res = requests.post(
                'https://api.coze.cn/v3/chat/message/list',
                headers=HEADERS,
                params={'chat_id': chat_id, 'conversation_id': conversation_id}
            )
            res.raise_for_status()
            messages = res.json().get('data', [])
            if messages:
                content = messages[0].get('content', '')
                if content.strip():
                    return content
        except Exception as e:
            print(f"[尝试获取失败] {e}")
    print("[超时] 没能拿到结果")
    return ""


def generate_review_html(input_md_path: str):
    with open(input_md_path, 'r', encoding='utf-8') as f:
        input_markdown = f.read()

    base_name = os.path.splitext(os.path.basename(input_md_path))[0]
    md_output_path = os.path.join("uploads", base_name + "_review.md")

    overview_prompt = '''以下是我刚完成的英语翻译练习，内容包含：
                                - 中文原文
                                - 我的翻译
                                - 英文参考原文；我手动用 `**...**` 高亮了我觉得难或不确定的英文单词或短语，或者自己觉得需要借鉴的内容
                                - 我的注释，包括我的分析和疑问
                                
                                请你作为【雅思写作老师】，帮我完成以下任务：

                                1. 自动识别三段内容：中文原文、我的翻译、英文参考原文、我的注释；
                                2. 对比分析我与参考答案的差距，给出一个【英语能力简报】，包括翻译问题类型、常见错误、表达等级等；
                                3. 针对每一段翻译的问题，把值得我记忆和模仿使用的重点提取出来、并且每个重点配一个中文句子翻译练习，用到这个知识点；所有这些重点配新句子翻译练习，一起放在最后的【重点记忆】部分；
                                4. 如果你可以的话，请把这些内容整理成一个【布局格式好看】【内容直观】的markdown复习手册，我方便导出或复习。

                                这是一个结果文档的模板：【
                                # Translate quiz review--exercise 1
                                
                                ## 🧠 英语能力简报
                                
                                ### 🌟 总体评价
                                
                                你已经掌握了大部分基本结构，能够准确传达句意，尤其在段落组织和信息顺序方面表现良好。但在以下几个方面仍需提升：
                                
                                * **表达准确性**：部分词汇使用不够地道，例如 "laterly"（不存在）和 "Santa Poloz"（拼写错误）。
                                * **自然表达**：缺乏一些口语化、地道的表达，如 “learn the ropes”“baby of the family”等。
                                * **细节还原**：有时遗漏小细节或连词，影响语感。
                                * **时态选择**：大部分处理良好，但应注意过去完成与一般过去的区分。
                                
                                ### 📌 常见问题分类
                                
                                | 类型      | 示例                                        | 改进建议                            |
                                | ------- | ----------------------------------------- | ------------------------------- |
                                | 词语搭配错误  | "go back to school for getting..."        | 使用动词不定式 “to get” 更自然            |
                                | 拼写或地名错误 | "Santa Poloz"                             | 正确应为 “Saint Paul”               |
                                | 结构略显直译  | "being later is always better than never" | 参考固定表达 “Better late than never” |
                                | 强度表达缺失  | "a big family" vs "probably the biggest"  | 增强句式，加入副词修饰提升表达力                |
                                
                                ### 💬 表达等级评估
                                
                                * **词汇量**：中上，能使用一些高级词如 “deprived”“spoiled”。
                                * **句式变化**：中等，建议学习更多连接词、插入语等丰富句型。
                                * **语感与地道性**：仍有提升空间，可通过背诵原文句式改善。
                                
                                ---
                                <br>
                                ## 📚 重点造句练习
                                (挑出最优质的、不超过5个、可练习点即可) 】

                                下面是我的 `.md` 内容：'''
    review_prompt = '''
                        以下是我刚完成的英语翻译练习，内容包含：
                        - 中文原文
                        - 我的翻译
                        - 英文参考原文；我手动用 `**...**` 高亮了我觉得难或不确定的英文单词或短语，或者自己觉得需要借鉴的内容
                        - 我的注释，包括我的分析和疑问

                        请你帮我完成以下任务：
                        1. 针对我的翻译并结合我的注释和原文高亮，生成【批改意见】，包括【短语讲解】、【句法语法分析】、【原文表达是否/为什么更优秀/地道】等，直接加在对应的每段原文之后，你的回答以【中文+带高亮英文原文+批改意见】的顺序排布！原文本的内容不要省略，【我的注释】可以不写入了，直接融入【批改意见】中就行；
                        2. 生成的回复以一个简单清晰的markdown格式呈现，方便我直接导出或复习。模板为下面的内容，请完全按照这个模式做批改，包括【空行换行符】、【---分页符】：
                                <br>
                            ---
                            ### 段落 1
                                <br>
                            **中文**：我对父亲最早的一些记忆之一是他以前常在黎明时离家去慢跑。
                                <br>
                            **你的翻译**：One of my earliest memories about my father is that he used to leave home and go jogging at dawn.
                                <br>
                            **原文**：One of my earliest memories of Dad is that he would often leave the house at dawn **to** **go** jogging.
                                <br>
                            #### 批改意见
                                <br>
                            - **短语讲解**：“memories of”比“memories about”更常用和地道，“of”在这里表示所属关系，强调记忆与父亲的关联性更强。“leave the house”比“leave home”表述更具体生动，“house”明确指出是居住的房子这一具体地点；“to go jogging”比“and go jogging”更能清晰地表达“离家”的目的，“to”在这里表目的，使句子逻辑更连贯。
                                <br>
                            - **句法语法分析**：你的翻译和原文在整体句子结构上都是主系表结构。“One of my earliest memories...”是主语，“is”是系动词，“that...”引导的表语从句作表语。在语法上都正确，但原文在连接词和短语使用上更胜一筹。
                                <br>
                            - **原文表达是否/为什么更优秀/地道**：原文表达更优秀地道。首先用词上“memories of”“leave the house”“to go jogging”比你的表述更常用和精准；其次在句子连贯性上，“to go jogging”更清晰表达了离家的目的，比“and go jogging”更符合英语表达习惯。  
                                <br>
                            
                            '''

    with open(md_output_path, 'w', encoding='utf-8') as f:
        print("📋 正在生成总评...")
        summary = coze_query(overview_prompt, input_markdown)
        f.write(summary + '\n\n## 分段批改\n\n')

        print("📋 分段批改中...")
        for i, para in enumerate(input_markdown.split('---'), 1):
            print(f"🧩 处理段落 {i}...")
            result = coze_query(review_prompt, para.strip())
            if result.strip():
                f.write(f"\n\n{result}")

    return md_to_html(md_output_path)