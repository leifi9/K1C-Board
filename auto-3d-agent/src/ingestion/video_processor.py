import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Union


class VideoProcessor:
    def __init__(self, video_path: Union[str, Path] = None):
        self.video_path = video_path

    def process_video(self, video_data: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Process a video and extract relevant information for 3D modeling.
        
        Args:
            video_data: Path to video file or video data
            
        Returns:
            List of processed frames with metadata
        """
        try:
            if isinstance(video_data, (str, Path)):
                video_path = Path(video_data)
                
                if not video_path.exists():
                    return [{
                        'error': f'Video file not found: {video_path}',
                        'frames': []
                    }]
                
                # Extract and process frames
                frames = self.extract_frames(video_path)
                
                # Analyze frames
                frame_data = []
                for i, frame in enumerate(frames):
                    if frame is not None:
                        height, width = frame.shape[:2]
                        
                        # Extract basic information
                        frame_info = {
                            'frame_number': i,
                            'dimensions': {'width': width, 'height': height},
                            'timestamp': i / 30.0  # Assuming 30 fps
                        }
                        
                        # Detect motion or significant changes
                        if i > 0 and len(frames) > 1:
                            diff = cv2.absdiff(frames[i-1], frame)
                            motion_score = np.mean(diff)
                            frame_info['motion_score'] = float(motion_score)
                        
                        frame_data.append(frame_info)
                
                return frame_data
            else:
                return []
                
        except Exception as e:
            return [{
                'error': str(e),
                'frames': []
            }]

    def extract_frames(self, video_path: Union[str, Path] = None, 
                      max_frames: int = 30, 
                      sample_rate: int = None) -> List[np.ndarray]:
        """
        Extract frames from a video file.
        
        Args:
            video_path: Path to the video file
            max_frames: Maximum number of frames to extract
            sample_rate: Extract every Nth frame (if None, evenly distribute frames)
            
        Returns:
            List of frame images as numpy arrays
        """
        if video_path is None:
            video_path = self.video_path
            
        if video_path is None:
            return []
        
        try:
            video_path = Path(video_path)
            
            if not video_path.exists():
                return []
            
            # Open video capture
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                return []
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            frames = []
            
            if sample_rate is None:
                # Calculate sample rate to get max_frames evenly distributed
                if total_frames > max_frames:
                    sample_rate = total_frames // max_frames
                else:
                    sample_rate = 1
            
            frame_count = 0
            extracted_count = 0
            
            while cap.isOpened() and extracted_count < max_frames:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Sample frames based on sample_rate
                if frame_count % sample_rate == 0:
                    frames.append(frame)
                    extracted_count += 1
                
                frame_count += 1
            
            cap.release()
            
            return frames
            
        except Exception as e:
            return []
    
    def extract_key_frames(self, video_path: Union[str, Path] = None, 
                          threshold: float = 30.0) -> List[np.ndarray]:
        """
        Extract key frames based on scene changes.
        
        Args:
            video_path: Path to the video file
            threshold: Threshold for detecting scene changes
            
        Returns:
            List of key frame images
        """
        if video_path is None:
            video_path = self.video_path
            
        if video_path is None:
            return []
        
        try:
            video_path = Path(video_path)
            
            if not video_path.exists():
                return []
            
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                return []
            
            key_frames = []
            prev_frame = None
            
            while cap.isOpened():
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                if prev_frame is not None:
                    # Calculate difference between frames
                    diff = cv2.absdiff(prev_frame, frame)
                    mean_diff = np.mean(diff)
                    
                    # If difference is above threshold, it's a key frame
                    if mean_diff > threshold:
                        key_frames.append(frame.copy())
                else:
                    # First frame is always a key frame
                    key_frames.append(frame.copy())
                
                prev_frame = frame.copy()
            
            cap.release()
            
            return key_frames
            
        except Exception as e:
            return []
