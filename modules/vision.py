import cv2
import mediapipe as mp
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class CPRMetrics:
    compression_rate: float  # compressions per minute
    compression_depth: float  # estimated depth in cm
    hand_position: Tuple[float, float]  # normalized coordinates
    is_correct_position: bool

class CPRVisionAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # CPR parameters
        self.target_compression_rate = 100  # compressions per minute
        self.target_compression_depth = 5.0  # cm
        self.compression_threshold = 0.1  # normalized distance threshold
        
        # State tracking
        self.last_compression_time = 0
        self.compression_count = 0
        self.compression_times = []
        
    def analyze_frame(self, frame: np.ndarray) -> Optional[CPRMetrics]:
        """Analyze a single frame for CPR metrics"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame with MediaPipe
            results = self.pose.process(rgb_frame)
            
            if not results.pose_landmarks:
                return None
                
            # Extract relevant landmarks
            landmarks = results.pose_landmarks.landmark
            
            # Get hand and chest positions
            left_wrist = (landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST].y)
            right_wrist = (landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST].x,
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST].y)
            left_shoulder = (landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                            landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y)
            right_shoulder = (landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].x,
                             landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].y)
            
            # Calculate hand position relative to chest
            chest_center = ((left_shoulder[0] + right_shoulder[0]) / 2,
                           (left_shoulder[1] + right_shoulder[1]) / 2)
            hand_center = ((left_wrist[0] + right_wrist[0]) / 2,
                          (left_wrist[1] + right_wrist[1]) / 2)
            
            # Calculate compression depth (normalized)
            compression_depth = abs(hand_center[1] - chest_center[1])
            
            # Update compression tracking
            current_time = cv2.getTickCount() / cv2.getTickFrequency()
            if compression_depth > self.compression_threshold:
                if self.last_compression_time == 0:
                    self.last_compression_time = current_time
                elif current_time - self.last_compression_time > 0.5:  # Minimum time between compressions
                    self.compression_count += 1
                    self.compression_times.append(current_time)
                    self.last_compression_time = current_time
                    
                    # Keep only the last 10 compressions for rate calculation
                    if len(self.compression_times) > 10:
                        self.compression_times.pop(0)
            
            # Calculate compression rate
            if len(self.compression_times) >= 2:
                time_span = self.compression_times[-1] - self.compression_times[0]
                compression_rate = (len(self.compression_times) - 1) * 60 / time_span
            else:
                compression_rate = 0
                
            # Check if hands are in correct position
            is_correct_position = (abs(hand_center[0] - chest_center[0]) < 0.1 and
                                 abs(hand_center[1] - chest_center[1]) < 0.1)
            
            return CPRMetrics(
                compression_rate=compression_rate,
                compression_depth=compression_depth * 100,  # Convert to cm (approximate)
                hand_position=hand_center,
                is_correct_position=is_correct_position
            )
        except Exception as e:
            print(f"Error in analyze_frame: {e}")
            return None
        
    def draw_guidelines(self, frame: np.ndarray, metrics: CPRMetrics) -> np.ndarray:
        """Draw visual guidelines on the frame"""
        h, w = frame.shape[:2]
        
        # Draw target hand position
        target_x = int(metrics.hand_position[0] * w)
        target_y = int(metrics.hand_position[1] * h)
        cv2.circle(frame, (target_x, target_y), 20, (0, 255, 0), 2)
        
        # Draw compression depth indicator
        depth_bar_height = int(metrics.compression_depth * 2)  # Scale for visibility
        cv2.rectangle(frame, (10, h-100), (30, h-100-depth_bar_height), (0, 255, 0), -1)
        
        # Draw metrics text
        cv2.putText(frame, f"Rate: {metrics.compression_rate:.1f} cpm", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Depth: {metrics.compression_depth:.1f} cm", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame 