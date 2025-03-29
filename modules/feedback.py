import pyttsx3
import time
from typing import Optional
from .vision import CPRMetrics

class CPRFeedback:
    def __init__(self):
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        
        # Feedback thresholds
        self.rate_threshold = 10  # compressions per minute
        self.depth_threshold = 1.0  # cm
        
        # Feedback cooldown
        self.last_feedback_time = 0
        self.feedback_cooldown = 2.0  # seconds
        
        # Feedback messages
        self.feedback_messages = {
            'rate_too_slow': "Please compress faster, aim for 100 compressions per minute",
            'rate_too_fast': "Please slow down, aim for 100 compressions per minute",
            'depth_too_shallow': "Press deeper, aim for 5 centimeters",
            'depth_too_deep': "Don't press too deep, aim for 5 centimeters",
            'position_incorrect': "Place your hands in the center of the chest",
            'good_rate': "Good compression rate!",
            'good_depth': "Good compression depth!",
            'good_position': "Good hand position!"
        }
        
    def provide_feedback(self, metrics: CPRMetrics) -> Optional[str]:
        """Analyze metrics and provide appropriate feedback"""
        current_time = time.time()
        
        # Check if enough time has passed since last feedback
        if current_time - self.last_feedback_time < self.feedback_cooldown:
            return None
            
        feedback_message = None
        
        # Check compression rate
        if metrics.compression_rate < 90:
            feedback_message = self.feedback_messages['rate_too_slow']
        elif metrics.compression_rate > 110:
            feedback_message = self.feedback_messages['rate_too_fast']
        elif 95 <= metrics.compression_rate <= 105:
            feedback_message = self.feedback_messages['good_rate']
            
        # Check compression depth
        if metrics.compression_depth < 4.0:
            feedback_message = self.feedback_messages['depth_too_shallow']
        elif metrics.compression_depth > 6.0:
            feedback_message = self.feedback_messages['depth_too_deep']
        elif 4.5 <= metrics.compression_depth <= 5.5:
            feedback_message = self.feedback_messages['good_depth']
            
        # Check hand position
        if not metrics.is_correct_position:
            feedback_message = self.feedback_messages['position_incorrect']
        elif feedback_message is None:
            feedback_message = self.feedback_messages['good_position']
            
        if feedback_message:
            self.last_feedback_time = current_time
            self.speak_feedback(feedback_message)
            
        return feedback_message
        
    def speak_feedback(self, message: str):
        """Convert feedback message to speech"""
        try:
            self.engine.say(message)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
            
    def get_visual_feedback(self, metrics: CPRMetrics) -> dict:
        """Generate visual feedback indicators"""
        return {
            'rate_status': 'good' if 95 <= metrics.compression_rate <= 105 else 'warning',
            'depth_status': 'good' if 4.5 <= metrics.compression_depth <= 5.5 else 'warning',
            'position_status': 'good' if metrics.is_correct_position else 'warning',
            'rate_value': metrics.compression_rate,
            'depth_value': metrics.compression_depth
        } 