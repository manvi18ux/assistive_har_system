# Assistive HAR System - Real-time Human Activity Recognition

A comprehensive AI-driven monitoring system for elderly care and patient assistance using computer vision and real-time alerts.

## 🌟 Features
````markdown
# AI Guardian — Assistive HAR System (Alerts-focused)

AI Guardian is an assistive human activity recognition (HAR) system that detects hand and body gestures in
real-time and surfaces alerts through a local dashboard and voice feedback.

About alerts
------------
This README now focuses on the alerting capabilities of the system. Alerts are produced by the gesture and
posture detection pipeline and are intended to notify caregivers or monitoring systems about important events.

Primary alert channels
- Dashboard (HTTP): All alerts are posted to the Flask dashboard endpoints (e.g. `/api/alert`) and shown in
  the UI.
- Local voice (TTS): The system can announce alerts locally using the TTS engine.

Removed from the About text: SMS alerting is not described here (it may remain in the codebase), so the
primary documented channels are dashboard + TTS.

Key gestures and alert types
- thumbs_up — confirmation/acknowledgement gesture (informational)
- victory — celebratory/positive event (informational)
- stop — open palm / stop gesture (high priority)
- help — both hands raised / help request (high priority)

Alert priorities
- Critical: fall detection (immediate attention required)
- High: `help` and `stop` gestures (urgent, actionable)
- Normal: `thumbs_up`, `victory` (informational)

Files of interest
- `gesture_holistic.py` — core camera loop and gesture detection
- `dashboard.py` — Flask server and REST endpoints for status and alerts
- `static/` and `templates/` — front-end assets (dashboard UI)

Quick start (short)
1. Install dependencies: `pip install -r requirements.txt`
2. Start detector: `python gesture_holistic.py`
3. Start dashboard: `python dashboard.py` and open `http://127.0.0.1:5000`



````
python -m venv venv
