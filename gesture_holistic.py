import cv2
import mediapipe as mp
import collections
import numpy as np
import time
import math
import pyttsx3
import threading
import json
from datetime import datetime
import winsound
import queue
import requests

# ---------- MediaPipe Setup ----------
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
mp_pose = mp.solutions.pose

# Pose landmarks
LEFT_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
RIGHT_SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
LEFT_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
RIGHT_HIP = mp_pose.PoseLandmark.RIGHT_HIP.value
LEFT_KNEE = mp_pose.PoseLandmark.LEFT_KNEE.value
RIGHT_KNEE = mp_pose.PoseLandmark.RIGHT_KNEE.value
NOSE = mp_pose.PoseLandmark.NOSE.value
LEFT_ANKLE = mp_pose.PoseLandmark.LEFT_ANKLE.value
RIGHT_ANKLE = mp_pose.PoseLandmark.RIGHT_ANKLE.value

# Hand landmarks
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20
WRIST_HAND = 0
INDEX_MCP = 5
MIDDLE_MCP = 9
RING_MCP = 13
PINKY_MCP = 17

# ---------- Activity Tracker ----------
class ActivityTracker:
    def __init__(self):
        self.current_activity = None
        self.activity_start_time = None
        self.activity_durations = {
            'Sitting': [],
            'Standing': [],
            'Walking': [],
            'Unknown': []
        }
        self.last_warning_times = {
            'sitting_too_long': 0,
            'standing_too_long': 0,
            'inactivity': 0
        }
        
        # Configurable thresholds (in seconds)
        self.thresholds = {
            'sitting_warning': 1800,  # 30 minutes
            'sitting_critical': 3600,  # 60 minutes
            'standing_warning': 1200,  # 20 minutes
            'standing_critical': 2400,  # 40 minutes
            'inactivity_warning': 600,  # 10 minutes
            'movement_reminder': 900   # 15 minutes
        }
        
        self.last_movement_time = time.time()
        self.daily_stats = {
            'total_sitting': 0,
            'total_standing': 0,
            'total_walking': 0,
            'longest_sitting': 0,
            'longest_standing': 0,
            'warnings_issued': 0
        }
    
    def update_activity(self, new_activity, alert_manager=None):
        """Update current activity and track durations"""
        current_time = time.time()
        
        # Track activity change
        if self.current_activity != new_activity:
            # Save duration of previous activity
            if self.current_activity and self.activity_start_time:
                duration = current_time - self.activity_start_time
                self.activity_durations[self.current_activity].append({
                    'duration': duration,
                    'end_time': current_time
                })
                
                # Update daily stats
                if self.current_activity == 'Sitting':
                    self.daily_stats['total_sitting'] += duration
                    self.daily_stats['longest_sitting'] = max(self.daily_stats['longest_sitting'], duration)
                elif self.current_activity == 'Standing':
                    self.daily_stats['total_standing'] += duration
                    self.daily_stats['longest_standing'] = max(self.daily_stats['longest_standing'], duration)
                elif self.current_activity == 'Walking':
                    self.daily_stats['total_walking'] += duration
                    self.last_movement_time = current_time
            
            # Start tracking new activity
            self.current_activity = new_activity
            self.activity_start_time = current_time
            
            # Reset movement time if walking
            if new_activity == 'Walking':
                self.last_movement_time = current_time
        
        # Check for health warnings
        if self.current_activity and self.activity_start_time and alert_manager:
            duration = current_time - self.activity_start_time
            self._check_health_warnings(duration, alert_manager)
    
    def _check_health_warnings(self, duration, alert_manager):
        """Check and issue health warnings based on activity duration"""
        current_time = time.time()
        
        # Sitting too long warnings
        if self.current_activity == 'Sitting':
            if duration > self.thresholds['sitting_critical']:
                if current_time - self.last_warning_times['sitting_too_long'] > 600:  # 10 min cooldown
                    alert_manager.trigger_alert(
                        'health_warning',
                        f'Critical: You have been sitting for {int(duration/60)} minutes. Please stand up and move around immediately!',
                        priority='critical',
                        cooldown=600
                    )
                    self.last_warning_times['sitting_too_long'] = current_time
                    self.daily_stats['warnings_issued'] += 1
            elif duration > self.thresholds['sitting_warning']:
                if current_time - self.last_warning_times['sitting_too_long'] > 900:  # 15 min cooldown
                    alert_manager.trigger_alert(
                        'health_warning',
                        f'Health Alert: You have been sitting for {int(duration/60)} minutes. Consider taking a break.',
                        priority='high',
                        cooldown=900
                    )
                    self.last_warning_times['sitting_too_long'] = current_time
                    self.daily_stats['warnings_issued'] += 1
        
        # Standing too long warnings
        elif self.current_activity == 'Standing':
            if duration > self.thresholds['standing_critical']:
                if current_time - self.last_warning_times['standing_too_long'] > 600:
                    alert_manager.trigger_alert(
                        'health_warning',
                        f'Alert: You have been standing for {int(duration/60)} minutes. Consider sitting down to rest.',
                        priority='high',
                        cooldown=600
                    )
                    self.last_warning_times['standing_too_long'] = current_time
                    self.daily_stats['warnings_issued'] += 1
            elif duration > self.thresholds['standing_warning']:
                if current_time - self.last_warning_times['standing_too_long'] > 900:
                    alert_manager.trigger_alert(
                        'health_warning',
                        f'Reminder: You have been standing for {int(duration/60)} minutes. Take a short break if needed.',
                        priority='normal',
                        cooldown=900
                    )
                    self.last_warning_times['standing_too_long'] = current_time
        
        # General inactivity warning (no walking for too long)
        time_since_movement = current_time - self.last_movement_time
        if time_since_movement > self.thresholds['movement_reminder']:
            if current_time - self.last_warning_times['inactivity'] > 1200:  # 20 min cooldown
                alert_manager.trigger_alert(
                    'health_warning',
                    f'Movement Reminder: You haven\'t walked for {int(time_since_movement/60)} minutes. A short walk would be beneficial.',
                    priority='normal',
                    cooldown=1200
                )
                self.last_warning_times['inactivity'] = current_time
                self.daily_stats['warnings_issued'] += 1
    
    def get_current_duration(self):
        """Get duration of current activity"""
        if self.current_activity and self.activity_start_time:
            return time.time() - self.activity_start_time
        return 0
    
    def get_activity_summary(self):
        """Get summary of activity durations"""
        summary = {
            'current_activity': self.current_activity,
            'current_duration': self.get_current_duration(),
            'daily_stats': self.daily_stats,
            'last_movement': time.time() - self.last_movement_time
        }
        return summary
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        self.daily_stats = {
            'total_sitting': 0,
            'total_standing': 0,
            'total_walking': 0,
            'longest_sitting': 0,
            'longest_standing': 0,
            'warnings_issued': 0
        }

