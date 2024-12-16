import cv2
from ultralytics import YOLO
from typing import Dict, List, Tuple
from .config import Config
from .line_counter import LineCounter
from .production import ProductionTracker

class ObjectDetector:
    def __init__(self):
        self.config = Config()
        self.model = YOLO(self.config.model_path)
        self.model.conf = self.config.confidence_threshold
        self.names = self.model.model.names
        self.current_detections = []
        self.line_counter = LineCounter()
        self.production_tracker = ProductionTracker()

    def process_frame(self, frame: cv2.Mat) -> cv2.Mat:
        if frame is None:
            return frame
            
        frame = cv2.resize(frame, (self.config.frame_width, self.config.frame_height))
        results = self.model.track(frame, persist=True)
        
        self.current_detections = []
        
        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.int().cpu().tolist()
            class_ids = results[0].boxes.cls.int().cpu().tolist()
            track_ids = results[0].boxes.id.int().cpu().tolist()

            for box, class_id, track_id in zip(boxes, class_ids, track_ids):
                class_name = self.names[class_id]
                x1, y1, x2, y2 = box
                
                detection = {
                    'class_name': class_name,
                    'track_id': track_id,
                    'box': box
                }
                self.current_detections.append(detection)
                
                # Draw detection box and label
                color = (0, 255, 0) if class_name.endswith('_OK') else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f'{track_id} - {class_name}', (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Draw counting line and update counts
        frame = self.line_counter.draw_counting_line(frame)
        self.line_counter.update_counts(self.current_detections)
        
        # Update production tracker with latest detections and counts
        counts = self.line_counter.get_counts()
        self.production_tracker.update_line_data(1, self.current_detections, counts)
        self.production_tracker.update_line_data(2, self.current_detections, counts)

        return frame

    def get_current_detections(self) -> List[Dict]:
        return self.current_detections
        
    def get_counts(self) -> Dict[str, int]:
        return self.line_counter.get_counts()