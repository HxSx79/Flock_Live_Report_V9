import cv2
import time
from typing import Generator, Optional, Tuple
from werkzeug.datastructures import FileStorage

class VideoStream:
    def __init__(self):
        self.cap = None
        self.test_video = None
        self.last_frame_time = 0
        self.frame_interval = 1.0 / 25  # 25 FPS
        self.target_aspect_ratio = 16 / 9  # Standard widescreen ratio
        self.frame_count = 0
        self.last_frame = None

    def start_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
            self.cap.set(cv2.CAP_PROP_FPS, 25)
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def set_test_video(self, video_file: FileStorage) -> None:
        """Set up test video with proper frame rate control"""
        temp_path = "/tmp/test_video.mp4"
        video_file.save(temp_path)
        
        # Release existing video if any
        if self.test_video is not None:
            self.test_video.release()
            
        self.test_video = cv2.VideoCapture(temp_path)
        self.frame_count = 0
        self.last_frame_time = time.time()
        self.last_frame = None

    def maintain_aspect_ratio(self, frame: cv2.Mat, target_width: int, target_height: int) -> cv2.Mat:
        """Resize frame maintaining aspect ratio with padding if necessary"""
        if frame is None:
            return None
            
        height, width = frame.shape[:2]
        current_ratio = width / height
        
        if current_ratio > self.target_aspect_ratio:
            # Width is the limiting factor
            new_width = target_width
            new_height = int(target_width / current_ratio)
            top_padding = (target_height - new_height) // 2
            bottom_padding = target_height - new_height - top_padding
            left_padding = 0
            right_padding = 0
        else:
            # Height is the limiting factor
            new_height = target_height
            new_width = int(target_height * current_ratio)
            left_padding = (target_width - new_width) // 2
            right_padding = target_width - new_width - left_padding
            top_padding = 0
            bottom_padding = 0
            
        # Resize frame
        resized = cv2.resize(frame, (new_width, new_height))
        
        # Add padding
        padded = cv2.copyMakeBorder(
            resized,
            top_padding,
            bottom_padding,
            left_padding,
            right_padding,
            cv2.BORDER_CONSTANT,
            value=[0, 0, 0]
        )
        
        return padded

    def read_frame(self) -> Tuple[bool, Optional[cv2.Mat]]:
        """Read frame with consistent frame rate for both live and test video"""
        current_time = time.time()
        elapsed = current_time - self.last_frame_time
        
        # Enforce frame rate
        if elapsed < self.frame_interval:
            if self.last_frame is not None:
                return True, self.last_frame.copy()
            time.sleep(self.frame_interval - elapsed)
        
        if self.test_video is not None:
            ret, frame = self.test_video.read()
            if not ret:
                # Reset video to beginning
                self.test_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.test_video.read()
                self.frame_count = 0
            
            if ret:
                self.frame_count += 1
                self.last_frame = frame.copy()
                self.last_frame_time = current_time
            return ret, frame
        
        if self.cap is None:
            self.start_camera()
            
        ret, frame = self.cap.read()
        if ret:
            self.last_frame = frame.copy()
            self.last_frame_time = current_time
        return ret, frame

    def generate_frames(self, detector) -> Generator[bytes, None, None]:
        while True:
            ret, frame = self.read_frame()
            if not ret:
                break
                
            # Maintain aspect ratio while resizing
            frame = self.maintain_aspect_ratio(frame, 1020, 600)
            frame = detector.process_frame(frame)
            
            try:
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                print(f"Error encoding frame: {e}")
                continue

    def release(self):
        if self.cap is not None:
            self.cap.release()
        if self.test_video is not None:
            self.test_video.release()