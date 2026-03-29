from flask import Flask, request, render_template
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs('uploads', exist_ok=True)

@app.route('/')
def index():
    return '''
    <form action="/upload" method="POST" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit">上传</button>
    </form>
    '''

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file.filename == '':
        return "没有选择文件"
    
    file.save(os.path.join('uploads', file.filename))
    return f"上传成功: {file.filename}"

if __name__ == '__main__':
    app.run(debug=True)