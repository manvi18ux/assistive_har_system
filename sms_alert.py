"""
SMS Alert Module for Assistive HAR System
Supports multiple SMS providers: Twilio, Email-to-SMS gateways
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import requests
from datetime import datetime
import time

class SMSAlert:
    def __init__(self, config_file='sms_config.json'):
        """Initialize SMS alert system with configuration"""
        self.config = self.load_config(config_file)
        self.last_sms_time = {}
        self.sms_cooldown = 60  # Minimum 60 seconds between SMS to same number
        
    def load_config(self, config_file):
        """Load SMS configuration"""
        default_config = {
            'enabled': False,
            'provider': 'email',  # 'twilio' or 'email'
            'emergency_contacts': [],
            'email': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': '',
                'sender_password': '',
                'carrier_gateways': {
                    'att': '@txt.att.net',
                    'tmobile': '@tmomail.net',
                    'verizon': '@vtext.com',
                    'sprint': '@messaging.sprintpcs.com'
                }
            },
            'twilio': {
                'account_sid': '',
                'auth_token': '',
                'from_number': ''
            }
        }
        
        try:
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)
        except FileNotFoundError:
            # Save default config
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default SMS config file: {config_file}")
            print("Please configure SMS settings in sms_config.json to enable SMS alerts")
        
        return default_config
    
    def send_alert(self, message, alert_type='general', priority='normal'):
        """Send SMS alert to all emergency contacts"""
        if not self.config['enabled']:
            print("SMS alerts are disabled. Enable in sms_config.json")
            return False
        
        success_count = 0
        for contact in self.config['emergency_contacts']:
            if self._check_cooldown(contact['number']):
                if self._send_sms(contact, message, alert_type, priority):
                    success_count += 1
                    self.last_sms_time[contact['number']] = time.time()
        
        return success_count > 0
    
    def _check_cooldown(self, number):
        """Check if enough time has passed since last SMS to this number"""
        if number not in self.last_sms_time:
            return True
        return (time.time() - self.last_sms_time[number]) > self.sms_cooldown
    
    def _send_sms(self, contact, message, alert_type, priority):
        """Send SMS using configured provider"""
        try:
            if self.config['provider'] == 'email':
                return self._send_via_email(contact, message, alert_type)
            elif self.config['provider'] == 'twilio':
                return self._send_via_twilio(contact, message)
            else:
                print(f"Unknown SMS provider: {self.config['provider']}")
                return False
        except Exception as e:
            print(f"SMS send error: {e}")
            return False
    
    def _send_via_email(self, contact, message, alert_type):
        """Send SMS via email-to-SMS gateway"""
        email_config = self.config['email']
        
        if not email_config['sender_email'] or not email_config['sender_password']:
            print("Email credentials not configured for SMS alerts")
            return False
        
        # Construct recipient email based on carrier
        carrier = contact.get('carrier', 'att')
        gateway = email_config['carrier_gateways'].get(carrier, '@txt.att.net')
        recipient = contact['number'].replace('-', '').replace(' ', '') + gateway
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_config['sender_email']
        msg['To'] = recipient
        msg['Subject'] = f"HAR Alert: {alert_type.upper()}"
        
        # Format message for SMS (keep it short)
        sms_body = f"HAR ALERT [{alert_type.upper()}]: {message[:100]}"
        if alert_type == 'fall':
            sms_body += f"\nTime: {datetime.now().strftime('%H:%M')}"
            sms_body += "\nCALL 911 if emergency!"
        
        msg.attach(MIMEText(sms_body, 'plain'))
        
        try:
            # Send email
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['sender_email'], email_config['sender_password'])
                server.send_message(msg)
            
            print(f"SMS sent to {contact['name']} ({contact['number']})")
            return True
            
        except Exception as e:
            print(f"Email-to-SMS error: {e}")
            return False
    
    def _send_via_twilio(self, contact, message):
        """Send SMS via Twilio API"""
        twilio_config = self.config['twilio']
        
        if not all([twilio_config['account_sid'], 
                   twilio_config['auth_token'], 
                   twilio_config['from_number']]):
            print("Twilio credentials not configured")
            return False
        
        try:
            # Twilio API endpoint
            url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_config['account_sid']}/Messages.json"
            
            # Prepare request
            auth = (twilio_config['account_sid'], twilio_config['auth_token'])
            data = {
                'From': twilio_config['from_number'],
                'To': contact['number'],
                'Body': f"HAR Alert: {message[:160]}"  # SMS limit
            }
            
            # Send request
            response = requests.post(url, auth=auth, data=data)
            
            if response.status_code == 201:
                print(f"SMS sent via Twilio to {contact['name']}")
                return True
            else:
                print(f"Twilio error: {response.text}")
                return False
                
        except Exception as e:
            print(f"Twilio SMS error: {e}")
            return False
    
    def add_contact(self, name, number, carrier='att'):
        """Add emergency contact"""
        contact = {
            'name': name,
            'number': number,
            'carrier': carrier,
            'added': datetime.now().isoformat()
        }
        self.config['emergency_contacts'].append(contact)
        self.save_config()
        print(f"Added emergency contact: {name}")
    
    def remove_contact(self, number):
        """Remove emergency contact"""
        self.config['emergency_contacts'] = [
            c for c in self.config['emergency_contacts'] 
            if c['number'] != number
        ]
        self.save_config()
        print(f"Removed contact with number: {number}")
    
    def save_config(self):
        """Save configuration to file"""
        with open('sms_config.json', 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def test_sms(self):
        """Send test SMS to verify configuration"""
        return self.send_alert(
            "Test message from HAR System. SMS alerts are working!",
            alert_type='test',
            priority='low'
        )


# Integration with main alert system
def integrate_sms_with_alerts(alert_manager, sms_alert):
    """Add SMS capability to existing alert manager"""
    original_handle = alert_manager._handle_alert
    
    def enhanced_handle(alert):
        # Call original handler
        original_handle(alert)
        
        # Send SMS for critical alerts
        if alert.get('priority') == 'critical':
            sms_alert.send_alert(
                alert['message'],
                alert_type=alert['type'],
                priority=alert['priority']
            )
    
    alert_manager._handle_alert = enhanced_handle
    print("SMS alerts integrated with main system")


if __name__ == "__main__":
    # Test SMS system
    sms = SMSAlert()
    
    # Example: Add emergency contact
    # sms.add_contact("John Doe", "1234567890", "att")
    
    # Test SMS
    # sms.test_sms()
