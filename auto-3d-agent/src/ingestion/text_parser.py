import re
from typing import List, Dict, Any

class TextParser:
    def parse_text(self, text: str) -> str:
        # Basic text parsing - return the text as is
        return text

    def extract_keywords(self, text: str) -> List[str]:
        # Improved keyword extraction
        if not text:
            return []
        
        # Convert to lowercase
        text_lower = text.lower()
        
        # Remove punctuation
        text_clean = re.sub(r'[^\w\s]', '', text_lower)
        
        # Split into words
        words = text_clean.split()
        
        # Filter out common stop words
        stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 
                     'should', 'may', 'might', 'must', 'can', 'and', 'or', 'but', 'if', 
                     'then', 'else', 'when', 'where', 'what', 'how', 'why', 'who', 'which'}
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords

    def extract_parameters(self, text: str) -> Dict[str, Any]:
        """Extract numerical parameters and units from text"""
        params = {}
        
        # Extract numbers with units
        number_patterns = [
            (r'(\d+(?:\.\d+)?)\s*mm', 'length_mm'),
            (r'(\d+(?:\.\d+)?)\s*cm', 'length_cm'),
            (r'(\d+(?:\.\d+)?)\s*m', 'length_m'),
            (r'(\d+(?:\.\d+)?)\s*degrees?', 'angle_deg'),
            (r'(\d+(?:\.\d+)?)\s*radians?', 'angle_rad'),
            (r'(\d+(?:\.\d+)?)\s*zähne?', 'teeth'),  # German for teeth
            (r'(\d+(?:\.\d+)?)\s*teeth', 'teeth'),
        ]
        
        for pattern, key in number_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                params[key] = float(matches[0])
        
        # Extract shape types
        shapes = ['cube', 'sphere', 'cylinder', 'cone', 'torus', 'gear', 'spring', 'thread']
        for shape in shapes:
            if shape in text.lower():
                params['shape'] = shape
                break
        
        return params
