import cv2
# Take an (X, Y, Z) world position and project it on the image plane

# Logitech Brio
# Focal length 2.74mm
f = 2.74
# Pixel Pitch 1.12 um
pixelPitch = 3 * (1.12e-3)

Xc = float(eval(input("X camera (mm) -> ")))
Yc = float(eval(input("Y camera (mm) -> ")))
Zc = float(eval(input("Z camera (mm) -> ")))

Xi_mm = f * Xc / Zc
Yi_mm = f * Yc / Zc

Xi_px = Xi_mm / pixelPitch
Yi_px = Yi_mm / pixelPitch
print(Xi_px)
print(Yi_px)


cap = cv2.VideoCapture(1)

print("cap started")
if not cap.isOpened():
    print("capture failed to open")
    quit()


while True:
    ret, frame = cap.read()

    if not ret:
        print("capture failed to initialize")
        quit()

    frameHeight, frameWidth, numChannels = frame.shape
    print(f"W: {frameWidth}, H: {frameHeight}")
    # translate origin given by projection to center of the frame
    Xi = int(Xi_px + frameWidth // 2)
    Yi = int(Yi_px + frameHeight // 2)
    print(f"X: {Xi} Y: {Yi}")
    cv2.circle(frame, (Xi, Yi), 5, (0, 0, 225), thickness=-1)
    cv2.circle(frame, (frameWidth // 2, frameHeight // 2), 5, (0, 225, 0), thickness=-1)
    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
