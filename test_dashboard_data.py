import requests
import time

# Send test data to dashboard
test_data = {
    'current_activity': 'Sitting',
    'current_duration': 1845,  # 30 minutes 45 seconds
    'last_movement': 420,  # 7 minutes ago
    'daily_stats': {
        'total_sitting': 7200,  # 2 hours
        'total_standing': 3600,  # 1 hour
        'total_walking': 1800,  # 30 minutes
        'longest_sitting': 3600,
        'longest_standing': 1200,
        'warnings_issued': 3
    }
}

print("Sending test activity duration data to dashboard...")
try:
    response = requests.post('http://127.0.0.1:5000/api/activity_duration', json=test_data)
    print(f"Response: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Also check what the dashboard returns
    status_response = requests.get('http://127.0.0.1:5000/api/status')
    import json
    data = status_response.json()
    if 'activity_duration' in data:
        print("\nActivity duration data in dashboard:")
        print(json.dumps(data['activity_duration'], indent=2))
    else:
        print("\nNo activity_duration key found in dashboard data!")
        print("Available keys:", list(data.keys()))
except Exception as e:
    print(f"Error: {e}")