# ---------- Alert Manager ----------
class AlertManager:
    def __init__(self):
        self.tts_engine = None
        self.alert_queue = queue.Queue()
        self.alert_history = []
        self.last_alert_times = {}
        self.running = True
        
        # Initialize TTS
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 130)  # Slower for clarity
            self.tts_engine.setProperty('volume', 1.0)  # Maximum volume
            
            # Test TTS on startup
            print("Initializing Text-to-Speech engine...")
            self.tts_engine.say("Voice alerts activated")
            self.tts_engine.runAndWait()
            print("TTS initialized successfully!")
            
            # Optional: Select a clearer voice if available
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Use the first available voice (usually clearer)
                self.tts_engine.setProperty('voice', voices[0].id)
        except Exception as e:
            print(f"TTS init failed: {e}")
            self.tts_engine = None
        
        # Start alert thread
        self.alert_thread = threading.Thread(target=self._process_alerts, daemon=True)
        self.alert_thread.start()
    
    def _process_alerts(self):
        while self.running:
            try:
                if not self.alert_queue.empty():
                    alert = self.alert_queue.get(timeout=0.1)
                    self._handle_alert(alert)
                else:
                    time.sleep(0.1)
            except:
                continue
    
    def _handle_alert(self, alert):
        # Check cooldown
        alert_type = alert['type']
        cooldown = alert.get('cooldown', 5)
        
        if alert_type in self.last_alert_times:
            if time.time() - self.last_alert_times[alert_type] < cooldown:
                return
        
        self.last_alert_times[alert_type] = time.time()
        
        # Log alert
        alert['timestamp'] = datetime.now().isoformat()
        self.alert_history.append(alert)
        self._save_to_log(alert)
        
        # Send to dashboard
        self._send_to_dashboard(alert)
        
        # Speak alert in a separate thread to avoid blocking
        if self.tts_engine and alert.get('speak', True):
            def speak_async():
                try:
                    print(f"Speaking: {alert['message']}")
                    self.tts_engine.say(alert['message'])
                    self.tts_engine.runAndWait()
                    print("Speech complete")
                except Exception as e:
                    print(f"TTS error: {e}")
            
            # Start speech in new thread
            speech_thread = threading.Thread(target=speak_async, daemon=True)
            speech_thread.start()
        
        # Play sound for critical alerts
        if alert.get('priority') == 'critical':
            try:
                # Play multiple beeps for urgent attention
                if alert.get('type') == 'help':
                    # Special pattern for help: 3 quick beeps
                    for _ in range(3):
                        winsound.Beep(2000, 300)
                        time.sleep(0.1)
                else:
                    # Single long beep for other critical alerts
                    winsound.Beep(1500, 500)
            except:
                pass
    
    def _save_to_log(self, alert):
        try:
            with open('activity_log.json', 'a') as f:
                json.dump(alert, f)
                f.write('\n')
        except:
            pass
    
    def trigger_alert(self, alert_type, message, priority='normal', cooldown=5):
        alert = {
            'type': alert_type,
            'message': message,
            'priority': priority,
            'cooldown': cooldown,
            'speak': True
        }
        self.alert_queue.put(alert)
    
    def _send_to_dashboard(self, alert):
        """Send alert to dashboard"""
        try:
            requests.post(
                'http://127.0.0.1:5000/api/alert',
                json=alert,
                timeout=0.5
            )
        except:
            pass  # Dashboard might not be running
    
    def send_activity_update(self, activity):
        """Send current activity to dashboard"""
        try:
            requests.post(
                'http://127.0.0.1:5000/api/activity',
                json={'activity': activity},
                timeout=0.5
            )
        except:
            pass
    
    def stop(self):
        self.running = False

