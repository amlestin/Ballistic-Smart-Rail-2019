#include "Arduino.h"
#include "FreeflyAPI.h"
#include "PWM.hpp"

// Define pins
PWM lockPin(2);
PWM firePin(3); 
PWM yawPin(18); 
PWM pitchPin(19); 
PWM zoomPin(20); 
PWM modePin(21);
const int laserPin = 4; //output pin for laser control

//Serial vars
uint8_t UART_Tx_Buf[64];
uint8_t UART_Rx_char;
const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];  // temporary array for use when parsing
int trackStatus;
int lastTrackStatus;
float xOffset = 0.0;
float yOffset = 0.0;
boolean newData = false;

//MoVI vars
float minPanRate = -0.075;//Max left pan rate
float maxPanRate = 0.075;//Max right pan rate
float minTiltValue = -500; //From the scope
float maxTiltValue = 500;//From the scope
float minTiltRate = -0.075;//Max down tilt rate
float maxTiltRate = 0.075;//Max up tilt rate
float panCommandValue;
float tiltCommandValue;
float manualTiltRate = 0.03;
float manualPanRate = 0.03;

//PID vars
unsigned int counter = 0;
unsigned int timer = 0;
unsigned int aimingTimer = 0;
unsigned long currentTime = 0;
unsigned long currentTime2 = 0;
double integral = 0;
double integral2 = 0;

//Other vars
bool br;
const int targetTimeout = 1000;
const float sensitivity = 0.70; //command vals are multiplied by this for padding (0.75 = 75% "power")
float targetWindow = 0.1;

void setup() {
  pinMode(laserPin, OUTPUT); //imma firin mah laaaazoooor!!
  Serial3.begin(115200);   // Pi connection
  Serial2.begin(111111);  // output to MoVI aux input
  Serial.begin(115200);
  FreeflyAPI.begin();
  Serial.println("ATMega Initialized");

  lockPin.begin(true);
  firePin.begin(true); 
  yawPin.begin(true); 
  pitchPin.begin(true); 
  zoomPin.begin(true); 
  modePin.begin(true); 
}

