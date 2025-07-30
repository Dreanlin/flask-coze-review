# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import os

# app = Flask(__name__)
# CORS(app)

# @app.route('/')
# def hello_world():
#     return 'Hello from Flask!'

# UPLOAD_DIR = 'uploads'
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# @app.route('/upload', methods=['POST'])
# def upload():
#     data = request.get_json()
#     username = data.get('username', 'anonymous')
#     exer = data.get('exer', 'exer')
#     filename = data.get('filename', f'{username}_{exer}.md')
#     content = data.get('content', '')

#     safe_filename = "".join(c for c in filename if c.isalnum() or c in ('_', '-', '.'))
#     filepath = os.path.join(UPLOAD_DIR, safe_filename)
#     with open(filepath, 'w', encoding='utf-8') as f:
#         f.write(content)
#     return jsonify({'status': 'ok', 'filename': safe_filename})



from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# 假设你把这个函数放在 coze_review.py 里
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

    # 保存 Markdown 文件
    with open(md_filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    try:
        # 调用你已有的 Coze 脚本进行批改并生成 HTML 字符串
        html_content = generate_review_html(md_filepath)

        # 保存 HTML 到本地
        html_filename = safe_filename.rsplit('.', 1)[0] + '.html'
        html_filepath = os.path.join(UPLOAD_DIR, html_filename)
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return jsonify({
            'status': 'ok',
            'md_file': safe_filename,
            'html_file': html_filename
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/files')
def list_files():
    files = os.listdir(UPLOAD_DIR)
    return jsonify(files)

@app.route('/files/<fname>')
def get_file(fname):
    safe_fname = "".join(c for c in fname if c.isalnum() or c in ('_', '-', '.'))
    with open(os.path.join(UPLOAD_DIR, safe_fname), encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'text/markdown; charset=utf-8'}

if __name__ == '__main__':
    app.run()