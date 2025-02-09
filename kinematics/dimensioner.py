
import argparse
import math
import matplotlib.pyplot as plt

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

class Actuator:
  def __init__(self, start: Vector3d, end: Vector3d):
    self.start = start
    self.end = end
  
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

class ConvDelta:
  def __init__(self, base: float, angle: float, startexclusion: float, endexclusion: float, disttoactuator: float, height: float):
    circumscribed_radius = base / math.sqrt(3.0)
    inscribed_radius = circumscribed_radius / 2.0

    pyramid_height = math.tan(math.radians(angle)) * circumscribed_radius

    print("height={}\npyramid_height={}\ndiff={}".format(height, pyramid_height, height-pyramid_height))

    # Ideal virtual actuators
    self.ide_act_a = Actuator(Vector3d(-base/2.0, -inscribed_radius, height), Vector3d(0.0, 0.0, height-pyramid_height))
    self.ide_act_b = Actuator(Vector3d(base/2.0, -inscribed_radius, height), Vector3d(0.0, 0.0, height-pyramid_height))
    self.ide_act_c = Actuator(Vector3d(0.0, circumscribed_radius, height), Vector3d(0.0, 0.0, height-pyramid_height))

    print("lengths={}, {}, {}".format(self.ide_act_a.length(), self.ide_act_b.length(), self.ide_act_c.length()))


    down = Vector3d(0.0, 0.0, -1.0)

    side = self.ide_act_c.direction().cross(down)
    print("side={}, {}, {}".format(side.x, side.y, side.z))
    # # Offseted actuators by the carriage offset
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

  def plot(self):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    self.ide_act_a.plot(ax, 'r')
    self.ide_act_b.plot(ax, 'g')
    self.ide_act_c.plot(ax, 'b')

    self.act_a.plot(ax, 'r')
    self.act_b.plot(ax, 'g')
    self.act_c.plot(ax, 'b')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()
  

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

  args = parser.parse_args()

  model = ConvDelta(args.base, args.angle, args.startexclusion, args.endexclusion, args.disttoactuator, args.height)
  
  if args.configfile:
    with open(args.configfile, "w") as f:
      f.write("# base={}; angle={}; startexclusion={}; endexclusion={}; disttoactuator={}; height={};\n\n".format(args.base, args.angle, args.startexclusion, args.endexclusion, args.disttoactuator, args.height))
      model.write_configs(f)
  
  if args.plot:
    model.plot()


if __name__ == "__main__":
  main()

