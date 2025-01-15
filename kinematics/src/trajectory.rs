
// use nalgebra_glm::*;

// mod model;

// struct Waypoint {
//   position: DVec3,
//   time: f64,
//   is_stop: bool,
// }
// struct ActuatorsWaypoint {
//   position: [f64;3],
//   time: f64,
//   is_stop: bool,
// }

// struct Segment1D {
//   start: f64,
//   end: f64,
//   target_velocity: f64,
// }

// impl Segment1D {
//   fn new(start: f64, end: f64, time: f64) -> Segment1D {
//     return Segment1D{start, end, target_velocity:(end-start)/time};
//   }
// }

// fn actuators_segments(start: Waypoint, end: Waypoint) -> [Segment1D;3] {
//   let start_act = [0.0, 0.0, 0.0]; // inverse kinematics
//   let end_act = [1.0, 1.0, 1.0];
//   let duration = end.time - start.time;

//   return [Segment1D::new(start_act[0], end_act[0], duration), 
//           Segment1D::new(start_act[1], end_act[1], duration),
//           Segment1D::new(start_act[2], end_act[2], duration)];
// }

// struct GCodeState {
//   is_mm: bool,
//   feedrate: f64
// }

// struct Delta {
//   actuators_positions: [f64;3],
//   eot_position: DVec3,

//   // stamp_kind: i32,
//   time: f64,
//   is_stopped: bool
  
// }

// impl Delta {
//   fn new_from_eot(eot_pos: DVec3, time: f64, stopped: bool, model: Model) -> Option<Delta> {
//     return Some(Delta{ actuators_positions:model.inverse_kinematics(eot_pos)?, eot_position: eot_pos, time, is_stopped:stopped});
//   }

//   fn get_waypoint(&self) -> Waypoint {
//     return Waypoint {position: self.eot_position, time: self.time, is_stop: self.is_stopped};
//   }
//   fn get_actuators_waypoint(&self) -> Waypoint {
//     return ActuatorsWaypoint {position: self.actuators_positions, time: self.time, is_stop: self.is_stopped};
//   }
// }


// struct Planner {
//   model: Model,
//   trajectory: [Delta; 1024], // Curently planed waypoints
//   exec_cursor: usize,
//   plan_cursor: usize,
//   planed_stops: u32,
// }

// impl Planner {

//   fn push_waypoint(self&, waypoint: Waypoint) {
    

//     if waypoint.is_stop {
//       self.planed_stops++;
//     }
//   }

//   fn push_waypoints(self&, waypoints: Vec<Waypoint>) {
//     for waypoint in waypoints {
//       self.push_waypoint(waypoint);
//     }
//   }
//   // Pushes a stop waypoint
//   fn push_stop(&self) {
//     let mut last_waypoint = trajectory[plan_cursor];
//     last_waypoint.is_stop = true;
//     push_waypoint(last_waypoint);
//   }

//   fn get_next(&self) -> ActuatorsWaypoint {
//     self.exec_cursor = increment_cursor(self.exec_cursor);
//     if planed_stops == 0 && how_long_ahead() < 1.0 { // Less than a second ahead and no stop is scheduled
//       println!("No planed stop and lookahead is too short, injecting stop...");
//       self.push_stop();
//     }

//     let next = trajectory[self.exec_cursor];
//     if next.is_stop {
//       if self.planed_stops == 0 {
//         panic!("No planed stop yet next is stop");
//       }
//       self.planed_stops -= 1;
//     }
    
//     return next;
//   }
//   // Returns how long ahead the trajectory is to the execution
//   fn how_long_ahead(&self) -> f64 {
//     return self.trajectory[plan_cursor].time - self.trajectory[exec_cursor].time;
//   }
//   fn increment_cursor(cursor: usize) -> usize {
//     cursor++;
//     while cursor >= 1024 {
//       cursor -= 1024;
//     }
//     return cursor;
//   }
// }

// // gcode => break into waypoints spaced by epsilon mm (speed, acceleration implied by timestamp)
// // converted in positions on all actuators
// // 
