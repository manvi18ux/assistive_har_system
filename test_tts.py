import pyttsx3
import winsound
import time

print("Testing TTS and sound alerts...")

# Test TTS
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 130)
    engine.setProperty('volume', 1.0)
    
    print("Testing voice alert...")
    engine.say("URGENT! Help requested! Someone needs immediate assistance! Please check on them now!")
    engine.runAndWait()
    print("Voice alert complete!")
    
except Exception as e:
    print(f"TTS Error: {e}")

# Test beep sounds
try:
    print("\nTesting beep sounds...")
    for i in range(3):
        winsound.Beep(2000, 300)
        time.sleep(0.1)
    print("Beep test complete!")
except Exception as e:
    print(f"Sound Error: {e}")

print("\nTest finished! If you heard the voice and beeps, TTS is working.")
