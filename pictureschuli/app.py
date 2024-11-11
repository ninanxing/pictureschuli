from flask import Flask, render_template, request, send_file, jsonify, url_for
from image_processor import ImageProcessor
import os
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 最大上传限制

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    timestamp = str(int(time.time()))
    input_filename = f"{timestamp}_input{os.path.splitext(file.filename)[1]}"
    output_filename = f"{timestamp}_output{os.path.splitext(file.filename)[1]}"
    
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    file.save(input_path)
    
    try:
        # 获取处理参数
        crop_box = None
        if all(x in request.form and request.form[x] for x in ['crop_left', 'crop_top', 'crop_right', 'crop_bottom']):
            crop_box = (
                int(request.form['crop_left']),
                int(request.form['crop_top']),
                int(request.form['crop_right']),
                int(request.form['crop_bottom'])
            )
        
        new_size = None
        if request.form.get('width') and request.form.get('height'):
            new_size = (int(request.form['width']), int(request.form['height']))
        
        # 处理压缩参数
        compression_type = request.form.get('compressionType', 'quality')
        quality = int(request.form.get('quality', 85))
        target_size = None
        
        if compression_type == 'size':
            size = float(request.form.get('targetSize', 500))
            unit = request.form.get('sizeUnit', 'KB')
            # 转换为字节
            multiplier = 1024 * 1024 if unit == 'MB' else 1024
            target_size = int(size * multiplier)
        
        # 处理图片
        processor = ImageProcessor()
        processor.process_image(
            input_path=input_path,
            output_path=output_path,
            crop_box=crop_box,
            new_size=new_size,
            quality=quality,
            target_size=target_size
        )
        
        return send_file(output_path, as_attachment=True, download_name=f"processed_{file.filename}")
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        except:
            pass

if __name__ == '__main__':
    app.run(debug=True) 