#include <Wire.h>
#include "Arduino.h"
#include "FreeflyAPI.h"

// Define variables and constants
unsigned int counter = 0;
unsigned int timer = 0;
unsigned int aimingTimer = 0;
//MoVI variables
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
//Pins
const int laserPin = 3; //output pin for laser control
const int panPin = 4; //change these to whatever pins you end up using for RC Rx
const int tiltPin = 5;
const int tagPin = 6;
const int zoomPin = 7;
//PID variables
unsigned long currentTime = 0;
unsigned long currentTime2 = 0;
double integral = 0;
double integral2 = 0;
//x.fval and y.fval unions (might not need these)
union xAzimuth {
  byte b[4];
  float fval;
} x;

union yAzimuth {
  byte b[4];
  float fval;
} y;

void setup() {
  pinMode(laserPin, OUTPUT);
  pinMode(panPin, INPUT);
  pinMode(tiltPin, INPUT);
  pinMode(tagPin, INPUT);
  pinMode(zoomPin, INPUT);
  Serial.begin(115200);   // Pi connection
  Serial1.begin(111111);  // output to MoVI aux input
  FreeflyAPI.begin();
  Serial.println("ATMega Initialized");
}

}

void loop() {
  counter = millis();
  if(trackingTarget == FALSE) {
    tagVal = pulseIn(tagPin, HIGH); //check if user has engaged the tag button/switch
    if(tagVal = ???TRUE){ 
      trackingTarget = TRUE;
    }
    else { //skipping these should save me like 60ms in auto mode (could use interrupts instead though)
      panVal = pulseIn(panPin, HIGH);
      tiltVal = pulseIn(tiltPin, HIGH);
      zoomVal = pulseIn(zoomPin, HIGH);

      CONVERT PWM VAL TO PANCOMMANDVAL //FIX LATER
      CONVERT PWM VAL TO TILTCOMMANDVAL
      CONVERT PWM VAL TO ZOOMCOMMANDVAL
    }
  }
  if(trackingTarget == TRUE) {
    //READ X/Y AND TARGETVISIBLE VALS FROM PI SERIAL (USE UNIONS FOR X/Y FLOATS?)
    //x.fval = VAL FROM SERIAL;
    //y.fval = VAL FROM SERIAL;
    //targetVisible == VAL FROM SERIAL;
    if(targetVisible == TRUE) {
      trackingTarget = TRUE;
      //calculate X PID
      integral += .06 *x.fval*(100/1e6); //delta time isn't working so the average being 100 is used //UPDATE: This will have to be retuned.
      panCommandValue = -1*((0.00020992*x.fval) + integral);
      //calculate Y PID
      integral2 += .06*y.fval*(100/1e6); // Ki was initially .032 but adjusted to compensate for better firmware
      tiltCommandValue = (0.00020992*y.fval) + integral2;
      //fire laser if within target window
      if ((x.fval<targetWindowSize and x.fval>-targetWindowSize) and (y.fval<targetWindowSize and y.fval>-targetWindowSize)) { //negatives might not work
        digitalWrite(laserPin, HIGH);
      else
        digitalWrite(laserPin, LOW);
      }
    }
    else {
      trackingTarget = FALSE;
    }
  }
  if(counter % 10 == 0) {
    FreeflyAPI.control.pan.value = panCommandValue;
    FreeflyAPI.control.tilt.value = tiltCommandValue;
    FreeflyAPI.send();
  }
}
