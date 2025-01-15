mod model;
mod gcode_consumer;

fn main() {
    println!("Hello, world!");
    let instr: String = "G0 50.0 45.0 44.0\n".to_string();
    gcode_consumer::consume_gcode(instr)
}
