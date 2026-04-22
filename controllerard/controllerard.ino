#include <Servo.h>

Servo myServo;

void setup() {
  Serial.begin(115200);
  myServo.attach(9);

  myServo.write(65);   // Start centered
  //0: (1,0) - 130 (-1,0)
}

void loop() {
  if (Serial.available()) {
    float joystick = Serial.parseFloat();

    // Clamp to valid range
    joystick = constrain(joystick, -1.0, 1.0);

    // Deadzone to reduce jitter
    if (abs(joystick) < 0.1) {
      joystick = 0;
    }

    // Map -1~1 to 0~180 with center at 65
    int angle = 65 + joystick * 65;

    Serial.print("joy: ");
    Serial.print(joystick);
    Serial.print(" angle: ");
    Serial.println(angle);
    myServo.write(angle);
  }
}