from calibrate import *

RIGHT_CAMERA = 1
LEFT_CAMERA = 2
PATTERN_SIZE = (3, 4)

# take_pics_timer(30, 10, "leftCamCal", LEFT_CAMERA)
leftCamCalErr, leftCamMtx, leftCamDst = calibrate_cam(PATTERN_SIZE, "leftCamCal", 29)
# print(f"Left calibration error: {leftCamCalErr}")
camIntsL = {"mtx": leftCamMtx, "dst": leftCamDst}
# take_pics_timer(30, 6, "rightCamCal", RIGHT_CAMERA)
rightCamCalErr, rightCamMtx, rightCamDst = calibrate_cam(PATTERN_SIZE, "rightCamCal", 24)
# print(f"Right calibration error: {rightCamCalErr}")
camIntsR = {"mtx": rightCamMtx, "dst": rightCamDst}


# take_stereo_pics_timer(10, 10, LEFT_CAMERA, RIGHT_CAMERA, "leftStereo", "rightStereo")
R, T = calibrate_stereo(PATTERN_SIZE, 1, "leftStereo", "rightStereo", camIntsL, camIntsR, 6)
