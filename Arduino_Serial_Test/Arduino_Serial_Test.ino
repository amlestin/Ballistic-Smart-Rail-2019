int incoming[3];
String content;
char testing[15];
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
        for(int i=0; i<15; i++) {
          testing[i] = Serial.read();
        }
        testing[15] = '\0';  //append null
        Serial.print(testing); 
        
        
//        if(character == '\n') {
//          Serial.print("Received: ");
//          Serial.print(content);
//          content = "";
//        }
  }

  
  
  //Serial.print("Serial received: ");
  //Serial.println(incoming[]);
}
