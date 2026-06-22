from calibrate import *
import numpy as np

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
take_stereo_pics(10, LEFT_CAMERA, RIGHT_CAMERA, "leftStereo", "rightStereo")
R, T = calibrate_stereo(PATTERN_SIZE, 1, "leftStereo", "rightStereo", camIntsL, camIntsR, 6)

# BRIGHT LIGHT DETECTION
leftPoints, rightPoints = find_light(RIGHT_CAMERA, LEFT_CAMERA)

# find the 3D coords of the light
pts3D = np.array(triangulate(leftPoints, rightPoints, camIntsL, camIntsR, R, T)).T
np.savetxt("tracks/track.csv", pts3D, delimiter=",", fmt="%f")
print(pts3D)

# graph from saved file

