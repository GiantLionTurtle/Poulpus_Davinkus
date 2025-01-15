

use nalgebra_glm::*;
use rand::prelude::*;

const close_enough_distance: f64 = 1e-4;
const close_enough_parametric: f64 = 1e-5;

struct LinearActuator {
  pt0: DVec3, // Start position 
  pt1: DVec3, // End position
  min: f64,  // min position in parametric space [0, 1]
  max: f64,  // max position in parametric space [0, 1]

  max_vel: f64,
  max_accel: f64,
}

impl LinearActuator {
  fn new(pt0: DVec3, pt1: DVec3, max_vel: f64, max_accel: f64, exclusion_start: f64, exclusion_end: f64) -> LinearActuator {
    let length = (pt1-pt0).magnitude();
    let mut min = exclusion_start.abs() / length;
    let mut max = 1.0 - exclusion_end.abs() / length;

    if min >= 1.0 {
      println!("LinearActuator::new error, expected min < 1, got min={}", min);
      min = 0.0;
    }
    if max <= 0.0 {
      println!("LinearActuator::new error, expected max > 0.0, got max={}", max);
      max = 1.0;
    }
    if min > max {
      println!("LinearActuator::new error, expected min < max, got min={} and max={}", min, max);
      min = 0.0;
      max = 1.0;
    }
    return LinearActuator {pt0, pt1, max_vel: max_vel.abs(), max_accel: max_accel.abs(), min, max};
  }
  fn at(&self, lerp: f64) -> DVec3 {
    return self.at_virtual(self.clamp_parametric(lerp));
  }
  fn at_virtual(&self, lerp: f64) -> DVec3 {
    return self.direction() * lerp + self.pt0;
  }
  fn clamp_parametric(&self, lerp: f64) -> f64 {
    return lerp.clamp(self.min, self.max);
  }
  fn direction(&self) -> DVec3 {
    return self.pt1-self.pt0;
  }
  /// Return a position on the actuators from which an arm of
  /// length arm_length could touch a position
  fn solve_position(&self, position: DVec3, arm_length: f64) -> Option<f64> {
    let dir = self.direction();
    let closest_lerp = self.closest_point(position);
    let carriage_pos = self.at_virtual(closest_lerp);
    
    let arm_length2 = arm_length.powi(2);
    let dist_to_act2 = length2(&(carriage_pos-position));
    if dist_to_act2 == arm_length2 {
      return self.in_range(closest_lerp);
    }
    if dist_to_act2 > arm_length2 {
      return None;
    }
    
    // Not directly perpendicular, not too far
    // solve for second cathede of a right triangle

    // offset in parametric space
    let offset_along_actuator = (arm_length2 - dist_to_act2).sqrt() / length(&dir);
    return match self.in_range(closest_lerp + offset_along_actuator) {
      Some(x) => Some(x),
      None => self.in_range(closest_lerp - offset_along_actuator)
    }
  }
  fn closest_point(&self, position: DVec3) -> f64 {
    let dir = self.direction();
    return dir.dot(&(position-self.pt0)) / length2(&dir);
  }
  fn in_range(&self, pos: f64) -> Option<f64> {
    if pos >= self.min - close_enough_parametric && pos <= self.max + close_enough_parametric {
      return Some(pos)
    }
    else {
      return None;
    }
  }

}


pub struct DeltaModel {
  actuators: [LinearActuator; 3],
  arm_length: f64, // Length of the linkages from the linear actuators to the platform
  eot_offset: DVec3, // eot offset in the DeltaModel's transform
}

