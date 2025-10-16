import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, Union, List


class ImageProcessor:
    def __init__(self):
        self.feature_detector = cv2.SIFT_create() if hasattr(cv2, 'SIFT_create') else None
    
    def process_image(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Process an image and extract relevant information for 3D modeling.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing processed image data and metadata
        """
        try:
            image_path = Path(image_path)
            
            # Check if file exists
            if not image_path.exists():
                return {
                    'error': f'Image file not found: {image_path}',
                    'dimensions': None,
                    'features': []
                }
            
            # Read image
            image = cv2.imread(str(image_path))
            if image is None:
                return {
                    'error': f'Could not read image: {image_path}',
                    'dimensions': None,
                    'features': []
                }
            
            # Get image dimensions
            height, width = image.shape[:2]
            
            # Extract features
            features = self.extract_features(image)
            
            # Detect edges for shape analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Analyze shapes
            shapes = self._analyze_shapes(contours)
            
            # Calculate dominant colors
            colors = self._extract_dominant_colors(image)
            
            return {
                'path': str(image_path),
                'dimensions': {'width': width, 'height': height},
                'features': features,
                'shapes': shapes,
                'colors': colors,
                'contour_count': len(contours)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'dimensions': None,
                'features': []
            }

    def extract_features(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Extract visual features from an image using SIFT or ORB.
        
        Args:
            image: OpenCV image array
            
        Returns:
            List of feature descriptors
        """
        if image is None:
            return []
        
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            features = []
            
            # Try SIFT first (more accurate but requires opencv-contrib)
            if self.feature_detector:
                try:
                    keypoints, descriptors = self.feature_detector.detectAndCompute(gray, None)
                    if keypoints and descriptors is not None:
                        for kp, desc in zip(keypoints[:10], descriptors[:10]):  # Limit to first 10
                            features.append({
                                'x': float(kp.pt[0]),
                                'y': float(kp.pt[1]),
                                'size': float(kp.size),
                                'angle': float(kp.angle),
                                'response': float(kp.response)
                            })
                except Exception:
                    pass
            
            # Fallback to ORB if SIFT fails
            if not features:
                try:
                    orb = cv2.ORB_create(nfeatures=10)
                    keypoints, descriptors = orb.detectAndCompute(gray, None)
                    if keypoints:
                        for kp in keypoints:
                            features.append({
                                'x': float(kp.pt[0]),
                                'y': float(kp.pt[1]),
                                'size': float(kp.size),
                                'angle': float(kp.angle),
                                'response': float(kp.response)
                            })
                except Exception:
                    pass
            
            return features
            
        except Exception as e:
            return []
    
    def _analyze_shapes(self, contours: List) -> List[Dict[str, Any]]:
        """Analyze contours to identify geometric shapes"""
        shapes = []
        
        for contour in contours[:10]:  # Limit to first 10 largest
            # Calculate area
            area = cv2.contourArea(contour)
            if area < 100:  # Skip very small contours
                continue
            
            # Approximate the contour
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
            
            # Classify shape based on number of vertices
            num_vertices = len(approx)
            shape_type = 'unknown'
            
            if num_vertices == 3:
                shape_type = 'triangle'
            elif num_vertices == 4:
                # Check if rectangle or square
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)
                shape_type = 'square' if 0.95 <= aspect_ratio <= 1.05 else 'rectangle'
            elif num_vertices > 4:
                # Check if circle
                area = cv2.contourArea(contour)
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                shape_type = 'circle' if circularity > 0.8 else 'polygon'
            
            shapes.append({
                'type': shape_type,
                'vertices': num_vertices,
                'area': float(area),
                'perimeter': float(perimeter)
            })
        
        return shapes
    
    def _extract_dominant_colors(self, image: np.ndarray, k: int = 3) -> List[List[int]]:
        """Extract dominant colors using k-means clustering"""
        try:
            # Reshape image to be a list of pixels
            pixels = image.reshape((-1, 3))
            pixels = np.float32(pixels)
            
            # Define criteria and apply k-means
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert centers to integer RGB values
            centers = np.uint8(centers)
            dominant_colors = centers.tolist()
            
            return dominant_colors
            
        except Exception:
            return []