# ---------- Wave Detector ----------
class WaveDetector:
    def __init__(self, maxlen=12):
        self.history = collections.deque(maxlen=maxlen)
        self.last_wave_time = 0

    def add_position(self, x):
        self.history.append(x)

    def detect_wave(self):
        if len(self.history) < 6:
            return False
        arr = np.array(self.history)
        amplitude = arr.max() - arr.min()
        sign_changes = np.sum(np.abs(np.diff(np.sign(np.diff(arr)))))
        now = time.time()
        if amplitude > 0.12 and sign_changes >= 2 and (now - self.last_wave_time) > 1.0:
            self.last_wave_time = now
            return True
        return False

# ---------- Hand Gestures ----------
def is_finger_folded(hand, tip, mcp):
    return hand.landmark[tip].y > hand.landmark[mcp].y

def is_finger_extended(hand, tip, mcp):
    return hand.landmark[tip].y < hand.landmark[mcp].y

def is_thumbs_up(hand):
    try:
        wrist_y = hand.landmark[WRIST_HAND].y
        thumb_tip_y = hand.landmark[THUMB_TIP].y
        folded = (
            is_finger_folded(hand, INDEX_TIP, INDEX_MCP) and
            is_finger_folded(hand, MIDDLE_TIP, MIDDLE_MCP) and
            is_finger_folded(hand, RING_TIP, RING_MCP) and
            is_finger_folded(hand, PINKY_TIP, PINKY_MCP)
        )
        return (thumb_tip_y < wrist_y - 0.02) and folded
    except:
        return False

def is_victory(hand):
    try:
        return (is_finger_extended(hand, INDEX_TIP, INDEX_MCP) and
                is_finger_extended(hand, MIDDLE_TIP, MIDDLE_MCP) and
                is_finger_folded(hand, RING_TIP, RING_MCP) and
                is_finger_folded(hand, PINKY_TIP, PINKY_MCP))
    except:
        return False

