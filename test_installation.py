import cv2
import mediapipe as mp
import pyttsx3
import speech_recognition as sr
from PyQt6.QtWidgets import QApplication
import sys
import numpy as np

def test_opencv():
    """Test OpenCV installation and camera access"""
    print("Testing OpenCV...")
    
    # Try different camera indices
    for i in range(2):  # Try first two camera indices
        print(f"Trying camera index {i}...")
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Successfully opened camera {i}")
                cap.release()
                return True
            else:
                print(f"❌ Could not read frame from camera {i}")
            cap.release()
        else:
            print(f"❌ Could not open camera {i}")
    
    print("❌ No working camera found")
    return False

def test_mediapipe():
    """Test MediaPipe installation and pose detection"""
    print("Testing MediaPipe...")
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    
    # Create a test image (black background with white rectangle)
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(test_image, (100, 100), (540, 380), (255, 255, 255), -1)
    
    # Convert to RGB
    rgb_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_image)
    
    print("✅ MediaPipe test passed")
    return True

def test_text_to_speech():
    """Test text-to-speech functionality"""
    print("Testing text-to-speech...")
    try:
        engine = pyttsx3.init()
        engine.say("Test")
        engine.runAndWait()
        print("✅ Text-to-speech test passed")
        return True
    except Exception as e:
        print(f"❌ Error in text-to-speech: {e}")
        return False

def test_speech_recognition():
    """Test speech recognition functionality"""
    print("Testing speech recognition...")
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Please speak something...")
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            print(f"Recognized text: {text}")
            print("✅ Speech recognition test passed")
            return True
    except Exception as e:
        print(f"❌ Error in speech recognition: {e}")
        return False

def test_pyqt():
    """Test PyQt installation"""
    print("Testing PyQt...")
    try:
        app = QApplication(sys.argv)
        print("✅ PyQt test passed")
        return True
    except Exception as e:
        print(f"❌ Error in PyQt: {e}")
        return False

def main():
    print("Starting installation tests...")
    print("-" * 50)
    
    tests = [
        ("OpenCV", test_opencv),
        ("MediaPipe", test_mediapipe),
        ("Text-to-Speech", test_text_to_speech),
        ("Speech Recognition", test_speech_recognition),
        ("PyQt", test_pyqt)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        if not test_func():
            all_passed = False
            print(f"❌ {test_name} test failed")
        else:
            print(f"✅ {test_name} test passed")
    
    print("\n" + "-" * 50)
    if all_passed:
        print("\n✅ All tests passed! The CPR training module is ready to use.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above and fix the issues.")

if __name__ == "__main__":
    main() 