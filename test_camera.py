import cv2

print("Testing camera access...")

# Try to open camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Cannot open camera!")
    print("Trying camera index 1...")
    cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("ERROR: No camera found at index 0 or 1")
        print("\nPossible solutions:")
        print("1. Check if camera is connected")
        print("2. Check if another app is using the camera")
        print("3. Check Windows camera permissions")
    else:
        print("Camera found at index 1")
else:
    print("Camera opened successfully at index 0!")
    
    # Test reading a frame
    ret, frame = cap.read()
    if ret:
        print(f"Successfully read frame: {frame.shape}")
        
        # Show test window
        cv2.imshow("Camera Test", frame)
        print("\nCamera test window opened!")
        print("Press any key to close...")
        cv2.waitKey(0)
    else:
        print("ERROR: Cannot read from camera")

cap.release()
cv2.destroyAllWindows()
print("Test complete")
