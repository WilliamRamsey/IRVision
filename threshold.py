import cv2

cap = cv2.VideoCapture(1)

print("cap started")
if not cap.isOpened():
    print("capture failed to open")
    quit()

while True:
    ret, frame = cap.read()
    # print(frame.shape)

    if not ret:
        print("capture failed to initialize")
        quit()
    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    retval, threshold_mask = cv2.threshold(grayscale, 127, 225, cv2.THRESH_BINARY)
    cv2.imshow("Webcam", threshold_mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
