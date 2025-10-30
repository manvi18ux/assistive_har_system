# Assistive HAR System - Real-time Human Activity Recognition

A comprehensive AI-driven monitoring system for elderly care and patient assistance using computer vision and real-time alerts.

## 🌟 Features

### Core Functionality
- **Real-time Gesture Recognition**
  - Wave detection
  - Thumbs up
  - Victory/Peace sign
  - **STOP gesture** (open palm)
  - Help pose (both hands raised)

- **Activity Detection**
  - Sitting/Standing posture
  - Walking detection
  - **Fall detection** with immediate alerts
  - Body posture monitoring
  - **NEW: Activity Duration Tracking** with health warnings

- **Multi-Channel Alert System**
  - **Text-to-Speech (TTS)** announcements
  - **SMS alerts** for critical events
  - Visual alerts with color coding
  - Sound alarms for emergencies
  - Web dashboard notifications

- **Monitoring Dashboard**
  - Real-time activity display
  - Statistics tracking
  - Alert history
  - System status monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Webcam
- Windows OS (for TTS functionality)

### Installation

1. **Clone or navigate to the project directory**
```bash
cd hand_body_gestures
```

2. **Create a virtual environment (recommended)**
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the System

1. **Start the main HAR system**
```bash
python gesture_holistic.py
```

2. **Start the monitoring dashboard (optional, in a new terminal)**
```bash
python dashboard.py
```
Then open your browser and go to: `http://127.0.0.1:5000`

## 📱 SMS Alert Configuration (Optional)

To enable SMS alerts for fall detection:

1. Run the system once to generate `sms_config.json`
2. Edit `sms_config.json` with your settings:

### Option 1: Email-to-SMS (Free)
```json
{
  "enabled": true,
  "provider": "email",
  "emergency_contacts": [
    {
      "name": "Emergency Contact",
      "number": "1234567890",
      "carrier": "att"
    }
  ],
  "email": {
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-password"
  }
}
```

### Option 2: Twilio (Paid)
```json
{
  "enabled": true,
  "provider": "twilio",
  "twilio": {
    "account_sid": "your-account-sid",
    "auth_token": "your-auth-token",
    "from_number": "+1234567890"
  }
}
```

## 🎯 Key Features Explained

### Activity Duration Tracking (NEW!)
- **Automatic Duration Monitoring**: Tracks how long you've been sitting, standing, or walking
- **Health Warnings**: 
  - Sitting too long (30 min warning, 60 min critical)
  - Standing too long (20 min warning, 40 min critical)
  - Movement reminders (every 15 minutes of inactivity)
- **Visual Indicators**: Color-coded duration display
  - Green: Healthy duration
  - Yellow/Orange: Warning threshold reached
  - Red: Critical - immediate action needed
- **Daily Statistics**: 
  - Total time in each activity
  - Longest continuous periods
  - Number of health warnings issued

### Fall Detection
- Monitors shoulder position changes and torso angle
- Triggers **critical alert** with:
  - Loud TTS announcement
  - Alarm sound
  - SMS to emergency contacts (if configured)
  - Dashboard emergency banner

### Help Gesture
- Detected when both hands are raised above head
- Triggers **high priority alert**
- Useful for conscious requests for assistance

### Stop Gesture
- Open palm with all fingers extended
- Can be used to:
  - Signal "stop" or "wait"
  - Pause activities
  - Get attention

### Dashboard Features
- **Real-time Statistics**: Falls, help requests, gestures
- **Alert History**: Last 50 alerts with timestamps
- **Activity Log**: Recent activities detected
- **Emergency Banner**: Appears for critical alerts

## 📊 System Architecture

```
┌─────────────────────┐
│   Camera Input      │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  MediaPipe Holistic │
│   (Pose + Hands)    │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Gesture Detection  │
│  - Hand gestures    │
│  - Body postures    │
│  - Fall detection   │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│   Alert Manager     │
│  - TTS alerts       │
│  - SMS alerts       │
│  - Logging          │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Dashboard (Flask)  │
│  - Web interface    │
│  - Real-time data   │
└─────────────────────┘
```

## 🔧 Configuration

Edit `config.json` to customize:
- Detection thresholds
- Alert cooldown periods
- Dashboard settings
- Gesture sensitivity

## 📝 Logs and Data

- **activity_log.json**: All alerts and events
- **session_stats.json**: Session statistics
- **sms_config.json**: SMS configuration

## 🎮 Controls

- **ESC**: Exit the application
- **Dashboard**: Auto-updates every 2 seconds

## 🚨 Alert Priority Levels

1. **Critical** (Red): Fall detection
2. **High** (Orange): Help requests, Stop gestures
3. **Normal** (Green): Regular gestures

## 🛠️ Troubleshooting

### TTS Not Working
- Ensure `pyttsx3` is installed
- Check Windows audio settings
- Try running as administrator

### Camera Not Opening
- Check if another application is using the camera
- Try changing camera index in code (0, 1, 2...)

### Dashboard Not Loading
- Ensure Flask is installed
- Check if port 5000 is available
- Try accessing `http://localhost:5000`

## 📈 Performance Tips

- Ensure good lighting for better detection
- Position camera at chest/shoulder height
- Maintain 3-6 feet distance from camera
- Avoid cluttered backgrounds

## 🔐 Privacy & Security

- All processing is done locally
- No data is sent to external servers (except SMS if configured)
- Logs are stored locally

## 📚 Use Cases

1. **Elderly Care Facilities**
   - Monitor multiple residents
   - Immediate fall detection
   - Non-verbal communication

2. **Home Care**
   - Remote monitoring
   - Emergency alerts to family
   - Activity tracking

3. **Rehabilitation Centers**
   - Posture monitoring
   - Activity analysis
   - Progress tracking

## 🤝 Contributing

Feel free to enhance the system with:
- Additional gestures
- IoT device integration
- Mobile app companion
- Cloud storage for logs
- Multi-camera support

## 📄 License

This project is for educational and assistive purposes.

## 🙏 Acknowledgments

- MediaPipe by Google for pose and hand detection
- OpenCV for computer vision capabilities
- Flask for web dashboard framework

---

**Important**: This system is designed to assist but not replace professional medical care. Always consult healthcare providers for medical decisions.