def is_stop_gesture(hand):
    """Detect stop gesture (open palm with all fingers extended)"""
    try:
        # Check if all fingers are extended
        all_extended = (
            is_finger_extended(hand, INDEX_TIP, INDEX_MCP) and
            is_finger_extended(hand, MIDDLE_TIP, MIDDLE_MCP) and
            is_finger_extended(hand, RING_TIP, RING_MCP) and
            is_finger_extended(hand, PINKY_TIP, PINKY_MCP)
        )
        # Check if thumb is also extended (away from palm)
        thumb_extended = hand.landmark[THUMB_TIP].x > hand.landmark[INDEX_MCP].x + 0.05 or \
                        hand.landmark[THUMB_TIP].x < hand.landmark[INDEX_MCP].x - 0.05
        return all_extended and thumb_extended
    except:
        return False

def is_help_pose(left_hand, right_hand, pose):
    try:
        if not left_hand or not right_hand or not pose:
            return False
        head_y = pose.landmark[NOSE].y
        left_wrist_y = left_hand.landmark[WRIST_HAND].y
        right_wrist_y = right_hand.landmark[WRIST_HAND].y
        
        # Check if both hands are above head
        is_help = (left_wrist_y < head_y - 0.05 and right_wrist_y < head_y - 0.05)
        
        if is_help:
            print(f"HELP DETECTED! Left wrist: {left_wrist_y:.2f}, Right wrist: {right_wrist_y:.2f}, Head: {head_y:.2f}")
        
        return is_help
    except Exception as e:
        print(f"Help pose detection error: {e}")
        return False

# ---------- Body Gestures ----------
def get_landmark(pose, idx):
    return pose.landmark[idx] if pose else None

def detect_posture(pose):
    try:
        lh = get_landmark(pose, LEFT_HIP)
        lk = get_landmark(pose, LEFT_KNEE)
        if None in [lh, lk]:
            return "Unknown"
        left_leg = abs(lh.y - lk.y)
        if 0.05 < left_leg < 0.20:
            return "Sitting"
        return "Standing"
    except:
        return "Unknown"

def detect_walking(pose, history, maxlen=15, x_threshold=0.03, angle_threshold=5):
    """
    Detect walking based on:
    1. Ankle horizontal movement
    2. Knee vertical oscillation
    3. Leg angles
    """
    try:
        la = get_landmark(pose, LEFT_ANKLE)
        ra = get_landmark(pose, RIGHT_ANKLE)
        lk = get_landmark(pose, LEFT_KNEE)
        rk = get_landmark(pose, RIGHT_KNEE)
        lh = get_landmark(pose, LEFT_HIP)
        rh = get_landmark(pose, RIGHT_HIP)

        if None in [la, ra, lk, rk, lh, rh]:
            return False

        # Store current frame info
        left_x = la.x
        right_x = ra.x
        left_knee_y = lk.y
        right_knee_y = rk.y
        left_leg_angle = math.degrees(math.atan2(lk.y - lh.y, lk.x - lh.x))
        right_leg_angle = math.degrees(math.atan2(rk.y - rh.y, rk.x - rh.x))

        history.append({
            'lx': left_x,
            'rx': right_x,
            'lyk': left_knee_y,
            'ryk': right_knee_y,
            'lla': left_leg_angle,
            'rla': right_leg_angle
        })

        if len(history) < maxlen:
            return False

        # Analyze ankle x movement
        left_xs = [f['lx'] for f in history]
        right_xs = [f['rx'] for f in history]
        left_range = max(left_xs) - min(left_xs)
        right_range = max(right_xs) - min(right_xs)

        # Analyze knee vertical oscillation
        left_knee_osc = max([f['lyk'] for f in history]) - min([f['lyk'] for f in history])
        right_knee_osc = max([f['ryk'] for f in history]) - min([f['ryk'] for f in history])

        # Analyze leg angles
        left_leg_angle_range = max([f['lla'] for f in history]) - min([f['lla'] for f in history])
        right_leg_angle_range = max([f['rla'] for f in history]) - min([f['rla'] for f in history])

        # Walking conditions: enough ankle movement OR knee oscillation OR leg angles
        if (left_range > x_threshold or right_range > x_threshold) and \
           (left_knee_osc > 0.02 or right_knee_osc > 0.02) and \
           (left_leg_angle_range > angle_threshold or right_leg_angle_range > angle_threshold):
            return True

    except:
        pass
    return False