impl DeltaModel {
  /// Creates a delta model thats a straight equilateral triangular pyramid
  /// The base sits on the xy plane, centered at the origin and the head points in the direction of the z axis
  /// at (0, 0, height)  
  /// One of the sides of the base is parallel to the x axis and the other 2 converge on the y axis
  /// @height The height of the pyramid
  /// @side One base side length
  /// @arm_length length of linkage from linear actuator to platform
  /// @eot_offset offset in the model's coordinate system of the eot from the platform
  /// @actuator_exclusion_start the physical limit of the actuators when going toward the start (in mm)
  /// @actuator_exclusion_start the physical limit of the actuators when going toward the end (in mm)
  fn new_convergent(height: f64, side: f64, arm_length: f64, eot_offset: DVec3, acuator_exclusion_start: f64, actuator_exclusion_end: f64) -> DeltaModel {
    let circumscribed_radius = side / (3 as f64).sqrt();
    let inscribed_radius = circumscribed_radius / 2.0;
    
    let head = DVec3::new(0.0, 0.0, height);
    let base_0 = DVec3::new(-side/2.0, -inscribed_radius, 0.0);
    let base_1 = DVec3::new(side/2.0, -inscribed_radius, 0.0);
    let base_2 = DVec3::new(0.0, circumscribed_radius, 0.0);
    // let arm_length = distance(&head, &base_0);
    
    return DeltaModel {
      actuators:[
        LinearActuator::new(base_0, head, 0.0, 0.0, acuator_exclusion_start, actuator_exclusion_end),
        LinearActuator::new(base_1, head, 0.0, 0.0, acuator_exclusion_start, actuator_exclusion_end),
        LinearActuator::new(base_2, head, 0.0, 0.0, acuator_exclusion_start, actuator_exclusion_end)
      ],
      arm_length,
      eot_offset
    };
  }

  /// From a motor state, get an effector position
  fn forward_kinematics(&self, motors_positions: [f64;3]) -> Option<DVec3> {
    // https://stackoverflow.com/questions/1406375/finding-intersection-points-between-3-spheres

    // let p0 = self.actuators[0].at(motor_a);
    // let p1 = self.actuators[1].at(motor_b);
    // let p2 = self.actuators[2].at(motor_c);
    let actpos = self.actuators_positions(motors_positions);

    // println!("p0: {}", p0);
    // println!("p1: {}", p1);
    // println!("p2: {}", p2);
    
    let temp1 = actpos[1]-actpos[0];
    let e_x = temp1.normalize();
    let temp2 = actpos[2]-actpos[0];
    // let i = dot(temp1, temp2);
    let i = dot(&e_x, &temp2);
    let temp3 = temp2 - i * e_x;
    let e_y = temp3.normalize();
    let e_z = cross(&e_x, &e_y);
    let d = temp1.norm();
    let j = dot(&e_y, &temp2);
    let x = (d.powi(2)) / (2.0*d);
    let y = (i.powi(2) - 2.0*i*x + j.powi(2)) / (2.0*j);
    
    let temp4 = self.arm_length.powi(2) - x.powi(2) - y.powi(2);  
    if temp4 < 0.0 {
      return None;
    }
    // println!("dump={}, {}, {}, {}, {}, {}", x, e_x, y, e_y, temp4, e_z);
    let z = temp4.sqrt();
    
    let plus = actpos[0] + x * e_x + y * e_y + z * e_z;
    let minus = actpos[0] + x * e_x + y * e_y - z * e_z;
    
    println!("plus: {}", plus);
    println!("minus: {}", minus);
    
    if plus.z < 0.0 {
      return Some(minus);
    }
    return Some(plus);
  }
  fn inverse_kinematics(&self, position: DVec3) -> Option<[f64;3]> {
    let l0 = self.actuators[0].solve_position(position, self.arm_length)?;
    let l1 = self.actuators[1].solve_position(position, self.arm_length)?;
    let l2 = self.actuators[2].solve_position(position, self.arm_length)?;

    return Some([l0, l1, l2]);
  }

  // Returns the positions of the actuators in the 3d space of the machine
  // given their position in their 1d space [0, 1]
  fn actuators_positions(&self, motors_positions:[f64;3]) -> [DVec3; 3] {
    return [self.actuators[0].at(motors_positions[0]), 
            self.actuators[1].at(motors_positions[1]), 
            self.actuators[2].at(motors_positions[2])];
  }
}

// pub struct Delta {
//   model: DeltaModel, // Kinematic model of the delta
//   motors_positions: [f64; 3], // Positions of the motors in parametric space [0, 1]
  
//   effector_kind: i32, // Which effector is currently on the platform
// }



////////// Tests ///////////////


#[cfg(test)]
mod linear_actuator_tests {
  use super::*;

