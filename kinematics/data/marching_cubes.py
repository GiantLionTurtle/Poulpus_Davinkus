from skimage import measure
from scipy.spatial import cKDTree
import open3d as o3d
import numpy as np

points = np.genfromtxt('positions.csv', delimiter=',')


voxel_size=5
iso_level_percentile=40

mins = np.min(points, axis=0) - 25
maxs = np.max(points, axis=0) + 25

print(f"mins:{mins}, maxes:{maxs}")


x = np.arange(mins[0], maxs[0], voxel_size)
y = np.arange(mins[1], maxs[1], voxel_size)
z = np.arange(mins[2], maxs[2], voxel_size)
x, y, z = np.meshgrid(x, y, z, indexing='ij')

tree = cKDTree(points)

grid_points = np.vstack([x.ravel(), y.ravel(), z.ravel()]).T
distances, _ = tree.query(grid_points)
scalar_field = distances.reshape(x.shape)

iso_level = np.percentile(distances, iso_level_percentile)

verts, faces, _, _ = measure.marching_cubes(scalar_field, level=iso_level)

verts = verts * voxel_size + mins

mesh = o3d.geometry.TriangleMesh()
mesh.vertices = o3d.utility.Vector3dVector(verts)
mesh.triangles = o3d.utility.Vector3iVector(faces)

mesh.compute_vertex_normals()

o3d.visualization.draw_geometries([mesh], mesh_show_back_face=True)
o3d.io.write_triangle_mesh('mesh.stl', mesh)