def torso_angle(pose):
    ls = pose.landmark[LEFT_SHOULDER]
    rs = pose.landmark[RIGHT_SHOULDER]
    lh = pose.landmark[LEFT_HIP]
    rh = pose.landmark[RIGHT_HIP]
    shoulder_mid = ((ls.x + rs.x)/2, (ls.y + rs.y)/2)
    hip_mid = ((lh.x + rh.x)/2, (lh.y + rh.y)/2)
    dx = hip_mid[0] - shoulder_mid[0]
    dy = hip_mid[1] - shoulder_mid[1]
    angle = math.degrees(math.atan2(dy, dx))
    return abs(angle)

def detect_falling(pose, prev_shoulder_y, shoulder_threshold=0.05, angle_threshold=70):
    if not pose or prev_shoulder_y is None:
        return False
    ls = pose.landmark[LEFT_SHOULDER].y
    rs = pose.landmark[RIGHT_SHOULDER].y
    avg_shoulder = (ls + rs)/2
    drop = avg_shoulder - prev_shoulder_y
    angle = torso_angle(pose)
    if drop > shoulder_threshold and angle < angle_threshold:
        return True
    return False

# ---------- Main ----------
def main():
    # Try to open camera with different indices
    cap = None
    for camera_index in [0, 1, 2]:
        print(f"Trying camera index {camera_index}...")
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)  # Use DirectShow on Windows
        if cap.isOpened():
            # Test if we can actually read from it
            ret, test_frame = cap.read()
            if ret:
                print(f"Camera opened successfully at index {camera_index}!")
                # Set camera properties for better performance
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
                break
            else:
                print(f"Camera at index {camera_index} opened but cannot read frames")
                cap.release()
                cap = None
        else:
            print(f"No camera at index {camera_index}")
    
    if cap is None or not cap.isOpened():
        print("\n" + "="*50)
        print("ERROR: Cannot access camera!")
        print("="*50)
        print("\nPossible solutions:")
        print("1. Close other applications using the camera (Zoom, Teams, etc.)")
        print("2. Check Windows Camera permissions:")
        print("   - Go to Settings > Privacy > Camera")
        print("   - Make sure 'Allow apps to access your camera' is ON")
        print("3. Try unplugging and reconnecting your webcam")
        print("4. Restart your computer")
        print("\nPress Enter to exit...")
        input()
        return

    # Initialize alert manager and activity tracker
    alert_manager = AlertManager()
    activity_tracker = ActivityTracker()
    print("Alert system initialized. TTS enabled for fall detection and help gestures.")
    print("Activity tracking enabled with health warnings for prolonged inactivity.")
    
    shoulder_history = collections.deque(maxlen=3)
    ankle_history = collections.deque(maxlen=5)
    left_wave_detector = WaveDetector()
    right_wave_detector = WaveDetector()
    
    # Statistics tracking
    stats = {
        'falls_detected': 0,
        'help_requests': 0,
        'total_gestures': 0,
        'session_start': datetime.now()
    }
    
    # Track last dashboard update time
    last_update_time = time.time()

    with mp_holistic.Holistic(min_detection_confidence=0.5,
                              min_tracking_confidence=0.5) as holistic:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(image_rgb)
            annotated = frame.copy()

            # Draw landmarks
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(annotated, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
            if results.left_hand_landmarks:
                mp_drawing.draw_landmarks(annotated, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            if results.right_hand_landmarks:
                mp_drawing.draw_landmarks(annotated, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

            gesture_text = ""
            
            # Send periodic updates to dashboard (every 2 seconds)
            current_time = time.time()
            if current_time - last_update_time > 2:
                # Send a heartbeat update with current status
                if gesture_text == "":
                    alert_manager.send_activity_update("Monitoring...")
                
                # Send activity duration data to dashboard
                activity_summary = activity_tracker.get_activity_summary()
                try:
                    requests.post(
                        'http://127.0.0.1:5000/api/activity_duration',
                        json=activity_summary,
                        timeout=0.5
                    )
                except:
                    pass  # Dashboard might not be running
                
                last_update_time = current_time

            # ---------- Shoulder History ----------
            prev_shoulder_y = shoulder_history[0] if len(shoulder_history) == shoulder_history.maxlen else None
            if results.pose_landmarks:
                ls = results.pose_landmarks.landmark[LEFT_SHOULDER].y
                rs = results.pose_landmarks.landmark[RIGHT_SHOULDER].y
                avg_shoulder = (ls + rs)/2
                shoulder_history.append(avg_shoulder)

                falling = detect_falling(results.pose_landmarks, prev_shoulder_y)
                walking = detect_walking(results.pose_landmarks, ankle_history)
                posture = detect_posture(results.pose_landmarks)
                
                # Update activity tracker
                if walking:
                    activity_tracker.update_activity('Walking', alert_manager)
                elif posture == "Sitting":
                    activity_tracker.update_activity('Sitting', alert_manager)
                elif posture == "Standing":
                    activity_tracker.update_activity('Standing', alert_manager)
                else:
                    activity_tracker.update_activity('Unknown', alert_manager)

                if falling:
                    gesture_text = "FALL DETECTED!"
                    alert_manager.trigger_alert(
                        'fall', 
                        'Fall detected! Immediate assistance required!',
                        priority='critical',
                        cooldown=30
                    )
                    stats['falls_detected'] += 1
                    alert_manager.send_activity_update("FALL DETECTED")
                elif is_help_pose(results.left_hand_landmarks, results.right_hand_landmarks, results.pose_landmarks):
                    gesture_text = "HELP REQUESTED!"
                    print(">>> TRIGGERING HELP ALERT <<<")
                    alert_manager.trigger_alert(
                        'help',
                        'URGENT! Help requested! Someone needs immediate assistance! Please check on them now!',
                        priority='critical',  # Changed to critical for louder alert
                        cooldown=10
                    )
                    stats['help_requests'] += 1
                    alert_manager.send_activity_update("HELP REQUESTED")
                elif walking:
                    gesture_text = "Walking"
                    alert_manager.send_activity_update("Walking")
                else:
                    gesture_text = posture
                    alert_manager.send_activity_update(posture)

            # ---------- Left Hand ----------
            if gesture_text in ["Standing", "Sitting"]:
                if results.left_hand_landmarks:
                    lh = results.left_hand_landmarks
                    left_x = lh.landmark[WRIST_HAND].x
                    left_wave_detector.add_position(left_x)
                    if left_wave_detector.detect_wave():
                        gesture_text = "Left Hand: Wave"
                        alert_manager.trigger_alert('gesture', 'Wave gesture detected', cooldown=3)
                        alert_manager.send_activity_update("Wave Gesture (Left)")
                        stats['total_gestures'] += 1
                    elif is_thumbs_up(lh):
                        gesture_text = "Left Hand: Thumbs Up"
                        alert_manager.trigger_alert('gesture', 'Thumbs up detected', cooldown=3)
                        alert_manager.send_activity_update("Thumbs Up (Left)")
                        stats['total_gestures'] += 1
                    elif is_stop_gesture(lh):
                        gesture_text = "Left Hand: STOP"
                        alert_manager.trigger_alert('gesture', 'Stop gesture detected', priority='high', cooldown=5)
                        alert_manager.send_activity_update("STOP Gesture (Left)")
                        stats['total_gestures'] += 1
                    elif is_victory(lh):
                        gesture_text = "Left Hand: Victory"
                        alert_manager.send_activity_update("Victory Gesture (Left)")
                        stats['total_gestures'] += 1

            # ---------- Right Hand ----------
            if gesture_text in ["Standing", "Sitting"]:
                if results.right_hand_landmarks:
                    rh = results.right_hand_landmarks
                    right_x = rh.landmark[WRIST_HAND].x
                    right_wave_detector.add_position(right_x)
                    if right_wave_detector.detect_wave():
                        gesture_text = "Right Hand: Wave"
                        alert_manager.trigger_alert('gesture', 'Wave gesture detected', cooldown=3)
                        alert_manager.send_activity_update("Wave Gesture (Right)")
                        stats['total_gestures'] += 1
                    elif is_thumbs_up(rh):
                        gesture_text = "Right Hand: Thumbs Up"
                        alert_manager.trigger_alert('gesture', 'Thumbs up detected', cooldown=3)
                        alert_manager.send_activity_update("Thumbs Up (Right)")
                        stats['total_gestures'] += 1
                    elif is_stop_gesture(rh):
                        gesture_text = "Right Hand: STOP"
                        alert_manager.trigger_alert('gesture', 'Stop gesture detected', priority='high', cooldown=5)
                        alert_manager.send_activity_update("STOP Gesture (Right)")
                        stats['total_gestures'] += 1
                    elif is_victory(rh):
                        gesture_text = "Right Hand: Victory"
                        alert_manager.send_activity_update("Victory Gesture (Right)")
                        stats['total_gestures'] += 1

            # ---------- Display ----------
            if gesture_text:
                # Color based on priority
                color = (0, 255, 0)  # Green default
                if "FALL" in gesture_text or "HELP" in gesture_text:
                    color = (0, 0, 255)  # Red for critical
                elif "STOP" in gesture_text:
                    color = (0, 165, 255)  # Orange for stop
                
                cv2.putText(annotated, gesture_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 2)
            
            # Display stats
            cv2.putText(annotated, f"Falls: {stats['falls_detected']}", (30, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(annotated, f"Help Requests: {stats['help_requests']}", (30, 125), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(annotated, f"Total Gestures: {stats['total_gestures']}", (30, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Display activity duration
            activity_summary = activity_tracker.get_activity_summary()
            current_duration = activity_summary['current_duration']
            if current_duration > 0:
                duration_text = f"{activity_summary['current_activity']}: {int(current_duration/60)}m {int(current_duration%60)}s"
                # Color code based on duration
                duration_color = (0, 255, 0)  # Green
                if activity_summary['current_activity'] == 'Sitting':
                    if current_duration > activity_tracker.thresholds['sitting_critical']:
                        duration_color = (0, 0, 255)  # Red
                    elif current_duration > activity_tracker.thresholds['sitting_warning']:
                        duration_color = (0, 165, 255)  # Orange
                elif activity_summary['current_activity'] == 'Standing':
                    if current_duration > activity_tracker.thresholds['standing_critical']:
                        duration_color = (0, 165, 255)  # Orange
                    elif current_duration > activity_tracker.thresholds['standing_warning']:
                        duration_color = (0, 255, 255)  # Yellow
                
                cv2.putText(annotated, duration_text, (30, 175), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, duration_color, 2)
                
            # Display health warnings count
            cv2.putText(annotated, f"Health Warnings: {activity_summary['daily_stats']['warnings_issued']}", 
                       (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Display time since last movement
            time_since_movement = activity_summary['last_movement']
            if time_since_movement > 60:
                movement_text = f"Last walked: {int(time_since_movement/60)}m ago"
                movement_color = (0, 255, 255) if time_since_movement < 900 else (0, 165, 255)
                cv2.putText(annotated, movement_text, (30, 225), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, movement_color, 1)

            cv2.imshow("Assistive HAR System - Real-time Monitoring", annotated)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit
                break

    # Cleanup
    alert_manager.stop()
    cap.release()
    cv2.destroyAllWindows()
    
    # Save session stats
    stats['session_end'] = datetime.now()
    
    # Add activity tracking stats
    activity_summary = activity_tracker.get_activity_summary()
    stats['activity_durations'] = {
        'total_sitting_minutes': round(activity_summary['daily_stats']['total_sitting'] / 60, 2),
        'total_standing_minutes': round(activity_summary['daily_stats']['total_standing'] / 60, 2),
        'total_walking_minutes': round(activity_summary['daily_stats']['total_walking'] / 60, 2),
        'longest_sitting_minutes': round(activity_summary['daily_stats']['longest_sitting'] / 60, 2),
        'longest_standing_minutes': round(activity_summary['daily_stats']['longest_standing'] / 60, 2),
        'health_warnings_issued': activity_summary['daily_stats']['warnings_issued']
    }
    
    with open('session_stats.json', 'w') as f:
        json.dump(stats, f, default=str, indent=2)
    print(f"\nSession ended. Stats saved to session_stats.json")
    print(f"Falls detected: {stats['falls_detected']}")
    print(f"Help requests: {stats['help_requests']}")
    print(f"Total gestures: {stats['total_gestures']}")
    print(f"\nActivity Summary:")
    print(f"Total sitting: {stats['activity_durations']['total_sitting_minutes']:.1f} minutes")
    print(f"Total standing: {stats['activity_durations']['total_standing_minutes']:.1f} minutes")
    print(f"Total walking: {stats['activity_durations']['total_walking_minutes']:.1f} minutes")
    print(f"Longest sitting period: {stats['activity_durations']['longest_sitting_minutes']:.1f} minutes")
    print(f"Health warnings issued: {stats['activity_durations']['health_warnings_issued']}")

if __name__ == "__main__":
    main()
