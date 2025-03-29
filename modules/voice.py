import speech_recognition as sr
import pyttsx3
import time
from typing import Optional, Callable

class VoiceInterface:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000  # Adjust based on your microphone
        self.recognizer.dynamic_energy_threshold = True
        
        # Initialize text-to-speech
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        
        # Command handlers
        self.command_handlers = {
            'help': self.handle_help,
            'pause': self.handle_pause,
            'resume': self.handle_resume,
            'stop': self.handle_stop,
            'explain': self.handle_explain
        }
        
        # CPR-related responses
        self.cpr_responses = {
            'compression_rate': "The recommended compression rate is 100 to 120 compressions per minute. "
                              "This means you should perform about 2 compressions per second.",
            'compression_depth': "For adult CPR, you should compress the chest at least 5 centimeters, "
                               "but not more than 6 centimeters. This ensures proper blood circulation.",
            'hand_position': "Place the heel of one hand in the center of the chest, "
                           "with your other hand on top. Keep your arms straight and elbows locked.",
            'general': "CPR involves chest compressions and rescue breaths. For hands-only CPR, "
                      "focus on chest compressions at a rate of 100-120 per minute and a depth of 5-6 centimeters."
        }
        
    def listen_for_command(self) -> Optional[str]:
        """Listen for voice commands and return the recognized text"""
        with sr.Microphone() as source:
            print("Listening for command...")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio).lower()
                print(f"Recognized: {text}")
                return text
            except sr.WaitTimeoutError:
                print("No speech detected")
                return None
            except sr.UnknownValueError:
                print("Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                return None
                
    def process_command(self, command: str) -> Optional[str]:
        """Process the recognized command and return a response"""
        # Check for specific CPR-related questions
        if 'how' in command and 'deep' in command:
            return self.cpr_responses['compression_depth']
        elif 'how' in command and 'fast' in command:
            return self.cpr_responses['compression_rate']
        elif 'where' in command and 'hands' in command:
            return self.cpr_responses['hand_position']
        elif 'what' in command and 'cpr' in command:
            return self.cpr_responses['general']
            
        # Check for registered commands
        for cmd, handler in self.command_handlers.items():
            if cmd in command:
                return handler()
                
        return "I'm not sure about that. You can ask for help to see available commands."
        
    def speak_response(self, response: str):
        """Convert response to speech"""
        try:
            self.engine.say(response)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
            
    # Command handlers
    def handle_help(self) -> str:
        return ("Available commands: help, pause, resume, stop, explain. "
                "You can also ask questions about compression rate, depth, or hand position.")
                
    def handle_pause(self) -> str:
        return "Training paused. Say 'resume' to continue."
        
    def handle_resume(self) -> str:
        return "Training resumed. Continue with chest compressions."
        
    def handle_stop(self) -> str:
        return "Training session ended. Thank you for practicing CPR!"
        
    def handle_explain(self) -> str:
        return self.cpr_responses['general']
        
    def start_voice_interface(self, callback: Optional[Callable[[str], None]] = None):
        """Start the voice interface in a loop"""
        print("Voice interface started in background")
        while True:
            try:
                command = self.listen_for_command()
                if command:
                    if 'stop' in command:
                        response = self.handle_stop()
                        self.speak_response(response)
                        break
                        
                    response = self.process_command(command)
                    self.speak_response(response)
                    
                    if callback:
                        callback(command)
            except Exception as e:
                print(f"Voice interface error: {e}")
                continue  # Continue listening even if there's an error 