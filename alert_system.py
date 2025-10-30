import pyttsx3
import threading
import time
import json
import requests
from datetime import datetime
from collections import deque
import winsound
import queue

class AlertSystem:
    def __init__(self, config):
        self.config = config
        self.tts_engine = None
        self.alert_queue = queue.Queue()
        self.alert_history = deque(maxlen=100)
        self.last_alert_times = {}
        self.alert_thread = None
        self.running = False
        
        # Initialize TTS if enabled
        if config['alerts']['tts_enabled']:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
                self.tts_engine.setProperty('volume', 0.9)
            except Exception as e:
                print(f"TTS initialization failed: {e}")
                self.tts_engine = None
        
        # Start alert processing thread
        self.start()
    
    def start(self):
        """Start the alert processing thread"""
        self.running = True
        self.alert_thread = threading.Thread(target=self._process_alerts, daemon=True)
        self.alert_thread.start()
    
    def stop(self):
        """Stop the alert processing thread"""
        self.running = False
        if self.alert_thread:
            self.alert_thread.join(timeout=2)
    
    def _process_alerts(self):
        """Process alerts from the queue"""
        while self.running:
            try:
                if not self.alert_queue.empty():
                    alert = self.alert_queue.get(timeout=0.1)
                    self._handle_alert(alert)
                else:
                    time.sleep(0.1)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Alert processing error: {e}")
    
    def _handle_alert(self, alert):
        """Handle individual alert based on type"""
        alert_type = alert['type']
        message = alert['message']
        priority = alert.get('priority', 'normal')
        
        # Log the alert
        self._log_alert(alert)
        
        # Handle different alert channels
        if self.config['alerts']['tts_enabled'] and self.tts_engine:
            self._speak(message)
        
        if priority == 'high':
            self._play_alarm()
        
        if self.config['alerts']['sms_enabled'] and priority == 'critical':
            self._send_sms(message)
        
        if self.config['alerts']['dashboard_enabled']:
            self._send_to_dashboard(alert)
    
    def _speak(self, text):
        """Text-to-speech announcement"""
        try:
            if self.tts_engine:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
        except Exception as e:
            print(f"TTS error: {e}")
    
    def _play_alarm(self):
        """Play alarm sound for high priority alerts"""
        try:
            # Windows beep
            winsound.Beep(1000, 500)  # 1000Hz for 500ms
            time.sleep(0.2)
            winsound.Beep(1500, 500)  # 1500Hz for 500ms
        except Exception as e:
            print(f"Alarm sound error: {e}")
    
    def _send_sms(self, message):
        """Send SMS alert (requires Twilio configuration)"""
        try:
            if not all([self.config['sms'].get('twilio_account_sid'),
                       self.config['sms'].get('twilio_auth_token'),
                       self.config['sms'].get('twilio_phone_number')]):
                print("SMS not configured. Please add Twilio credentials to config.json")
                return
            
            # Twilio SMS implementation would go here
            # For now, we'll just log it
            print(f"SMS Alert (simulated): {message}")
            
        except Exception as e:
            print(f"SMS error: {e}")
    
    def _send_to_dashboard(self, alert):
        """Send alert to dashboard via HTTP"""
        try:
            # Send to dashboard endpoint
            requests.post(
                f"http://{self.config['dashboard']['host']}:{self.config['dashboard']['port']}/api/alert",
                json=alert,
                timeout=1
            )
        except Exception:
            # Dashboard might not be running, that's okay
            pass
    
    def _log_alert(self, alert):
        """Log alert to history"""
        alert['timestamp'] = datetime.now().isoformat()
        self.alert_history.append(alert)
        
        # Save to file if logging enabled
        if self.config['logging']['enabled']:
            try:
                with open(self.config['logging']['log_file'], 'a') as f:
                    json.dump(alert, f)
                    f.write('\n')
            except Exception as e:
                print(f"Logging error: {e}")
    
    def trigger_alert(self, alert_type, message, priority='normal', cooldown_key=None):
        """
        Trigger an alert with cooldown support
        
        Args:
            alert_type: Type of alert (fall, help, gesture, etc.)
            message: Alert message
            priority: Alert priority (normal, high, critical)
            cooldown_key: Key for cooldown checking
        """
        # Check cooldown
        if cooldown_key:
            cooldown_time = self._get_cooldown_time(alert_type)
            if cooldown_key in self.last_alert_times:
                time_since_last = time.time() - self.last_alert_times[cooldown_key]
                if time_since_last < cooldown_time:
                    return False
            self.last_alert_times[cooldown_key] = time.time()
        
        # Queue the alert
        alert = {
            'type': alert_type,
            'message': message,
            'priority': priority,
            'timestamp': time.time()
        }
        self.alert_queue.put(alert)
        return True
    
    def _get_cooldown_time(self, alert_type):
        """Get cooldown time for specific alert type"""
        if alert_type == 'fall':
            return self.config['alerts'].get('fall_alert_cooldown', 30)
        elif alert_type == 'help':
            return self.config['alerts'].get('help_alert_cooldown', 10)
        else:
            return 5  # Default cooldown
    
    def get_alert_history(self, limit=50):
        """Get recent alert history"""
        return list(self.alert_history)[-limit:]


class IoTController:
    """Control IoT devices (lights, alarms, etc.)"""
    
    def __init__(self, config):
        self.config = config
        self.devices = {}
    
    def register_device(self, device_id, device_type, endpoint):
        """Register an IoT device"""
        self.devices[device_id] = {
            'type': device_type,
            'endpoint': endpoint,
            'status': 'offline'
        }
    
    def trigger_device(self, device_id, action):
        """Trigger an IoT device action"""
        if device_id not in self.devices:
            return False
        
        device = self.devices[device_id]
        try:
            # Send command to IoT device
            response = requests.post(
                device['endpoint'],
                json={'action': action},
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            print(f"IoT device error: {e}")
            return False
    
    def emergency_mode(self):
        """Activate all emergency devices"""
        for device_id, device in self.devices.items():
            if device['type'] in ['alarm', 'light', 'siren']:
                self.trigger_device(device_id, 'activate')
