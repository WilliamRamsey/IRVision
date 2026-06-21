import cv2
import time


capR = cv2.VideoCapture(2, cv2.CAP_MSMF)
capR.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
capR.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
capR.set(cv2.CAP_PROP_FPS, 120) 
time.sleep(1)
capL = cv2.VideoCapture(1, cv2.CAP_MSMF)
capL.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
capL.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
capL.set(cv2.CAP_PROP_FPS, 120)


if not capL.isOpened() or not capR.isOpened():
    print("capture failed to open")
    quit()

while True:
    retR, frameR = capR.read()
    retL, frameL = capL.read()


    if not retR or not retL:
        print("capture failed to initialize")
        quit()

    cv2.imshow("Right Camera", frameR)
    cv2.imshow("Left Camera", frameL)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capR.release()
capL.release()
cv2.destroyAllWindows()
