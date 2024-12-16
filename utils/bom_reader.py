import pandas as pd
import os
from typing import Dict, Optional

class BOMReader:
    def __init__(self, bom_file: str = "BOM.xlsx"):
        self.bom_file = bom_file
        self.bom_data = None
        self.valid_class_names = set()
        self._load_bom()

    def _load_bom(self) -> None:
        """Load BOM data and initialize valid class names set"""
        if not os.path.exists(self.bom_file):
            raise FileNotFoundError(f"BOM file not found: {self.bom_file}")
        
        self.bom_data = pd.read_excel(self.bom_file)
        self.valid_class_names = set(self.bom_data['Class_Name'].unique())

    def get_part_info(self, class_name: str) -> Dict[str, str]:
        """
        Get part information for a given class name
        Returns part info if class exists in BOM, default values otherwise
        """
        if class_name not in self.valid_class_names:
            return {
                'customer': 'Unknown',
                'program': 'Unknown',
                'part_number': 'Unknown',
                'description': 'Unknown',
                'num_clips': 0
            }

        try:
            part_info = self.bom_data[self.bom_data['Class_Name'] == class_name].iloc[0]
            return {
                'customer': part_info['Customer'],
                'program': part_info['Program'],
                'part_number': part_info['Part_Number'],
                'description': part_info['Description'],
                'num_clips': int(part_info.get('Number_of_Clips', 0))
            }
        except (IndexError, KeyError):
            return {
                'customer': 'Unknown',
                'program': 'Unknown',
                'part_number': 'Unknown',
                'description': 'Unknown',
                'num_clips': 0
            }

    def is_valid_class(self, class_name: str) -> bool:
        """Check if a class name exists in the BOM"""
        return class_name in self.valid_class_names