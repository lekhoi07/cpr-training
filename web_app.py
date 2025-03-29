import streamlit as st
import cv2
import numpy as np
from modules.vision import CPRVisionAnalyzer, CPRMetrics
from modules.feedback import CPRFeedback
import time

def main():
    st.set_page_config(page_title="CPR Training Module", layout="wide")
    
    # Initialize components
    if 'vision_analyzer' not in st.session_state:
        st.session_state.vision_analyzer = CPRVisionAnalyzer()
    if 'feedback_system' not in st.session_state:
        st.session_state.feedback_system = CPRFeedback()
    if 'is_training' not in st.session_state:
        st.session_state.is_training = False
    if 'is_paused' not in st.session_state:
        st.session_state.is_paused = False
    
    # Title and description
    st.title("CPR Training Module")
    st.markdown("""
    This interactive CPR training module uses computer vision to analyze your CPR technique
    and provide real-time feedback on compression rate, depth, and hand position.
    """)
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Video feed
        st.subheader("Video Feed")
        video_placeholder = st.empty()
        
        # Camera controls
        if not st.session_state.is_training:
            if st.button("Start Training", type="primary"):
                st.session_state.is_training = True
                st.session_state.is_paused = False
                st.experimental_rerun()
        else:
            if st.button("Pause" if not st.session_state.is_paused else "Resume"):
                st.session_state.is_paused = not st.session_state.is_paused
                st.experimental_rerun()
            if st.button("Stop Training", type="secondary"):
                st.session_state.is_training = False
                st.session_state.is_paused = False
                st.experimental_rerun()
    
    with col2:
        # Metrics display
        st.subheader("Real-time Metrics")
        
        # Create placeholders for metrics
        rate_placeholder = st.empty()
        depth_placeholder = st.empty()
        position_placeholder = st.empty()
        
        # Status indicators
        st.subheader("Status Indicators")
        rate_status = st.empty()
        depth_status = st.empty()
        position_status = st.empty()
    
    # Main training loop
    if st.session_state.is_training and not st.session_state.is_paused:
        # Initialize camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Could not open camera!")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        try:
            while st.session_state.is_training and not st.session_state.is_paused:
                ret, frame = cap.read()
                if not ret:
                    st.error("Could not read frame from camera")
                    break
                
                # Process frame
                metrics = st.session_state.vision_analyzer.analyze_frame(frame)
                
                if metrics:
                    # Draw guidelines
                    frame = st.session_state.vision_analyzer.draw_guidelines(frame, metrics)
                    
                    # Update metrics display
                    rate_placeholder.markdown(f"**Compression Rate:** {metrics.compression_rate:.1f} cpm")
                    depth_placeholder.markdown(f"**Compression Depth:** {metrics.compression_depth:.1f} cm")
                    position_placeholder.markdown(f"**Hand Position:** {'Correct' if metrics.is_correct_position else 'Needs Adjustment'}")
                    
                    # Update status indicators
                    visual_feedback = st.session_state.feedback_system.get_visual_feedback(metrics)
                    rate_status.markdown(f"Rate Status: {visual_feedback['rate_status'].upper()}")
                    depth_status.markdown(f"Depth Status: {visual_feedback['depth_status'].upper()}")
                    position_status.markdown(f"Position Status: {visual_feedback['position_status'].upper()}")
                    
                    # Provide audio feedback
                    st.session_state.feedback_system.provide_feedback(metrics)
                
                # Display frame
                video_placeholder.image(frame, channels="BGR", use_column_width=True)
                
                # Add a small delay to control frame rate
                time.sleep(0.033)  # ~30 FPS
                
        finally:
            cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 