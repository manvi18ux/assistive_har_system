"""
Test script for Activity Duration Tracking feature
Tests the new health warning system for prolonged inactivity
"""

import time
from gesture_holistic import ActivityTracker, AlertManager
import threading

def test_activity_tracking():
    """Test the activity tracking and health warnings"""
    
    print("="*50)
    print("Testing Activity Duration Tracking")
    print("="*50)
    
    # Initialize components
    alert_manager = AlertManager()
    activity_tracker = ActivityTracker()
    
    # Override thresholds for faster testing (in seconds)
    activity_tracker.thresholds = {
        'sitting_warning': 5,      # 5 seconds for testing
        'sitting_critical': 10,    # 10 seconds for testing
        'standing_warning': 5,     # 5 seconds for testing
        'standing_critical': 10,   # 10 seconds for testing
        'inactivity_warning': 3,   # 3 seconds for testing
        'movement_reminder': 6     # 6 seconds for testing
    }
    
    print("\nThresholds set for quick testing:")
    print("- Sitting warning: 5 seconds")
    print("- Sitting critical: 10 seconds")
    print("- Movement reminder: 6 seconds")
    
    print("\n" + "-"*30)
    print("Test 1: Sitting Duration Tracking")
    print("-"*30)
    
    # Simulate sitting
    print("Starting sitting activity...")
    activity_tracker.update_activity('Sitting', alert_manager)
    
    # Wait and check duration
    for i in range(12):
        time.sleep(1)
        duration = activity_tracker.get_current_duration()
        print(f"Sitting for {duration:.1f} seconds", end='\r')
        
        # Update to trigger warnings
        activity_tracker.update_activity('Sitting', alert_manager)
    
    print("\n\n" + "-"*30)
    print("Test 2: Activity Change Tracking")
    print("-"*30)
    
    # Change to standing
    print("Changing to standing...")
    activity_tracker.update_activity('Standing', alert_manager)
    time.sleep(2)
    
    # Change to walking
    print("Changing to walking...")
    activity_tracker.update_activity('Walking', alert_manager)
    time.sleep(2)
    
    # Back to sitting
    print("Back to sitting...")
    activity_tracker.update_activity('Sitting', alert_manager)
    time.sleep(2)
    
    print("\n" + "-"*30)
    print("Test 3: Activity Summary")
    print("-"*30)
    
    summary = activity_tracker.get_activity_summary()
    print(f"Current Activity: {summary['current_activity']}")
    print(f"Current Duration: {summary['current_duration']:.1f} seconds")
    print(f"Total Sitting: {summary['daily_stats']['total_sitting']:.1f} seconds")
    print(f"Total Standing: {summary['daily_stats']['total_standing']:.1f} seconds")
    print(f"Total Walking: {summary['daily_stats']['total_walking']:.1f} seconds")
    print(f"Longest Sitting: {summary['daily_stats']['longest_sitting']:.1f} seconds")
    print(f"Health Warnings Issued: {summary['daily_stats']['warnings_issued']}")
    
    print("\n" + "-"*30)
    print("Test 4: Movement Reminder")
    print("-"*30)
    
    # Simulate no movement for a while
    print("Simulating inactivity (no walking)...")
    activity_tracker.update_activity('Sitting', alert_manager)
    
    for i in range(8):
        time.sleep(1)
        time_since = time.time() - activity_tracker.last_movement_time
        print(f"Time since last movement: {time_since:.1f} seconds", end='\r')
        activity_tracker.update_activity('Sitting', alert_manager)
    
    print("\n\n" + "="*50)
    print("Activity Tracking Tests Complete!")
    print("="*50)
    
    # Check alert history
    if alert_manager.alert_history:
        print(f"\nAlerts triggered during test:")
        for alert in alert_manager.alert_history:
            print(f"- {alert['type']}: {alert['message']}")
    else:
        print("\nNo alerts triggered (check threshold values)")
    
    # Cleanup
    alert_manager.stop()
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_activity_tracking()