  #[test]
  fn at() {
    let lin_act = LinearActuator::new(DVec3::new(0.0, 0.0, 0.0), DVec3::new(100.0, 0.0, 0.0), 10.0, 10.0);

    approx::assert_abs_diff_eq!(lin_act.at(0.5), DVec3::new(50.0, 0.0, 0.0));

    // Should respect exclusion zone
    approx::assert_abs_diff_eq!(lin_act.at(1.0), DVec3::new(90.0, 0.0, 0.0)); 
    approx::assert_abs_diff_eq!(lin_act.at(1.0), lin_act.at(0.95));
    approx::assert_abs_diff_eq!(lin_act.at(0.0), DVec3::new(10.0, 0.0, 0.0));

    // Should handle out of bounds gracefully
    approx::assert_abs_diff_eq!(lin_act.at(1.0), lin_act.at(1.4)); 
    approx::assert_abs_diff_eq!(lin_act.at(0.0), lin_act.at(-10.0));
  }
  #[test]
  fn direction() {
    let lin_act = LinearActuator::new(DVec3::new(0.0, 0.0, 0.0), DVec3::new(20.0, 20.0, 20.0), 10.0, 10.0);
    approx::assert_abs_diff_eq!(lin_act.direction().normalize(), DVec3::new(1.0, 1.0, 1.0).normalize()); 
  }
  #[test]
  fn closest_point() {
    let lin_act = LinearActuator::new(DVec3::new(-100.0, 0.0, 0.0), DVec3::new(100.0, 0.0, 0.0), 10.0, 10.0);
  
    approx::assert_abs_diff_eq!(lin_act.closest_point(DVec3::new(0.0, -10.0, 0.0)), 0.5);
  }
}

#[cfg(test)]
mod model_tests {
  use super::*;

  #[test]
  fn forward_kinematics() {
    let model = DeltaModel::new_convergent(300.0, 350.0, 400.0, DVec3::new(0.0, 0.0, 0.0), 10.0, 35.0);

    let pos_home = model.forward_kinematics([0.0, 0.0, 0.0]).unwrap();
    approx::assert_abs_diff_eq!(pos_home.x, 0.0, epsilon = close_enough_distance);
    approx::assert_abs_diff_eq!(pos_home.y, 0.0, epsilon = close_enough_distance);
    assert!(pos_home.z >= 0.0);

    for _ in 0..1000 {
      let motors_positions:[f64;3] = gen_rand_motors_positions(&model);
      let eot = model.forward_kinematics(motors_positions).unwrap();
      let act_positions = model.actuators_positions(motors_positions);

      println!("motors_positions=[{}, {}, {}]\n eotpos={},\nact_positions=[{}, {}, {}]", motors_positions[0], motors_positions[1], motors_positions[2], eot, act_positions[0], act_positions[1], act_positions[2]);
    
      for i in 0..3 {
        approx::assert_abs_diff_eq!((eot-act_positions[i]).magnitude(), model.arm_length, epsilon = close_enough_distance);
      }
    }
  }
  #[test]
  fn inverse_kinematics() {

  }

  // Test feed the results of a kinematics in the other and expect the initial result
  #[test]
  fn mix_kinematics() {
    let model = DeltaModel::new_convergent(300.0, 350.0, 400.0, DVec3::new(0.0, 0.0, 0.0), 10.0, 35.0);

    println!("Test both kinematics in chain");
    
    for _ in 0..1000 {
      let motors_positions:[f64;3] = gen_rand_motors_positions(&model);
      let eot = model.forward_kinematics(motors_positions).unwrap();
      let act_positions = model.actuators_positions(motors_positions);

      println!("motors_positions=[{}, {}, {}]\n eotpos={},\nact_positions=[{}, {}, {}]", motors_positions[0], motors_positions[1], motors_positions[2], eot, act_positions[0], act_positions[1], act_positions[2]);
    
      for i in 0..3 {
        approx::assert_abs_diff_eq!((eot-act_positions[i]).magnitude(), model.arm_length, epsilon = close_enough_distance);
      }
      
      let inverse_motors = model.inverse_kinematics(eot).unwrap();

      for i in 0..3 {
        approx::assert_abs_diff_eq!(motors_positions[i], inverse_motors[i], epsilon = close_enough_parametric);
      }
    }
  }

  fn gen_rand_motors_positions(model: &DeltaModel) -> [f64;3] {
    let mut rng = thread_rng();
    return [model.actuators[0].clamp_parametric(rng.gen()), 
            model.actuators[1].clamp_parametric(rng.gen()), 
            model.actuators[2].clamp_parametric(rng.gen())];
  }
}