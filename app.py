from flask import Flask, render_template, request, jsonify
import os
import cv2
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)

# ========== 配置 ==========
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ========== 加载 YOLO 模型 ==========
print("正在加载 YOLO 模型...")
model = YOLO('yolov8n.pt')
print("YOLO 模型加载完成！")


# ========== 辅助函数 ==========
def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def detect_objects(image_path):
    """
    对图片进行 YOLO 检测
    返回检测结果列表
    """
    # 读取图片
    img = cv2.imread(image_path)
    
    # 运行 YOLO 检测
    results = model(img)
    
    # 提取检测结果
    detections = []
    
    for r in results:
        boxes = r.boxes
        if boxes is not None:
            for box in boxes:
                # 获取边界框坐标
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                # 获取置信度
                conf = box.conf[0].item()
                # 获取类别索引
                cls = int(box.cls[0].item())
                # 获取类别名称
                class_name = model.names[cls]
                
                detections.append({
                    'class': class_name,
                    'confidence': round(conf, 3),
                    'bbox': [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)]
                })
    
    return detections


# ========== 路由 ==========
@app.route('/')
def index():
    """显示上传页面"""
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """处理上传的文件并进行 YOLO 检测"""
    
    # 1. 检查是否有文件被上传
    if 'file' not in request.files:
        return jsonify({'error': '没有文件部分'}), 400
    
    file = request.files['file']
    
    # 2. 检查是否选择了文件
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    # 3. 检查文件类型是否允许
    if not allowed_file(file.filename):
        return jsonify({'error': '文件类型不允许，请上传图片 (png, jpg, jpeg, gif)'}), 400
    
    # 4. 保存文件
    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # 5. 进行 YOLO 检测
    try:
        detections = detect_objects(filepath)
    except Exception as e:
        return jsonify({'error': f'检测失败: {str(e)}'}), 500
    
    # 6. 返回检测结果
    return jsonify({
        'success': True,
        'filename': filename,
        'detections': detections,
        'count': len(detections)
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)