import cv2
from typing import Dict, List, Set
from .geometry import Point, calculate_intersection
from .tracking import TrackingState
from .flock_report import FlockReport
from .bom_reader import BOMReader

class LineCounter:
    def __init__(self):
        self.counted_ids: Set[int] = set()
        self.line_x_position = 0.5  # Vertical line at 50% of width
        self.line_y_position = 0.5  # Horizontal line at 50% of height
        self.tracking_state = TrackingState()
        self.counts = {'line1': 0, 'line2': 0}
        self.flock_report = FlockReport()
        self.bom_reader = BOMReader()

    def draw_counting_line(self, frame: cv2.Mat) -> cv2.Mat:
        """Draw the counting lines on the frame"""
        height, width = frame.shape[:2]
        
        # Draw vertical counting line (yellow)
        line_x = int(width * self.line_x_position)
        cv2.line(frame, (line_x, 0), (line_x, height), (0, 255, 255), 2)
        
        # Draw horizontal zone separator line (white)
        line_y = int(height * self.line_y_position)
        cv2.line(frame, (0, line_y), (width, line_y), (255, 255, 255), 2)
        
        # Add zone labels
        cv2.putText(frame, "Line 1", (10, int(height * 0.25)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Line 2", (10, int(height * 0.75)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame

    def update_counts(self, detections: List[Dict]) -> None:
        """Update part counts based on detected objects crossing the line"""
        for detection in detections:
            if not self._is_valid_detection(detection):
                continue

            track_id = detection['track_id']
            current_pos = self._get_detection_center(detection)
            
            if self.tracking_state.has_previous_position(track_id):
                prev_pos = self.tracking_state.get_previous_position(track_id)
                if self._has_crossed_line(prev_pos, current_pos):
                    self._process_line_crossing(track_id, detection, current_pos)
            
            self.tracking_state.update_position(track_id, current_pos)

    def _is_valid_detection(self, detection: Dict) -> bool:
        """Check if detection has required data and is a valid part in BOM"""
        if not all(key in detection for key in ['track_id', 'box', 'class_name']):
            return False
        return self.bom_reader.is_valid_class(detection['class_name'])

    def _get_detection_center(self, detection: Dict) -> Point:
        """Calculate center point of detection box"""
        x1, y1, x2, y2 = detection['box']
        return Point((x1 + x2) / 2, (y1 + y2) / 2)

    def _has_crossed_line(self, prev_pos: Point, current_pos: Point) -> bool:
        """Check if movement between points crosses the vertical counting line"""
        return (prev_pos.x < self.line_x_position and current_pos.x >= self.line_x_position) or \
               (prev_pos.x > self.line_x_position and current_pos.x <= self.line_x_position)

    def _process_line_crossing(self, track_id: int, detection: Dict, position: Point) -> None:
        """Process a line crossing event"""
        if track_id not in self.counted_ids:
            class_name = detection['class_name']
            
            # Record the crossing in the flock report
            self.flock_report.record_crossing(class_name)
            
            # Determine which line to count based on y-position
            # If above horizontal line (y < line_y_position) -> Line 1
            # If below horizontal line (y >= line_y_position) -> Line 2
            if position.y < self.line_y_position:
                self.counts['line1'] += 1
            else:
                self.counts['line2'] += 1
                
            self.counted_ids.add(track_id)

    def get_counts(self) -> Dict[str, int]:
        """Get current counts for both lines"""
        return self.counts.copy()

    def reset_counts(self) -> None:
        """Reset all counts and tracking data"""
        self.counted_ids.clear()
        self.tracking_state.reset()
        self.counts = {'line1': 0, 'line2': 0}