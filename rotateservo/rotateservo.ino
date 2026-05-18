#include <Servo.h>

Servo myServo;

void setup() {
  myServo.attach(9);
  myServo.write(65);   // start at center
  delay(1000);         // pause so it settles
}

void loop() {
  // Move from 0 → 130
  for (int angle = 0; angle <= 130; angle++) {
    myServo.write(angle);
    delay(15); // speed (lower = faster)
  }

  delay(500);

  // Move from 130 → 0
  for (int angle = 130; angle >= 0; angle--) {
    myServo.write(angle);
    delay(15);
  }

  
  delay(500);
}