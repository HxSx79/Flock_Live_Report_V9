import pandas as pd
import os
from datetime import datetime

class LatestDetectionsReader:
    def __init__(self, filename="Latest_Detections.xlsx"):
        self.filename = filename

    def get_latest_detections(self, limit=15):
        if not os.path.exists(self.filename):
            return []
            
        try:
            df = pd.read_excel(self.filename)
            df = df.head(limit)
            
            # Format time as HH:mm
            df['Time'] = pd.to_datetime(df['Time']).dt.strftime('%H:%M')
            
            # Convert to list of dictionaries
            latest = df.to_dict('records')
            return latest
        except Exception as e:
            print(f"Error reading latest detections: {e}")
            return []