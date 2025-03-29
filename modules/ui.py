from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QColor
import cv2
import numpy as np
from typing import Optional

class CPRTrainingUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CPR Training Module")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)
        
        # Create video display area
        self.video_frame = QFrame()
        self.video_frame.setMinimumSize(800, 600)
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_layout = QVBoxLayout(self.video_frame)
        self.video_layout.addWidget(self.video_label)
        
        # Create metrics display area
        self.metrics_frame = QFrame()
        self.metrics_frame.setMinimumSize(300, 600)
        self.metrics_layout = QVBoxLayout(self.metrics_frame)
        
        # Create metric labels
        self.rate_label = QLabel("Compression Rate: 0 cpm")
        self.depth_label = QLabel("Compression Depth: 0 cm")
        self.position_label = QLabel("Hand Position: Not Detected")
        
        # Style the metric labels
        for label in [self.rate_label, self.depth_label, self.position_label]:
            label.setStyleSheet("font-size: 16px; padding: 10px;")
            self.metrics_layout.addWidget(label)
            
        # Add status indicators
        self.rate_status = QLabel("Rate Status: Waiting...")
        self.depth_status = QLabel("Depth Status: Waiting...")
        self.position_status = QLabel("Position Status: Waiting...")
        
        for status in [self.rate_status, self.depth_status, self.position_status]:
            status.setStyleSheet("font-size: 14px; padding: 5px;")
            self.metrics_layout.addWidget(status)
            
        # Add control buttons
        self.start_button = QPushButton("Start Training")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        
        for button in [self.start_button, self.pause_button, self.stop_button]:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px;
                    font-size: 14px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.metrics_layout.addWidget(button)
            
        # Add stretch to push everything up
        self.metrics_layout.addStretch()
        
        # Add frames to main layout
        self.layout.addWidget(self.video_frame)
        self.layout.addWidget(self.metrics_frame)
        
        # Connect signals
        self.start_button.clicked.connect(self.start_training)
        self.pause_button.clicked.connect(self.pause_training)
        self.stop_button.clicked.connect(self.stop_training)
        
        # Initialize state
        self.is_training = False
        self.is_paused = False
        
    def update_video_frame(self, frame: np.ndarray):
        """Update the video display with a new frame"""
        if frame is None:
            return
            
        try:
            # Convert frame to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to QImage
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Scale image to fit label while maintaining aspect ratio
            scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                self.video_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation
            )
            
            self.video_label.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Error updating video frame: {e}")
        
    def update_metrics(self, metrics: dict):
        """Update the metrics display"""
        # Update rate
        self.rate_label.setText(f"Compression Rate: {metrics['rate_value']:.1f} cpm")
        self.rate_status.setText(f"Rate Status: {metrics['rate_status'].upper()}")
        self.rate_status.setStyleSheet(
            f"color: {'green' if metrics['rate_status'] == 'good' else 'red'};"
        )
        
        # Update depth
        self.depth_label.setText(f"Compression Depth: {metrics['depth_value']:.1f} cm")
        self.depth_status.setText(f"Depth Status: {metrics['depth_status'].upper()}")
        self.depth_status.setStyleSheet(
            f"color: {'green' if metrics['depth_status'] == 'good' else 'red'};"
        )
        
        # Update position
        self.position_status.setText(f"Position Status: {metrics['position_status'].upper()}")
        self.position_status.setStyleSheet(
            f"color: {'green' if metrics['position_status'] == 'good' else 'red'};"
        )
        
    def start_training(self):
        """Start the training session"""
        self.is_training = True
        self.is_paused = False
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        
    def pause_training(self):
        """Pause the training session"""
        self.is_paused = not self.is_paused
        self.pause_button.setText("Resume" if self.is_paused else "Pause")
        
    def stop_training(self):
        """Stop the training session"""
        self.is_training = False
        self.is_paused = False
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.pause_button.setText("Pause")
        
    def is_active(self) -> bool:
        """Check if the training session is active"""
        return self.is_training and not self.is_paused 