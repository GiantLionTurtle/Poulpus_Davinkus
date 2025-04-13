
import argparse
import math
import matplotlib.pyplot as plt
from matplotlib import cm
import mathutil
import random as rng
import numpy as np

from skimage import measure
from scipy.spatial import cKDTree
import open3d as o3d
import numpy as np


class Vector3d:
  def __init__(self, x: float, y: float, z: float):
    self.x = x
    self.y = y
    self.z = z
  
  def normalize(self):
    len = self.length()
    return Vector3d(self.x / len, self.y / len, self.z / len)

  def length(self) -> float:
    return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

  def minus(self, other):
    return Vector3d(self.x-other.x, self.y-other.y, self.z-other.z)

  def plus(self, other):
    return Vector3d(self.x+other.x, self.y+other.y, self.z+other.z)

  def times(self, t: float):
    return Vector3d(self.x*t, self.y*t, self.z*t)

  def invert(self):
    return Vector3d(-self.x, -self.y, -self.z)

  def cross(self, other):
    return Vector3d(self.y * other.z - self.z * other.y, self.z * other.x - self.x * other.z, self.x * other.y - self.y * other.x)

  def to_list(self):
    return [self.x, self.y, self.z]

class Actuator:
  def __init__(self, start: Vector3d, end: Vector3d):
    self.start = start
    self.end = end
  
  def at_lerp(self, lerp):
    return self.direction().times(lerp).plus(self.start)
  def at_dist(self, dist):
    return self.at_lerp(dist / self.length) # is this right within the context of clipper?

  def direction(self) -> Vector3d:
    return self.end.minus(self.start)
  
  def direction_normal(self) -> Vector3d:
    return self.direction().normalize()

  def length(self) -> float:
    return self.direction().length()

  def offset(self, by: Vector3d):
    return Actuator(self.start.plus(by), self.end.plus(by))

  def trim(self, start_trim: float, end_trim: float):
    dir_norm = self.direction_normal()
    return Actuator(self.start.plus(dir_norm.times(start_trim)), self.end.minus(dir_norm.times(end_trim)))

  def to_str(self) -> str:
    return "min_x:{}\nmin_y:{}\nmin_z:{}\nmax_x:{}\nmax_y:{}\nmax_z:{}\nposition_endstop:{}\nposition_max:{}\n".\
            format(self.start.x, self.start.y, self.start.z, self.end.x, self.end.y, self.end.z, 0, self.length())

  def plot(self, ax, param):
    ax.plot([self.start.x, self.end.x], [self.start.y, self.end.y], [self.start.z, self.end.z], param)

def data_for_cylinder_along_z(center_x,center_y,radius,height_z):
    z = np.linspace(0, height_z, 50)
    theta = np.linspace(0, 2*np.pi, 50)
    theta_grid, z_grid=np.meshgrid(theta, z)
    x_grid = radius*np.cos(theta_grid) + center_x
    y_grid = radius*np.sin(theta_grid) + center_y
    return x_grid,y_grid,z_grid

