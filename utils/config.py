class Config:
    def __init__(self):
        self.model_path = "best.pt"
        self.confidence_threshold = 0.95
        self.frame_width = 1020
        self.frame_height = 600
        self.camera_id = "/dev/video0"
        self.frame_rate = 25