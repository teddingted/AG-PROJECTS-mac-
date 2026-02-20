from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
import base64
import json
from io import BytesIO
import csv
from core.auto_detector import AutoDetector
from core.logger import setup_logger

# Setup Logger
logger = setup_logger('app')

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')

from flask.json.provider import DefaultJSONProvider

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return super().default(obj)

app.json = CustomJSONProvider(app)



app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global storage for session data
session_data: dict = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    tb = traceback.format_exc()
    logger.error(f"Unhandled exception: {str(e)}\n{tb}")
    return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Read image and get dimensions
    img = cv2.imread(filepath)
    height, width = img.shape[:2]
    
    # Convert to base64 for display
    _, buffer = cv2.imencode('.png', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    session_data['image_path'] = filepath
    session_data['image_size'] = (width, height)
    
    return jsonify({
        'success': True,
        'image': f'data:image/png;base64,{img_base64}',
        'width': width,
        'height': height
    })

@app.route('/calibrate', methods=['POST'])
def calibrate():
    data = request.json
    session_data['calibration'] = {
        'points': data['points'],  # [(x1,y1), (x2,y2), (y1_x,y1_y), (y2_x,y2_y)]
        'values': data['values']   # [x1_val, x2_val, y1_val, y2_val]
    }
    return jsonify({'success': True})

@app.route('/detect_auto', methods=['POST'])
def detect_auto():
    if 'image_path' not in session_data:
        return jsonify({'error': 'No image uploaded'}), 400
    
    data = request.json
    mode = data.get('mode', 'full_auto')
    n_series = data.get('n_series', 3)
    
    detector = AutoDetector(session_data['image_path'])
    
    if mode == 'full_auto':
        # Detect axes
        axes = detector.detect_axes()
        if not axes:
            return jsonify({'error': 'Could not detect axes'}), 400
        
        endpoints = detector.get_axis_endpoints(axes)
        
        # Detect multiple series
        series_list = detector.detect_multiple_series(n_series=n_series)
        
        return jsonify({
            'success': True,
            'axes': endpoints,
            'series': series_list
        })
    
    elif mode == 'guided':
        colors = data.get('colors', [])
        detection_method = data.get('detection_method', 'color')
        
        # DEBUG: Log incoming data structure
        print(f"DEBUG_REQUEST: Buttons={detection_method}, Colors={len(colors)}")
        
        # FIX: Try get calibration from request, else from session
        calibration = data.get('calibration') 
        if not calibration:
            print("DEBUG_REQUEST: Calibration missing in body, checking session...")
            calibration = session_data.get('calibration')
        
        if calibration:
            print(f"DEBUG_REQUEST: Calibration FOUND. Type={type(calibration)}")
            if isinstance(calibration, dict):
                 print(f"DEBUG_REQUEST: Calibration Keys={calibration.keys()}")
                 if 'points' in calibration:
                     print(f"DEBUG_REQUEST: Points Count={len(calibration['points'])}")
        else:
            print("DEBUG_REQUEST: Calibration FAILED. It is None.")
        
        # New Safety Check
        if not calibration:
             return jsonify({'error': 'Calibration data missing. Please Calibrate Axes first.'}), 400

        if not colors:
            return jsonify({'error': 'No colors provided'}), 400
        
        # Extract series for each picked color
        series_list = detector.detect_auto(
            mode='guided', 
            colors=colors, 
            n_series=len(colors),
            detection_method=detection_method,
            calibration_points=calibration  # Pass raw calibration data
        )
        
        # Filter and Format
        filtered_series = []
        if isinstance(series_list, list):
             for s in series_list:
                # Filter noise
                if s and len(s['points']) > 5:
                    filtered_series.append(s)
        
        # DEBUG: Check if ROI is in response
        if filtered_series and 'debug_roi' in filtered_series[0]:
            print(f"DEBUG_RESPONSE: ROI present in first series: {filtered_series[0]['debug_roi']}")
        else:
            print("DEBUG_RESPONSE: No ROI in response series")

        return jsonify({'series': filtered_series})
    
    return jsonify({'error': 'Invalid mode'}), 400

@app.route('/export', methods=['POST'])
def export_csv():
    data = request.json
    points = data.get('points', [])
    calibration = session_data.get('calibration')
    
    if not calibration:
        return jsonify({'error': 'No calibration data'}), 400
    
    # Convert pixel coordinates to data values
    cal_points = calibration['points']
    cal_values = calibration['values']
    
    # Calculate conversion factors
    x1_px, x2_px = cal_points[0][0], cal_points[1][0]
    y1_px, y2_px = cal_points[2][1], cal_points[3][1]
    
    x1_val, x2_val, y1_val, y2_val = cal_values
    
    x_scale = (x2_val - x1_val) / (x2_px - x1_px)
    y_scale = (y2_val - y1_val) / (y2_px - y1_px)
    
    # Convert points
    csv_data = []
    for point in points:
        px_x, px_y, graph_id = point['x'], point['y'], point.get('graph_id', 1)
        
        val_x = x1_val + (px_x - x1_px) * x_scale
        val_y = y1_val + (px_y - y1_px) * y_scale
        
        csv_data.append([graph_id, val_x, val_y])
    
    # Create CSV in memory
    output = BytesIO()
    output.write(b'Graph_ID,X,Y\n')
    for row in csv_data:
        line = f"{row[0]},{row[1]:.6f},{row[2]:.6f}\n"
        output.write(line.encode('utf-8'))
    
    output.seek(0)
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='digitized_data.csv'
    )

@app.route('/version')
def version():
    return jsonify({'version': 'V6', 'features': ['RedExclusion', 'SmartROI', 'Clustering']})

if __name__ == '__main__':
    import webbrowser
    import threading
    import sys
    
    # FORCE FLUSH
    sys.stdout.reconfigure(line_buffering=True)
    
    print("="*50)
    print("🚀  AUTO PLOT DIGITIZER - VERSION V6 (UPDATED)  🚀")
    print("="*50)
    print("✅  V6 Logic Loaded: Red Exclusion, Smart ROI, Clustering")
    
    def open_browser():
        webbrowser.open('http://localhost:8080')
    
    # Open browser after short delay
    threading.Timer(1.5, open_browser).start()
    
    print("📱 Opening browser at http://localhost:8080")
    print("⏹️  Press Ctrl+C to stop")
    
    app.run(debug=True, port=8080, use_reloader=False)
