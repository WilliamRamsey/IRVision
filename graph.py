import numpy as np
import open3d as o3d
import time

points = np.loadtxt("tracks/track2.csv", delimiter=",") / 50
points[:, :1] += 0.5

vis = o3d.visualization.Visualizer() #ignore
vis.create_window()
view_control = vis.get_view_control()
view_control.set_constant_z_far(5000.0) # make far plane further
render_option = vis.get_render_option()
render_option.point_size = 5


pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector([[100, 100, 100]])
coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
    size=1, 
    origin=[0, 0, 0]
)


# Display
vis.add_geometry(pcd)
vis.add_geometry(coordinate_frame)
# o3d.visualization.draw_geometries([pcd, coordinate_frame]) # ignore
time.sleep(10)
start = time.time_ns()
i = 1
while i < len(points):

	if (time.time_ns() - start) / 1e9 > 0.2:
		pcd.points = o3d.utility.Vector3dVector(points[:i])
		vis.update_geometry(pcd)
		i += 1
		start = time.time_ns()

	# poll @ 30 fps
	if (time.time_ns() - start) / 1e9 > (1/30):
		vis.poll_events()
		vis.update_renderer()
