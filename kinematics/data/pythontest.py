
import open3d as o3d
from numpy import genfromtxt

my_data = genfromtxt('positions.csv', delimiter=',')

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(my_data)

o3d.visualization.draw_geometries([pcd])
alpha = 0.1
print(f"alpha={alpha:.3f}")
mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, alpha)
print("comp normals")
mesh.compute_vertex_normals()
o3d.visualization.draw_geometries([mesh], mesh_show_back_face=True)
print("done")
