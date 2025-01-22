use model::DeltaModel;
use nalgebra_glm::*;
use std::fs::File;
use std::io::prelude::*;

mod model;
mod gcode_consumer;

fn main() {
  let model = DeltaModel::new_convergent(200.0, 450.0, 330.0, DVec3::new(0.0, 0.0, 0.0), 100.0, 50.0);

  println!("actuatorslength={}", model.actuators[0].length(false));
  let work_points = model.approximate_work_volume(10000);
  let mut file = File::create("data/positions.csv").unwrap();

  let mut points_str = String::from("");
  for point in work_points {
    points_str.push_str(format!("{}, {}, {}\n", point.x, point.y, point.z).as_str());
  }
  file.write_all(points_str.as_bytes()).unwrap();

  // let instr: String = "G0 50.0 45.0 44.0\n".to_string();
  // gcode_consumer::consume_gcode(instr)
}
