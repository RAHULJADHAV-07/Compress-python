from flask import Flask, render_template, request, send_file, jsonify
import os
from werkzeug.utils import secure_filename
from specialized_pdf_compressor import alternative_pdf_compression
from image_compressor import compress_jpg, compress_png
from video_compressor import compress_video

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size for videos

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress/pdf', methods=['POST'])
def compress_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Generate output filename
        output_filename = f'compressed_{filename}'
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        # Compress PDF
        method = request.form.get('method', 'auto')
        compressed_path = alternative_pdf_compression(input_path, output_path, method)
        
        # Get file sizes for comparison
        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(compressed_path)
        reduction = ((original_size - compressed_size) / original_size) * 100
        
        # Clean up input file
        os.remove(input_path)
        
        # Return compression stats and file
        response = jsonify({
            'original_size': original_size,
            'compressed_size': compressed_size,
            'reduction': reduction,
            'file_path': compressed_path
        })
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<path:file_path>')
def download_file(file_path):
    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path),
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/compress/jpg', methods=['POST'])
def compress_jpg_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith(('.jpg', '.jpeg')):
        return jsonify({'error': 'Only JPG files are allowed'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Generate output filename
        output_filename = f'compressed_{filename}'
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        # Get quality setting
        quality = int(request.form.get('quality', 80))
        
        # Compress JPG
        result = compress_jpg(input_path, output_path, quality=quality)
        
        # Clean up input file
        os.remove(input_path)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/compress/png', methods=['POST'])
def compress_png_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.png'):
        return jsonify({'error': 'Only PNG files are allowed'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Generate output filename
        output_filename = f'compressed_{filename}'
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        # Get compression level
        level = int(request.form.get('level', 6))
        
        # Compress PNG
        result = compress_png(input_path, output_path, compression_level=level)
        
        # Clean up input file
        os.remove(input_path)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/compress/video', methods=['POST'])
def compress_video_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith(('.mp4', '.avi', '.mov')):
        return jsonify({'error': 'Only MP4, AVI, and MOV files are allowed'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Generate output filename
        output_filename = f'compressed_{filename}'
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        # Get compression settings
        resolution = request.form.get('resolution', 'original')
        
        # Compress video
        result = compress_video(input_path, output_path, resolution=resolution)
        
        # Clean up input file
        os.remove(input_path)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)