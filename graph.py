import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

fig = plt.subplots(subplot_kw={"projection": "3d"})[0]
ax = fig.gca()
def set_axes_equal(ax):
	"""Set equal scale on all 3 axes of a matplotlib 3D axis.

	This tries to use `set_box_aspect` (Matplotlib >=3.3). If unavailable,
	it adjusts the axis limits so the ranges are equal.
	"""
	try:
		ax.set_box_aspect((1, 1, 1))
		return
	except Exception:
		# Fall back to manual limits adjustment
		pass

	x_limits = ax.get_xlim3d()
	y_limits = ax.get_ylim3d()
	z_limits = ax.get_zlim3d()

	x_range = abs(x_limits[1] - x_limits[0])
	y_range = abs(y_limits[1] - y_limits[0])
	z_range = abs(z_limits[1] - z_limits[0])

	max_range = max([x_range, y_range, z_range])

	x_middle = np.mean(x_limits)
	y_middle = np.mean(y_limits)
	z_middle = np.mean(z_limits)

	ax.set_xlim3d(x_middle - max_range / 2, x_middle + max_range / 2)
	ax.set_ylim3d(y_middle - max_range / 2, y_middle + max_range / 2)
	ax.set_zlim3d(z_middle - max_range / 2, z_middle + max_range / 2)

	
data = pd.read_csv("tracks/track.csv", header=None)

ax.scatter(data.iloc[:, 0], data.iloc[:, 1], data.iloc[:, 2])
set_axes_equal(ax)
plt.show()