from calibrate import *
from calibrate_procedure import *
import numpy as np

# BRIGHT LIGHT DETECTION
# click s to start and q to end
leftPoints, rightPoints = find_light(RIGHT_CAMERA, LEFT_CAMERA)

# find the 3D coords of the light
pts3D = np.array(stereoCams.triangulate(leftPoints, rightPoints)).T
np.savetxt("tracks/track2.csv", pts3D, delimiter=",", fmt="%f")
print(pts3D)

