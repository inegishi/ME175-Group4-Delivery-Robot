const int ENA = 10;  // P1
const int IN1 = 8;   // A1
const int IN2 = 9;   //B1

String inputString = "";
bool stringComplete = false;

void setup() {
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  // FORCE STOP at startup
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, 0);

  Serial.begin(9600);
}

void loop() {
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}

void processCommand(String cmd) {
  int commaIndex = cmd.indexOf(',');

  if (commaIndex == -1) return;

  String throttleStr = cmd.substring(0, commaIndex);
  String steerStr = cmd.substring(commaIndex + 1);

  float throttle = throttleStr.toFloat();  // -1.0 to 1.0

  // --- MOTOR CONTROL ---
  int speed = abs(throttle) * 255;  // convert to PWM

  if (throttle > 0.05) {
    // forward
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
  } else if (throttle < -0.05) {
    // backward
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
  } else {
    // stop
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    speed = 0;
  }

  analogWrite(ENA, speed);

  // --- STEERING (PRINT ONLY for now) ---
  // You’ll hook this to servo later
  Serial.print("Throttle: ");
  Serial.print(throttle);
  Serial.print(" | Steering: ");
  Serial.println(steerStr);
}