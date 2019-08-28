byte number = 0;

void setup(){
Serial.begin(115200);
Serial2.begin(115200);
}

void loop(){
  while (Serial.available()) {
    number = Serial.read();
    Serial.print("character recieved on serial1: ");
    Serial2.print("character received on serial1: ");
    Serial.println(number, DEC);
    Serial2.println(number, DEC);
    }
  while (Serial2.available()) {
    number = Serial2.read();
    Serial2.println(number, DEC);
    Serial.println(number, DEC);
    }
}

int BitShiftCombine(unsigned char x_high, unsigned char x_low) {
  int combined = x_high; //send x_high over to leftmost 8 bits
  combined = combined<<8; //shift x_high over to leftmost 8 bits
  combined |=x_low; //logical OR keeps x_high intact in combined and fills
                    //rightmost 8 bits
  return combined;
}
