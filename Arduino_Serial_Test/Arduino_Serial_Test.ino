void setup() {
Serial.begin(115200); //PC serial monitor
Serial2.begin(115200); //start connection to Pi's GPIO serial port
}

void loop() {
if (Serial.available() > 0) { //read from PC serial monitor
int incoming = Serial.read();
Serial.print("character recieved: "); //output to PC serial monitor...
Serial2.print("character recieved: "); //then output to Pi
Serial.println(incoming, DEC);
Serial2.println(incoming, DEC);
}
}