class ConvDelta:
  def __init__(self, base: float, angle: float, startexclusion: float, endexclusion: float, disttoactuator: float, height: float, armlength: float):
    
    self.armlength = armlength

    circumscribed_radius = base / math.sqrt(3.0)
    inscribed_radius = circumscribed_radius / 2.0

    pyramid_height = math.tan(math.radians(angle)) * circumscribed_radius

    # Ideal virtual actuators
    self.ide_act_a = Actuator(Vector3d(-base/2.0, -inscribed_radius, height), Vector3d(0.0, 0.0, height-pyramid_height))
    self.ide_act_b = Actuator(Vector3d(base/2.0, -inscribed_radius, height), Vector3d(0.0, 0.0, height-pyramid_height))
    self.ide_act_c = Actuator(Vector3d(0.0, circumscribed_radius, height), Vector3d(0.0, 0.0, height-pyramid_height))

    # Offseted actuators by the carriage offset
    down = Vector3d(0.0, 0.0, -1.0)
    act_a = self.ide_act_a.offset(self.ide_act_a.direction().cross(self.ide_act_a.direction().cross(down)).normalize().times(-disttoactuator))
    act_b = self.ide_act_b.offset(self.ide_act_b.direction().cross(self.ide_act_b.direction().cross(down)).normalize().times(-disttoactuator))
    act_c = self.ide_act_c.offset(self.ide_act_c.direction().cross(self.ide_act_c.direction().cross(down)).normalize().times(-disttoactuator))

    # # Trim the endstops as the carriages cannot go to either end of the pyramid
    self.act_a = act_a.trim(startexclusion, endexclusion)
    self.act_b = act_b.trim(startexclusion, endexclusion)
    self.act_c = act_c.trim(startexclusion, endexclusion)

    # self.act_a = act_a
    # self.act_b = act_b
    # self.act_c = act_c

  def write_configs(self, file):
    file.write("[stepper_a]\n{}\n\n[stepper_b]\n{}\n\n[stepper_c]\n{}\n".format(self.act_a.to_str(), self.act_b.to_str(), self.act_c.to_str()))

  def test_forward(self, n_points):

    xs = []
    ys = []
    zs = []
    for i in range(0, n_points):
      rands = [rng.random(), rng.random(), rng.random()]
      pos = mathutil.trilateration([self.act_a.at_lerp(rands[0]).to_list(), self.act_b.at_lerp(rands[1]).to_list(), self.act_c.at_lerp(rands[2]).to_list()], [self.armlength**2, self.armlength**2, self.armlength**2])
      xs.append(pos[0])
      ys.append(pos[1])
      zs.append(pos[2])
    
    return (xs, ys, zs)

  def plot(self):
    actuators_positions = [self.act_a.start.to_list(), self.act_a.end.to_list(), self.ide_act_a.start.to_list(), self.ide_act_a.end.to_list(),
                           self.act_b.start.to_list(), self.act_b.end.to_list(), self.ide_act_b.start.to_list(), self.ide_act_b.end.to_list(),
                           self.act_c.start.to_list(), self.act_c.end.to_list(), self.ide_act_c.start.to_list(), self.ide_act_c.end.to_list()]
    lines = [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [10, 11]]
    colors = [[1, 0, 0] for i in range(len(lines))]
    actuators_lines = o3d.geometry.LineSet()
    actuators_lines.points = o3d.utility.Vector3dVector(actuators_positions)
    actuators_lines.lines = o3d.utility.Vector2iVector(lines)
    actuators_lines.colors = o3d.utility.Vector3dVector(colors)

    # Work cylinder which we wish to reach
    work_cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=175, height=150, resolution=20, split=4).translate([0.0, 0.0, 150.0/2.0])


    # Compute many points within the work enveloppe
    enveloppe = self.test_forward(1500000)
    enveloppe_points = np.column_stack(enveloppe)


    # Marching cubes on enveloppe points to create a mesh for further visualization/analysis
    voxel_size=5
    iso_level_percentile=30

    mins = np.min(enveloppe_points, axis=0) - 25
    maxs = np.max(enveloppe_points, axis=0) + 25

    x = np.arange(mins[0], maxs[0], voxel_size)
    y = np.arange(mins[1], maxs[1], voxel_size)
    z = np.arange(mins[2], maxs[2], voxel_size)
    x, y, z = np.meshgrid(x, y, z, indexing='ij')

    tree = cKDTree(enveloppe_points)

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


    # Show geometries
    viewer = o3d.visualization.Visualizer()
    viewer.create_window()

    viewer.add_geometry(mesh)
    viewer.add_geometry(actuators_lines)
    viewer.add_geometry(work_cylinder)

    opt = viewer.get_render_option()
    opt.show_coordinate_frame = True
    opt.background_color = np.asarray([0.5, 0.5, 0.5])
    viewer.run()
    viewer.destroy_window()

    o3d.io.write_triangle_mesh('mesh.stl', mesh)



def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-b", "--base", type=float)
  parser.add_argument("-a", "--angle", type=float)
  parser.add_argument("-s", "--startexclusion", type=float)
  parser.add_argument("-e", "--endexclusion", type=float)
  parser.add_argument("-d", "--disttoactuator", type=float)
  parser.add_argument("-l", "--height", type=float)
  parser.add_argument("-c", "--configfile", type=str)
  parser.add_argument("-w", "--workspacefile", type=str)
  parser.add_argument("-p", "--plot", action="store_true")
  parser.add_argument("-y", "--armlength", type=float)
  

  args = parser.parse_args()

  model = ConvDelta(args.base, args.angle, args.startexclusion, args.endexclusion, args.disttoactuator, args.height, args.armlength)
  
  if args.configfile:
    with open(args.configfile, "w") as f:
      f.write("# base={}; angle={}; startexclusion={}; endexclusion={}; disttoactuator={}; height={}; arm={}\n\n".format(args.base, args.angle, args.startexclusion, args.endexclusion, args.disttoactuator, args.height, args.armlength))
      model.write_configs(f)
  
  if args.plot:
    model.plot()


if __name__ == "__main__":
  main()

