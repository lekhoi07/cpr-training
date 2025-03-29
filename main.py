import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import threading
import queue
import traceback
import time

from modules.vision import CPRVisionAnalyzer
from modules.feedback import CPRFeedback
from modules.voice import VoiceInterface
from modules.ui import CPRTrainingUI

class CPRTrainingApp:
    def __init__(self):
        try:
            print("Initializing CPR Training App...")
            
            # Initialize UI
            print("Creating UI...")
            self.ui = CPRTrainingUI()
            print("UI created successfully")
            
            # Initialize components
            print("Initializing vision analyzer...")
            self.vision_analyzer = CPRVisionAnalyzer()
            print("Initializing feedback system...")
            self.feedback_system = CPRFeedback()
            print("Initializing voice interface...")
            self.voice_interface = VoiceInterface()
            
            # Initialize video capture with optimized settings
            print("Opening camera...")
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("WARNING: Could not open camera!")
            else:
                # Set camera properties for better performance
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Reduced resolution
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                print("Camera opened successfully")
            
            # Set up timer for video update with reduced frequency
            print("Setting up video timer...")
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(33)  # ~30 FPS
            print("Video timer started")
            
            # Set up voice command queue
            self.command_queue = queue.Queue()
            
            # Start voice interface in a separate thread
            self.voice_thread = threading.Thread(target=self.start_voice_interface)
            self.voice_thread.daemon = True
            self.voice_thread.start()
            
            # Initialize frame processing state
            self.last_frame_time = 0
            self.frame_interval = 1.0 / 30.0  # Target 30 FPS
            
        except Exception as e:
            print(f"Error during initialization: {e}")
            print("Traceback:")
            traceback.print_exc()
            raise
        
    def start_voice_interface(self):
        """Run voice interface in a separate thread"""
        try:
            self.voice_interface.start_voice_interface(self.handle_voice_command)
        except Exception as e:
            print(f"Error in voice interface: {e}")
            print("Traceback:")
            traceback.print_exc()
        
    def update_frame(self):
        """Update the video frame and process CPR metrics"""
        try:
            if not self.ui.is_active():
                return
                
            current_time = time.time()
            if current_time - self.last_frame_time < self.frame_interval:
                return  # Skip frame if too soon
                
            ret, frame = self.cap.read()
            if not ret:
                print("WARNING: Could not read frame from camera")
                return
                
            # Process frame with vision analyzer
            metrics = self.vision_analyzer.analyze_frame(frame)
            
            if metrics:
                # Draw guidelines on frame
                frame = self.vision_analyzer.draw_guidelines(frame, metrics)
                
                # Update UI metrics
                visual_feedback = self.feedback_system.get_visual_feedback(metrics)
                self.ui.update_metrics(visual_feedback)
                
                # Provide audio feedback
                self.feedback_system.provide_feedback(metrics)
                
            # Update video display
            self.ui.update_video_frame(frame)
            self.last_frame_time = current_time
            
        except Exception as e:
            print(f"Error in update_frame: {e}")
            print("Traceback:")
            traceback.print_exc()
        
    def handle_voice_command(self, command: str):
        """Handle voice commands from the voice interface"""
        try:
            print(f"Received voice command: {command}")
            if 'pause' in command:
                self.ui.pause_training()
            elif 'resume' in command:
                self.ui.pause_training()
            elif 'stop' in command:
                self.ui.stop_training()
        except Exception as e:
            print(f"Error handling voice command: {e}")
            print("Traceback:")
            traceback.print_exc()
            
    def run(self):
        """Run the application"""
        try:
            print("Starting application...")
            self.ui.show()
            print("Window should now be visible")
            return QApplication.instance().exec()
        except Exception as e:
            print(f"Error in run: {e}")
            print("Traceback:")
            traceback.print_exc()
            return 1
        
    def cleanup(self):
        """Clean up resources"""
        try:
            print("Cleaning up resources...")
            if hasattr(self, 'cap') and self.cap is not None:
                self.cap.release()
            cv2.destroyAllWindows()
            print("Cleanup complete")
        except Exception as e:
            print(f"Error during cleanup: {e}")
            print("Traceback:")
            traceback.print_exc()

def main():
    try:
        print("Creating QApplication...")
        app = QApplication(sys.argv)
        print("Creating CPR Training App...")
        cpr_app = CPRTrainingApp()
        
        print("Running application...")
        sys.exit(cpr_app.run())
    except Exception as e:
        print(f"Fatal error: {e}")
        print("Traceback:")
        traceback.print_exc()
        return 1
    finally:
        print("Cleaning up...")
        if 'cpr_app' in locals():
            cpr_app.cleanup()

if __name__ == "__main__":
    main() 