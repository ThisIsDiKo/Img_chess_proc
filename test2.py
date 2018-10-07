from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot

figure = pyplot.figure()
axes = mplot3d.Axes3D(figure)

m = mesh.Mesh.from_file('Body1.stl')
print(m.y)
axes.add_collection3d(mplot3d.art3d.Poly3DCollection(m.vectors))

scale = m.points.flatten(-1)
axes.auto_scale_xyz(scale, scale, scale)

#pyplot.show()
