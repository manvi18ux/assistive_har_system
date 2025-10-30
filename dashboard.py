from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
import threading
import time

app = Flask(__name__, static_folder='static')
CORS(app)

# Route configuration
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Global storage for real-time data
dashboard_data = {
    'current_activity': 'Unknown',
    'alerts': [],
    'statistics': {
        'falls_today': 0,
        'help_requests_today': 0,
        'total_gestures_today': 0,
        'last_fall_time': None,
        'last_help_time': None
    },
    'activity_log': [],
    'activity_duration': {
        'current_activity': 'Unknown',
        'current_duration': 0,
        'last_movement': 0,
        'daily_stats': {
            'total_sitting': 0,
            'total_standing': 0,
            'total_walking': 0,
            'longest_sitting': 0,
            'longest_standing': 0,
            'warnings_issued': 0
        }
    },
    'system_status': 'Active',
    'monitoring_started': datetime.now().isoformat()
}

# Lock for thread-safe operations
data_lock = threading.Lock()

@app.route('/')
def index():
    """Serve the enhanced dashboard page"""
    return render_template('dashboard_enhanced.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/api/status')
def get_status():
    """Get current system status"""
    with data_lock:
        return jsonify(dashboard_data)

@app.route('/api/alert', methods=['POST'])
def receive_alert():
    """Receive alert from the main system"""
    try:
        alert = request.json
        alert['received_at'] = datetime.now().isoformat()
        
        with data_lock:
            # Add to alerts list (keep last 50)
            dashboard_data['alerts'].insert(0, alert)
            dashboard_data['alerts'] = dashboard_data['alerts'][:50]
            
            # Update statistics
            if alert['type'] == 'fall':
                dashboard_data['statistics']['falls_today'] += 1
                dashboard_data['statistics']['last_fall_time'] = alert['received_at']
            elif alert['type'] == 'help':
                dashboard_data['statistics']['help_requests_today'] += 1
                dashboard_data['statistics']['last_help_time'] = alert['received_at']
            elif alert['type'] == 'gesture':
                dashboard_data['statistics']['total_gestures_today'] += 1
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/activity', methods=['POST'])
def update_activity():
    """Update current activity"""
    try:
        data = request.json
        activity = data.get('activity', 'Unknown')
        
        with data_lock:
            dashboard_data['current_activity'] = activity
            dashboard_data['activity_log'].insert(0, {
                'activity': activity,
                'timestamp': datetime.now().isoformat()
            })
            dashboard_data['activity_log'] = dashboard_data['activity_log'][:100]
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/activity_duration', methods=['POST'])
def update_activity_duration():
    """Receive activity duration data from main system"""
    try:
        data = request.json or {}
        print(f"[DEBUG] Received activity duration data: {data}")  # Debug log
        with data_lock:
            ad = dashboard_data['activity_duration']
            ad['current_activity'] = data.get('current_activity', ad['current_activity'])
            ad['current_duration'] = data.get('current_duration', ad['current_duration'])
            ad['last_movement'] = data.get('last_movement', ad['last_movement'])
            # Merge daily stats if provided
            if 'daily_stats' in data and isinstance(data['daily_stats'], dict):
                ad['daily_stats'].update(data['daily_stats'])
        print(f"[DEBUG] Updated dashboard_data['activity_duration']: {dashboard_data['activity_duration']}")  # Debug log
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f"[ERROR] Failed to update activity duration: {e}")  # Debug log
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/logs')
def get_logs():
    """Get activity logs from file"""
    logs = []
    try:
        if os.path.exists('activity_log.json'):
            with open('activity_log.json', 'r') as f:
                for line in f:
                    try:
                        logs.append(json.loads(line))
                    except:
                        continue
    except Exception as e:
        print(f"Error reading logs: {e}")
    
    # Return last 100 logs
    return jsonify(logs[-100:])

@app.route('/api/stats')
def get_stats():
    """Get session statistics"""
    stats = {}
    try:
        if os.path.exists('session_stats.json'):
            with open('session_stats.json', 'r') as f:
                stats = json.load(f)
    except Exception as e:
        print(f"Error reading stats: {e}")
    
    return jsonify(stats)

def cleanup_daily_stats():
    """Reset daily statistics at midnight"""
    while True:
        time.sleep(3600)  # Check every hour
        current_hour = datetime.now().hour
        if current_hour == 0:  # Midnight
            with data_lock:
                dashboard_data['statistics']['falls_today'] = 0
                dashboard_data['statistics']['help_requests_today'] = 0
                dashboard_data['statistics']['total_gestures_today'] = 0

if __name__ == '__main__':
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_daily_stats, daemon=True)
    cleanup_thread.start()
    
    print("Dashboard running at http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
