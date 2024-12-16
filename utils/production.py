from datetime import datetime
from typing import Dict, List
from .bom_reader import BOMReader

class ProductionTracker:
    def __init__(self):
        self.bom_reader = BOMReader()
        self.line1_data = {
            'part': {
                'program': '',
                'number': '',
                'description': '',
                'name': ''  # Kept for backward compatibility
            },
            'production': {'quantity': 0, 'delta': 0, 'pph': 0},
            'scrap': {'total': 0, 'rate': 0}
        }
        self.line2_data = {
            'part': {
                'program': '',
                'number': '',
                'description': '',
                'name': ''  # Kept for backward compatibility
            },
            'production': {'quantity': 0, 'delta': 0, 'pph': 0},
            'scrap': {'total': 0, 'rate': 0}
        }
        self.totals = {
            'quantity': 0,
            'delta': 0,
            'scrap': 0,
            'scrapRate': 0
        }
        self.production_details = []
        self.last_update_time = datetime.now()

    def update_part_info(self, line_number: int, class_name: str) -> None:
        """Update part information based on detected class name"""
        part_info = self.bom_reader.get_part_info(class_name)
        line_data = self.line1_data if line_number == 1 else self.line2_data
        
        line_data['part'].update({
            'program': part_info['program'],
            'number': part_info['part_number'],
            'description': part_info['description'],
            'name': part_info['description']  # Kept for backward compatibility
        })

    def update_production_counts(self, counts: Dict[str, int]) -> None:
        """Update production quantities based on line counter data"""
        current_time = datetime.now()
        time_diff = (current_time - self.last_update_time).total_seconds() / 3600  # hours
        
        # Update Line 1
        new_quantity = counts.get('line1', 0)
        if new_quantity > self.line1_data['production']['quantity']:
            delta = new_quantity - self.line1_data['production']['quantity']
            self.line1_data['production']['quantity'] = new_quantity
            self.line1_data['production']['delta'] = delta
            if time_diff > 0:
                self.line1_data['production']['pph'] = int(delta / time_diff)
        
        # Update Line 2
        new_quantity = counts.get('line2', 0)
        if new_quantity > self.line2_data['production']['quantity']:
            delta = new_quantity - self.line2_data['production']['quantity']
            self.line2_data['production']['quantity'] = new_quantity
            self.line2_data['production']['delta'] = delta
            if time_diff > 0:
                self.line2_data['production']['pph'] = int(delta / time_diff)
        
        # Update totals
        self.totals['quantity'] = (self.line1_data['production']['quantity'] + 
                                 self.line2_data['production']['quantity'])
        self.totals['delta'] = (self.line1_data['production']['delta'] + 
                              self.line2_data['production']['delta'])
        
        self.last_update_time = current_time

    def update_line_data(self, line_number: int, detections: List[Dict], counts: Dict[str, int]) -> None:
        # Update part info based on detections
        for detection in detections:
            class_name = detection.get('class_name')
            if class_name:
                self.update_part_info(line_number, class_name)
        
        # Update production counts
        self.update_production_counts(counts)

    def get_all_data(self) -> Dict:
        return {
            'line1_part': self.line1_data['part'],
            'line1_production': self.line1_data['production'],
            'line1_scrap': self.line1_data['scrap'],
            'line2_part': self.line2_data['part'],
            'line2_production': self.line2_data['production'],
            'line2_scrap': self.line2_data['scrap'],
            'total_quantity': self.totals['quantity'],
            'total_delta': self.totals['delta'],
            'total_scrap': self.totals['scrap'],
            'average_scrap_rate': self.totals['scrapRate']
        }