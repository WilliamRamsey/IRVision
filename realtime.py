import cv2
from ultralytics import YOLO
import time
import numpy as np
import matplotlib.pyplot as plt
from calibrate import *

RIGHT_CAMERA = 2
LEFT_CAMERA = 1
PATTERN_SIZE = (6, 7)


# MONO CALIBRATION FOR EACH CAMERA
# take_pics(20, "rightCamCal", RIGHT_CAMERA)
rightCamCalErr, rightCamMtx, rightCamDst = calibrate_cam(PATTERN_SIZE, "rightCamCal", 20)
print(f"rightCamCal Error: {rightCamCalErr}")
# take_pics(20, "leftCamCal", LEFT_CAMERA)
leftCamCalErr, leftCamMtx, leftCamDst = calibrate_cam(PATTERN_SIZE, "leftCamCal", 19)
print(f"leftCameraCal Error: {leftCamCalErr}")
camIntsR = {"mtx": rightCamMtx, "dst": rightCamDst}
camIntsL = {"mtx": leftCamMtx, "dst": leftCamDst}

# STEREO CALIBRATION FOR BOTH CAMERAS
# take_stereo_pics(10, LEFT_CAMERA, RIGHT_CAMERA, "leftStereo", "rightStereo")
R, T = calibrate_stereo(PATTERN_SIZE, 1, "leftStereo", "rightStereo", camIntsL, camIntsR, 6)

# MODEL INIT
model = YOLO("yolo11n-pose.pt")  

# CAMERA INIT
capR = cv2.VideoCapture(RIGHT_CAMERA, cv2.CAP_MSMF)
capR.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
capR.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
capR.set(cv2.CAP_PROP_FPS, 120) 
time.sleep(1)
capL = cv2.VideoCapture(LEFT_CAMERA, cv2.CAP_MSMF)
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
        break

    # Run pose estimation
    resultsR = model(frameR, verbose=False)
    resultsL = model(frameL, verbose=False)
    if resultsR[0].keypoints is not None and resultsL[0].keypoints is not None:

        pointsR = resultsR[0].keypoints.xy.cpu().numpy()
        confidenceR = resultsR[0].keypoints.conf.cpu().numpy()
        confidenceR = np.stack((confidenceR, confidenceR), 2)

        pointsL = resultsL[0].keypoints.xy.cpu().numpy()
        confidenceL = resultsL[0].keypoints.conf.cpu().numpy()
        confidenceL = np.stack((confidenceL, confidenceL), 2)

        print(f"confidence: {confidenceL.shape}")
        print(f"points: {pointsL.shape}")

        # Filter points based on confidecnce score
        mask = (confidenceR > 0.4) & (confidenceL > 0.4)
        print(mask)
        filteredPointsL = pointsL[mask]
        filteredPointsR = pointsR[mask]
        print(filteredPointsL)
        
        
        if len(filteredPointsL) != 0 and len(filteredPointsR) != 0:
            print("Plotting ")
            pts3D = np.array(triangulate(filteredPointsL, filteredPointsR, camIntsL, camIntsR, R, T)).T
            fig = plt.subplots(subplot_kw={"projection": "3d"})[0]
            ax = fig.gca()
            ax.scatter(pts3D[:, 0], pts3D[:, 1], pts3D[:, 2])

    annotated_frameL = resultsL[0].plot()
    annotated_frameR = resultsR[0].plot()


    plt.figure("Left")
    plt.imshow(cv2.cvtColor(annotated_frameL, cv2.COLOR_BGR2RGB))
    plt.figure("Right")
    plt.imshow(cv2.cvtColor(annotated_frameR, cv2.COLOR_BGR2RGB))
    plt.show()
    time.sleep(0.01)
    plt.close("all")

    # Press q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capR.release()
capL.release()
cv2.destroyAllWindows()