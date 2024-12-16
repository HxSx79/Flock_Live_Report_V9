import cv2
import time

class WebcamStream:
    def __init__(self, camera_id="/dev/video0"):
        self.camera_id = camera_id
        self.cap = None
        self.last_frame_time = 0
        self.frame_interval = 1.0 / 25  # 25 FPS

    def start(self):
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_V4L2)
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FPS, 25)  # Set FPS to 25
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Use MJPG codec
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer size

    def read(self):
        if self.cap is None:
            self.start()
            
        # Implement frame rate control
        current_time = time.time()
        time_diff = current_time - self.last_frame_time
        
        if time_diff < self.frame_interval:
            time.sleep(self.frame_interval - time_diff)
            
        ret, frame = self.cap.read()
        if ret:
            self.last_frame_time = time.time()
            
        return ret, frame

    def release(self):
        if self.cap is not None:
            self.cap.release()