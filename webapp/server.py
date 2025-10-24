"""
Flask API Server for K1C-Board Web UI
Provides REST API endpoints for the 3D model generation webapp
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
import json
from pathlib import Path
import uuid

# Add auto-3d-agent to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'auto-3d-agent', 'src'))

try:
    from app import AdapterCreationApp
except ImportError:
    print("Warning: Could not import AdapterCreationApp. Running in mock mode.")
    AdapterCreationApp = None

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
OUTPUT_FOLDER = Path(__file__).parent.parent / 'auto-3d-agent' / 'output'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'step', 'stp', 'stl', 'obj'}

UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['OUTPUT_FOLDER'] = str(OUTPUT_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'backend': 'available' if AdapterCreationApp else 'mock'
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    filepath = UPLOAD_FOLDER / unique_filename
    
    file.save(str(filepath))
    
    return jsonify({
        'path': str(filepath),
        'filename': unique_filename
    })

@app.route('/api/generate', methods=['POST'])
def generate_model():
    """Generate 3D model based on configuration"""
    try:
        data = request.get_json()
        config = data.get('config', {})
        
        input_type = config.get('inputType', 'text')
        output_format = config.get('outputFormat', 'stl')
        output_path = config.get('outputPath', './output')
        
        # Validate required fields
        if input_type == 'text' and not config.get('inputText'):
            return jsonify({
                'success': False,
                'error': 'Input text is required for text-based generation'
            }), 400
        
        if input_type in ['image', 'video', 'cad'] and not config.get('inputPath'):
            return jsonify({
                'success': False,
                'error': 'Input file is required'
            }), 400
        
        # If we have the actual AdapterCreationApp, use it
        if AdapterCreationApp:
            try:
                # Initialize the app
                generator = AdapterCreationApp()
                
                # Prepare generation parameters
                if input_type == 'text':
                    result = generator.generate_from_text(
                        config.get('inputText'),
                        output_format=output_format
                    )
                elif input_type == 'image':
                    result = generator.generate_from_image(
                        config.get('inputPath'),
                        output_format=output_format
                    )
                elif input_type == 'video':
                    result = generator.generate_from_video(
                        config.get('inputPath'),
                        output_format=output_format
                    )
                elif input_type == 'cad':
                    result = generator.generate_adapter_from_cad(
                        config.get('inputPath'),
                        output_format=output_format
                    )
                
                return jsonify({
                    'success': True,
                    'message': 'Model generated successfully',
                    'outputPath': str(result) if result else None
                })
            
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Generation failed: {str(e)}'
                }), 500
        else:
            # Mock response for testing without backend
            output_file = OUTPUT_FOLDER / f'generated_model_{uuid.uuid4()}.{output_format}'
            
            return jsonify({
                'success': True,
                'message': 'Model generated successfully (mock mode)',
                'outputPath': str(output_file)
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/progress/<job_id>', methods=['GET'])
def get_progress(job_id):
    """Get generation progress for a job"""
    # This is a placeholder for future async job tracking
    return jsonify({
        'status': 'completed',
        'message': 'Job completed',
        'progress': 100
    })

@app.route('/api/outputs', methods=['GET'])
def list_outputs():
    """List generated output files"""
    try:
        outputs = []
        if OUTPUT_FOLDER.exists():
            for file in OUTPUT_FOLDER.iterdir():
                if file.is_file():
                    outputs.append({
                        'name': file.name,
                        'path': str(file),
                        'size': file.stat().st_size
                    })
        
        return jsonify({'outputs': outputs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def file_too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 100MB'}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting K1C-Board API Server...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Output folder: {OUTPUT_FOLDER}")
    print(f"Backend mode: {'available' if AdapterCreationApp else 'mock'}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
