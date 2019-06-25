void setup() {
  Serial.begin(115200);  // Pi
}

void loop() {
  Serial.println("Testing 123");
  digitalWrite(13, HIGH);
  delay(600);
  digitalWrite(13, LOW);
  delay(600);
}
