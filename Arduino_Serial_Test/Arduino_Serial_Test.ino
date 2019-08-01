int incoming = 0;
String content = "";
char character;

void setup() {
  Serial.begin(115200); //PC serial monitor
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
  while (Serial.available() > 0) { //read from PC serial monitor
      character = Serial.read();
      content.concat(character);
    }

    if (content != "") {
      Serial.print(content);
      content = "";
    }
  }
