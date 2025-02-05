#include <Arduino.h>

// Define pin connections
#define X_STEP_PIN 2
#define X_DIR_PIN 5
#define X_ENABLE_PIN 8

void setup() {
  // Set pin modes
  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(X_ENABLE_PIN, OUTPUT);

  // Enable the stepper driver
  digitalWrite(X_ENABLE_PIN, LOW);
}

void loop() {
  // Set direction
  digitalWrite(X_DIR_PIN, HIGH);

  // Move stepper motor
  for (int i = 0; i < 200; i++) {
    digitalWrite(X_STEP_PIN, HIGH);
    delayMicroseconds(1000);
    digitalWrite(X_STEP_PIN, LOW);
    delayMicroseconds(1000);
  }

  // Pause before changing direction
  delay(1000);

  // Change direction
  digitalWrite(X_DIR_PIN, LOW);

  // Move stepper motor in opposite direction
  for (int i = 0; i < 200; i++) {
    digitalWrite(X_STEP_PIN, HIGH);
    delayMicroseconds(1000);
    digitalWrite(X_STEP_PIN, LOW);
    delayMicroseconds(1000);
  }

  // Pause before next loop
  delay(1000);
}