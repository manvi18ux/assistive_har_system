import pyttsx3
import winsound
import time
import threading

def test_help_alert():
    """Test the exact help alert as it would be in the system"""
    
    # Initialize TTS
    engine = pyttsx3.init()
    engine.setProperty('rate', 130)
    engine.setProperty('volume', 1.0)
    
    print("Testing HELP alert sequence...")
    print("This is what you should hear when help gesture is detected:\n")
    
    # Play the beeps first (3 quick beeps for help)
    print("1. Playing 3 quick beeps...")
    for i in range(3):
        winsound.Beep(2000, 300)
        time.sleep(0.1)
    
    # Then play the voice alert
    print("2. Playing voice alert...")
    message = "URGENT! Help requested! Someone needs immediate assistance! Please check on them now!"
    
    # Method 1: Direct (blocking)
    print("   Method 1: Direct voice...")
    engine.say(message)
    engine.runAndWait()
    
    time.sleep(1)
    
    # Method 2: In thread (non-blocking)
    print("   Method 2: Threaded voice...")
    def speak_async():
        engine2 = pyttsx3.init()
        engine2.setProperty('rate', 130)
        engine2.setProperty('volume', 1.0)
        engine2.say(message)
        engine2.runAndWait()
    
    thread = threading.Thread(target=speak_async)
    thread.start()
    thread.join()  # Wait for completion
    
    print("\nTest complete!")
    print("If you heard beeps and voice both times, TTS is working correctly.")
    print("If you only heard beeps, there may be a TTS configuration issue.")

if __name__ == "__main__":
    test_help_alert()
