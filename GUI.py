import open3d as o3d
import numpy as np

points = np.loadtxt('tracks/track.csv', delimiter=',')
print(points.shape)
# Create point cloud object
pcd = o3d.geometry.PointCloud()

# Attach numpy array
pcd.points = o3d.utility.Vector3dVector(points)

frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
    size=1.0
)

o3d.visualization.draw_geometries(
    [pcd, frame]
)
