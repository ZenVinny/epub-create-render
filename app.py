import os
import json
import uuid
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from scripts.extract_kakao import extract_kakaopage_chapter
from scripts.epub_builder import build_epub

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

STATE_FILE = 'form_state.json'

def load_state():
    """Load saved form state from JSON file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_state(data):
    """Save form state to JSON file."""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

ALLOWED_EXTENSIONS = {'txt', 'mhtml', 'html'}

def allowed_file(filename):
    if '.' not in filename:
        return True
    return filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    state = load_state()
    return render_template('kakao.html', state=state)

@app.route('/process', methods=['POST'])
def process():
    output_format = request.form.get('format', 'epub')
    novel_title = request.form.get('title', 'KakaoPage Novel')

    # Save state for next time
    save_state({
        'title': novel_title,
        'format': output_format,
    })

    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        flash('Please select at least one file.')
        return redirect(url_for('index'))

    chapters = []
    for file in files:
        if not allowed_file(file.filename):
            flash(f'Invalid file type: {file.filename}')
            continue
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        try:
            text = extract_kakaopage_chapter(filepath)
            chapter_title = os.path.splitext(filename)[0]
            chapters.append({'title': chapter_title, 'text': text})
        except Exception as e:
            flash(f'Error processing {filename}: {str(e)}')
        finally:
            os.remove(filepath)

    if not chapters:
        flash('No valid chapters extracted.')
        return redirect(url_for('index'))

    uid = uuid.uuid4().hex[:8]
    base_name = secure_filename(novel_title.replace(' ', '_'))
    if output_format == 'epub':
        out_filename = f"{base_name}_{uid}.epub"
        out_path = os.path.join(app.config['DOWNLOAD_FOLDER'], out_filename)
        build_epub(chapters, novel_title, out_path)
    else:
        out_filename = f"{base_name}_{uid}.txt"
        out_path = os.path.join(app.config['DOWNLOAD_FOLDER'], out_filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            for ch in chapters:
                f.write(f"{ch['title']}\n{'='*40}\n{ch['text']}\n\n")

    return render_template('kakao_result.html', filename=out_filename, title=novel_title)

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)