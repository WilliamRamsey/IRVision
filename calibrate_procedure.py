from calibrate import *
from Camera import *

RIGHT_CAMERA = 0
LEFT_CAMERA = 2
PATTERN_SIZE = (3, 4)

camL = Camera(LEFT_CAMERA)
camR = Camera(RIGHT_CAMERA)

### CAMERA CALIBRATION
# camL.take_pics_timer(30, 10, "leftCamCal")
leftCamCalErr, leftCamMtx, leftCamDst = camL.calibrate(PATTERN_SIZE, "leftCamCal", 29)
print(f"Left calibration error: {leftCamCalErr}")

# camR.take_pics_timer(30, 6, "rightCamCal")
rightCamCalErr, rightCamMtx, rightCamDst = camR.calibrate(PATTERN_SIZE, "rightCamCal", 24)
print(f"Right calibration error: {rightCamCalErr}")


### STEREO CALIBRATION
stereoCams = Stereo(camL, camR)
# stereoCams.take_pics_timer(15, 10, "leftStereo", "rightStereo")
R, T = stereoCams.calibrate(PATTERN_SIZE, 1, "leftStereo", "rightStereo", 6)
