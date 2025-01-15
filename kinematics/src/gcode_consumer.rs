
use gcode::{GCode, Mnemonic, Parser, Nop, buffers::DefaultBuffers};
use nalgebra_glm::*;

const step_length_mm: f64 = 1e-4;
const max_acceleration: f64 = 4.0;

struct GCodeState {
  is_absolute: bool,
  is_mm: bool,
  feedrate: f64,
}

struct Segment {
  target_velocity: f64,
  length: f64,
  positions: Vec<DVec3>,
  timestamps: f64,
}
struct GCodeConsumer {
  state: GCodeState,

}

struct TrapezoidProfile {
  target_vel: f64, 
  start_vel: f64,
  end_vel: f64,
  acceleration: f64,
  length: f64,

  t_accel: f64,
  t_cruising: f64,
  dist_accel: f64,
  dist_cruising: f64,
}
impl TrapezoidProfile {
  fn new(max_accel: f64, target_vel: f64, start_vel: f64, end_vel: f64, length: f64) -> Option<TrapezoidProfile> {
    let t_accel = (self.velocity - start_vel) / self.acceleration;
    let t_decel = (self.velocity - start_vel) / self.acceleration;
    if t_accel < 0.0 {
      panic!("Start velocity is greater than max");
    }
    if t_decel < 0.0 {
      panic!("End velocity is greater than max");
    }

    let dist_accel = start_vel * t_accel + 0.5 * t_accel.powi(2) * self.acceleration;
    let dist_decel = end_vel * t_decel + 0.5 * t_decel.powi(2) * self.acceleration;

    if dist_accel + dist_decel > length {
      // triangle moment
      let vel_diff = end_vel - start_vel;
      let a = max_accel;
      let b = 2 * start_vel;
      let c = end_vel * vel_diff / max_accel + vel_diff.powi(2) / (2*max_accel) - length;

      let term = b.powi(2) - 4 * a * c;
      if term < 0.0 {
        println!("Could not create triangular profile")
        return None;
      }
      let term_sq = term.sqrt();
      let t_accel = (-b + term_sq) / (2*a);
      let dist_accel = start_vel * t_accel + 0.5 * t_accel.powi(2) * self.acceleration;
      return Some(TrapezoidProfile{target_vel, start_vel, end_vel, acceleration:max_accel, t_accel, t_cruising: 0.0, dist_accel, dist_cruising: 0.0});
    }

    let dist_cruising = (length - dist_accel - dist_decel);
    let t_cruising = dist_cruising / target_vel;

    return Some(TrapezoidProfile { target_vel, start_vel, end_vel, acceleration:max_accel, length, t_accel, t_cruising, dist_accel, dist_cruising });
  }
  fn get_timestamp(self&, position: f64) -> f64 {
    if position > length + close_enough_distance {
      println!("get_timestamp out of range!");
      return 0.0;
    }
    if position < self.dist_accel {
      return TrapezoidProfile::solve_for_t(self.start_vel, self.acceleration, 0.0, position);
    } else if position < (self.dist_accel + self.dist_cruising) {
      return self.t_accel + (position - self.dist_accel) / self.target_velocity;
    } else {
      return TrapezoidProfile::solve_for_t(self.end_vel, self.acceleration, 0.0, self.length - position) + t_accel + t_cruising;
    }
  }
  fn solve_for_t(vel: f64, accel: f64, x0: f64, xf: f64) -> f64 {
    let a = 0.5*accel; 
    let b = vel;
    let c = x0 - xf;

    // solve quadratic formula
    let term = b.powi(2) - 4 * a * c;
    if term < 0.0 {
      println!("Error while solving for t");
      return 0.0;
    }
    let term_sq = term.sqrt();
    return (-b + term_sq) / (2*a);
  }
}

impl Segment {
  fn new_linear(from: DVec3, to: DVec3, target_velocity: f64) -> Segment {
    let profile = TrapezoidProfile { velocity: target_velocity, acceleration: max_acceleration };
    let length = (to - from).length();
    let mut positions = Vec::new();
    let mut timestamps = Vec::new();

    let n_steps = length / step_length_mm;
    let param_step_size = 1.0 / (n_steps-1);
    let mut lerp = 0.0;
    let mut cumulative_length = 0.0;
    for i in 0..n_steps {
      
      positions.push(from + (to - from) * lerp);
      
      lerp += param_step_size;
      cumulative_length += step_length_mm;

      timestamps.push(profile.get_timestamp(0.0, 0.0, cumulative_length, length));
    }
  }

  fn duration(&self) -> f64 {
    if timestamps.length() == 0 {
      return 0.0
    }
    return timestamps[timestamps.length()] - timestamps[0];
  }
}


pub fn consume_gcode(gcode: String) {
  let lines: Parser<Nop, DefaultBuffers> = Parser::new(&gcode, Nop);
  for line in lines {
      for code in line.gcodes() {
          match code.mnemonic() {
              Mnemonic::General => match code.major_number() {
                  0 | 1 => {
                      // self.parse_G0(code, &context);
                      println!("linearmove!");
                  }
                  2 | 3 => {
                      // self.parse_G2(code, &context);
                      println!("circularmove!");
                  }
                  // 90 => self.absolute = true,
                  // 91 => self.absolute = false,
                  _ => {}
              },
              _ => {}
          }
      }
    }
}