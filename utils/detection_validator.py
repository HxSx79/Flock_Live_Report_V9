class DetectionValidator:
    def __init__(self):
        self.valid_detections = {}
        self.clip_detections = {}
        
    def is_valid_detection(self, class_name):
        """
        Validate if the detection meets all required criteria
        Returns True if the detection is valid, False otherwise
        """
        # Store validation result for the class
        if class_name not in self.valid_detections:
            self.valid_detections[class_name] = True
            
        return self.valid_detections[class_name]

    def update_clip_detection(self, class_name):
        """
        Update clip detection status based on detected class name
        """
        if class_name.startswith("Clip") and class_name.endswith("_OK"):
            self.clip_detections[class_name] = True
        
    def is_valid_clip_detection(self, class_name, clip_number, total_clips):
        """
        Validate if a specific clip detection meets all required criteria
        Returns True if the clip detection is valid, False otherwise
        """
        # For single clip, look for Clip_OK
        if total_clips == 1:
            return "Clip_OK" in self.clip_detections
        
        # For multiple clips, look for Clip{N}_OK
        expected_class = f"Clip{clip_number}_OK"
        return expected_class in self.clip_detections
        
    def reset_validation(self, class_name=None):
        """
        Reset validation status for a specific class or all classes
        """
        if class_name:
            self.valid_detections.pop(class_name, None)
            if class_name.startswith("Clip") and class_name.endswith("_OK"):
                self.clip_detections.pop(class_name, None)
        else:
            self.valid_detections.clear()
            self.clip_detections.clear()