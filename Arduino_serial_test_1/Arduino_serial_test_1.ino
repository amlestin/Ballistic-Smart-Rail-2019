char content[32];
char byteRead;
int testVal;

void setup() {
  Serial.begin(115200);
}

void loop() {
  int i = 0;
  //int availableBytes = Serial.available();
    while(Serial.available() > 0) {
      //content[i] = Serial.read(); //put latest byte into char array
      //i++;
      int trackStatus = Serial.parseInt();
      int zoom = Serial.parseInt();
      int x1 = Serial.parseInt();

      if(Serial.read() == '\n') {
        Serial.print("trackStatus: ");
        Serial.println(trackStatus);
        Serial.print("zoom: ");
        Serial.println(zoom);
        Serial.print("x1: ");
        Serial.println(x1);
      }
    }
    content[i+1] = '\0'; //append null
    if(i != 0) {
      //Serial.print(content);
      //Serial.println("");
      testVal = atoi(content);
      Serial.print(testVal+2);
      content[0] = '\0';      
    }
  }
