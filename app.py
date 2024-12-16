from flask import Flask, render_template, Response, jsonify, request
from datetime import datetime
import sys
from utils.video import VideoStream
from utils.detection import ObjectDetector
from utils.production import ProductionTracker
from utils.config import Config
from utils.shutdown import ShutdownManager

app = Flask(__name__)
config = Config()
video_stream = VideoStream()
detector = ObjectDetector()
production_tracker = ProductionTracker()
shutdown_manager = ShutdownManager()

@app.route('/')
def index():
    current_time = datetime.now().strftime("%H:%M:%S")
    current_datetime = datetime.now().strftime("%A, %B %d, %Y %H:%M:%S")
    
    return render_template('index.html',
                         current_time=current_time,
                         current_datetime=current_datetime,
                         **production_tracker.get_all_data())

@app.route('/shutdown', methods=['POST'])
def shutdown():
    try:
        # Release resources first
        video_stream.release()
        
        # Attempt server shutdown
        if shutdown_manager.shutdown_server():
            return jsonify({'success': True, 'message': 'Server shutting down...'})
        else:
            return jsonify({'success': False, 'error': 'Failed to shutdown server'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/video_feed')
def video_feed():
    return Response(video_stream.generate_frames(detector),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'success': False, 'error': 'No video file provided'})
    
    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'success': False, 'error': 'No video file selected'})
    
    try:
        video_stream.set_test_video(video_file)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)