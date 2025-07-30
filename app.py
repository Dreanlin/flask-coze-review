from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import threading  # 👈 加这个

# 调用批改函数
from coze_review import generate_review_html

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()
    username = data.get('username', 'anonymous')
    exer = data.get('exer', 'exer')
    filename = data.get('filename', f'{username}_{exer}.md')
    content = data.get('content', '')

    safe_filename = "".join(c for c in filename if c.isalnum() or c in ('_', '-', '.'))
    md_filepath = os.path.join(UPLOAD_DIR, safe_filename)

    with open(md_filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    # 👇 在后台线程中异步生成 HTML
    def generate_html():
        try:
            html_content = generate_review_html(md_filepath)
            html_filename = safe_filename.rsplit('.', 1)[0] + '.html'
            html_filepath = os.path.join(UPLOAD_DIR, html_filename)
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"[✔] 成功生成：{html_filename}")
        except Exception as e:
            print(f"[✘] HTML 生成失败：{e}")

    threading.Thread(target=generate_html).start()

    # 👇 马上返回响应
    return jsonify({
        'status': 'processing',
        'message': '报告正在后台生成，请稍后访问 HTML 页面',
        'html_url': f"/files/{safe_filename.rsplit('.', 1)[0]}.html"
    }), 202

@app.route('/files')
def list_files():
    return jsonify(os.listdir(UPLOAD_DIR))

@app.route('/files/<fname>')
def get_file(fname):
    safe_fname = "".join(c for c in fname if c.isalnum() or c in ('_', '-', '.'))
    filepath = os.path.join(UPLOAD_DIR, safe_fname)
    if not os.path.exists(filepath):
        return '文件不存在或还未生成', 404
    with open(filepath, encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}

if __name__ == '__main__':
    app.run()