void loop() {
  counter = millis(); //start counter for slowing down MoVI commands

  recvWithStartEndMarkers();
  if(newData == true) {
    strcpy(tempChars, receivedChars);  // this temporary copy is necessary to protect the original data
                                     // because strtok() used in parseData() replaces the commas with \0
    parseData();
    newData = false;
  }
//  Serial.print("X:");
//  Serial.print(xOffset);
//  Serial.print("\tY:");
//  Serial.print(yOffset);
//  Serial.print("\tTrackStatus:");
//  Serial.println(trackStatus);
  
  if(lockPin.getValue() >= 2000) { //if lock switch is toggled on: auto mode
      if(trackStatus == 0 && lastTrackStatus == 0) { //wasn't recently tracking
        Serial3.print("Start tracking"); //Tell Pi to start tracking whatever is at the center of the screen (or at least display a tracking marker if I'm still just using a color tracker)
        trackStatus = 1;
      }
      else if(trackStatus == 0 && lastTrackStatus == 1) { //was recently tracking (temporarily lost target)
        for(int j=0; j>=targetTimeout || br; j++) { //keep checking the trackStatus until the target timeout period has expired or the break var (br) is TRUE
          recvWithStartEndMarkers();
          if(newData == true) {
            strcpy(tempChars, receivedChars);  // this temporary copy is necessary to protect the original data
                                             // because strtok() used in parseData() replaces the commas with \0
            parseData();
            newData = false;
          }
          if(trackStatus == 1) {
            br = true;
          }
        }
        if(br == false) { //br will only be false if the targetTimeout was reached without the trackingStatus changing
          while(lockPin.getValue() >= 2000) {
            if(counter % 500 == 0) { //only tells user (through Pi) every .5 secs even though it checks constantly
              Serial3.print("Disengage lock switch");
            }
          }
          Serial3.print("Lock switch disengaged");
        }
    }
    else if(trackStatus == 1) { //auto mode

      //Yaw (pan)
      //currentTime = millis()/1e6; //this wasn't working in the original PID loop
      //integral += .06 *xOffset*(100/1e6); //the average being 100 is used for time so you'll need to change/fix this
      panCommandValue = xOffset*sensitivity; //simple proportional control
      Serial.print("panCommVal:");
      Serial.println(panCommandValue);
      FreeflyAPI.control.pan.value = panCommandValue; //this sets it but doesn't send it
//      Serial.print("Mode:Auto PanCommVal: ");
//      Serial.print(panCommandValue);
//      Serial.print("\t");

      //Pitch (tilt)
      //currentTime2 = millis()/1e6;
      //integral2 += .06*yOffset*(100/1e6);
      tiltCommandValue = yOffset*sensitivity; //simple proportional control (320x240 res)
      FreeflyAPI.control.tilt.value = tiltCommandValue;
//      Serial.print("TiltCommVal: ");
//      Serial.println(tiltCommandValue);
    }
  }
  
  else if(modePin.getValue() <= 980) { //relative manual mode
    FreeflyAPI.control.pan.type = RATE;
    FreeflyAPI.control.tilt.type = RATE;
    panCommandValue = ((yawPin.getValue())-1488.0)/520; //turn PWM value (972 to 1996) into MoVI comm val (-1 to 1). Btw, 520 is the PWM's distance from midpoint (1488)
//    Serial.print("Mode:Man/rel PanCommVal: ");
//    Serial.print(panCommandValue);
//    Serial.print("\t");

    tiltCommandValue = ((pitchPin.getValue())-1484.0)/520.0;
//    Serial.print("pitchPin Val: ");
//    Serial.print(pitchPin.getValue());
//    Serial.print("TiltCommVal: ");
//    Serial.println(tiltCommandValue);
  }

  else if(modePin.getValue() >= 1470 && modePin.getValue() <= 1490) { //absolute manual mode
    FreeflyAPI.control.pan.type = ABSOLUTE;
    FreeflyAPI.control.tilt.type = ABSOLUTE;
    panCommandValue = ((yawPin.getValue())-1488.0)/1040.0; //dividing by 1040 so it equates to half of 180 degrees
//    Serial.print("Mode:Man/abs PanCommVal: ");
//    Serial.print(panCommandValue);
//    Serial.print("\t");

    tiltCommandValue = ((pitchPin.getValue())-1484.0)/1040.0;
//    Serial.print("pitchPin Val: ");
//    Serial.print(pitchPin.getValue());
//    Serial.print("\t TiltCommVal: ");
//    Serial.println(tiltCommandValue);

    //absolute mode resting filter
    if(tiltCommandValue <= 0.05 && tiltCommandValue >= -0.05) {
      tiltCommandValue = 0;
    }
    if(panCommandValue <= 0.05 && panCommandValue >= -0.05) {
      panCommandValue = 0;
    }
  }

  if(counter % 30 == 0) {
    //max/min limiter ---------------
    if(panCommandValue > 1.0) {
      panCommandValue = 1.0;
    }
    if(panCommandValue < -1.0) {
      panCommandValue = -1.0;
    }
    if(tiltCommandValue > 1.0) {
      tiltCommandValue = 1.0;
    }
    if(tiltCommandValue < -1.0) {
      tiltCommandValue = -1.0;
    }
    //--------------------------------
    FreeflyAPI.control.pan.value = panCommandValue;
    //Serial.print("panCommVal:");
    //Serial.print(panCommandValue);
    FreeflyAPI.control.tilt.value = tiltCommandValue;
    //Serial.print("\ttiltCommVal:");
    //Serial.println(tiltCommandValue);
//    Serial.print("pan: ");
//    Serial.print(panCommandValue);
//    Serial.print("\t tilt: ");
//    Serial.println(tiltCommandValue);
    FreeflyAPI.send();
    
  #ifndef UNO_BOARD
  // Get Received Messages
  int i = 64;
  uint8_t c;
  while (Serial2.available() > 0)
  {
    c = Serial2.read();
    QX_StreamRxCharSM(QX_COMMS_PORT_UART, c);
  }
  #endif
  // Empty the send buffer
  for (int i = 0; i < sizeof(UART_Tx_Buf); i++) {
    if (BufRemove(1, &UART_Tx_Buf[i]) == 0) break;
  #ifdef UNO_BOARD
        Serial.write(UART_Tx_Buf[i]);
  #else
        Serial2.write(UART_Tx_Buf[i]);
  #endif
      }
  }
  if(abs(xOffset) <= targetWindow && abs(yOffset) <= targetWindow && firePin.getValue() >= 1900) {
    digitalWrite(laserPin, HIGH);
  }
  else digitalWrite(laserPin, LOW);
}

//======================== Other Functions ====================================

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '[';
    char endMarker = ']';
    char rc;

    while (Serial3.available() > 0 && newData == false) {
        rc = Serial3.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

//============

void parseData() {      // split the data into its parts

    char * strtokIndx; // this is used by strtok() as an index
 
    strtokIndx = strtok(tempChars, ","); // this continues where the previous call left off
    xOffset = atof(strtokIndx);     // convert this part to a float

    strtokIndx = strtok(NULL, ",");
    yOffset = atof(strtokIndx);

    strtokIndx = strtok(NULL, ",");
    trackStatus = atoi(strtokIndx); //i.e. is the target visible and tracking?

}
