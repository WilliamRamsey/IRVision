import numpy as np
import open3d as o3d
from ultralytics import YOLO

from calibrate_procedure import *

# GUI SETUP
cv2.namedWindow("Left Detections", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
cv2.namedWindow("Right Detections", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)

vis = o3d.visualization.Visualizer() #ignore
vis.create_window()
view_control = vis.get_view_control()
view_control.set_constant_z_far(5000.0) # make far plane further
render_option = vis.get_render_option()
render_option.point_size = 10

# GUI point cloud setup
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector([[100, 100, 100], [100, 100, 100]])
frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=2)
vis.add_geometry(pcd)
vis.add_geometry(frame)

# YOLO MODEL INIT
model = YOLO("yolo11n-pose.pt")

print("Waiting for detection...")
while True:

    # grab frames
    frameL, frameR = stereoCams.read()

    # detect points
    resultsR = model(frameR, verbose=False)
    resultsL = model(frameL, verbose=False)
    keypointsL = resultsL[0].keypoints
    keypointsR = resultsR[0].keypoints

    confidenceMask = np.zeros((1, 17, 1))
    
    if (keypointsL is not None and keypointsR is not None) and (len(keypointsR) and len(keypointsL)):
        pointsR = resultsR[0].keypoints[0].xy.cpu().numpy()
        pointsL = resultsL[0].keypoints[0].xy.cpu().numpy()
        confidenceR = resultsR[0].keypoints[0].conf.cpu().numpy()
        confidenceL = resultsL[0].keypoints[0].conf.cpu().numpy()
        confidenceMask = (confidenceL > 0.4) & (confidenceR > 0.4)
        confidenceMask = np.stack((confidenceMask, confidenceMask), 2)
        filteredPointsL = pointsL[confidenceMask]
        filteredPointsR = pointsR[confidenceMask]

    # visualize camera views
    annotated_frameL = resultsL[0].plot()
    annotated_frameR = resultsR[0].plot()
    cv2.imshow("Left Detections", annotated_frameL)
    cv2.imshow("Right Detections", annotated_frameR)

    # triangulate and visualize
    if any(confidenceMask.reshape(-1)):
        pts3D = stereoCams.triangulate(filteredPointsL, filteredPointsR).T / 20
        pts3D[:, 1] = - pts3D[:, 1]
        print(pts3D)


        # visualize 3D points
        pcd.points = o3d.utility.Vector3dVector(pts3D) # Push points
        vis.update_geometry(pcd)
        
    vis.poll_events()
    vis.update_renderer()

