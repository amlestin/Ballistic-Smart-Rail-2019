/*-----------------------------------------------------------------------------
                Copyright 2018 Space Coast Unmanned, LLC.
                Developed for SOFWERX

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


*/
/*---------------Freefly example code portion license taken from Freefly API Arduino example code:--------------------------

  Copyright 2017 Freefly Systems

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
  -------------------------------------------------------------------
*/
#include <Wire.h>
#include "Arduino.h"
#include "FreeflyAPI.h"

// Define variables and constants
uint8_t UART_Tx_Buf[64];
uint8_t UART_Rx_char;
//uint32_t print_cntr = 0;
unsigned int lastCommand = 0; //1,2,3,4 = Up, Down, Left, Right. Keeps track for DPAD toggle
volatile uint8_t message[41]; //scope sends 22 byte messages for manual control, 40 for correction
volatile uint8_t newMessage[41]; //scope sends 22 byte messages for manual control, 40 for correction
volatile int index = 0; //index of message array
int msgType = 2; //this byte tells you if its manual gimbal control or auto correction
int panOrTilt = 8; // this byte tells you if it's a pan or tilt command
int directionByte = 10; // this byte tells you if it's an up or down tilt
int isNewMessage = 0; //flag for knowing if message is new or old
int isProcessing = 0; //flag to let interrupt know if it interrupted loop
unsigned int counter = 0;
unsigned int timer = 0;
unsigned int aimingTimer = 0;
unsigned int dpadDebounce = 0;
unsigned int triggerCounter = 0;
float minPanValue = -500; //From the scope
float maxPanValue = 500;//From the scope
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
bool trigger = 0;
int laserTime = 0;
unsigned int triggerPin = 2; //input pin for trigger fire from scope
unsigned int laserPin = 3; //output pin for laser control

unsigned long lastTime = 0;
unsigned long currentTime = 0;
unsigned long currentTime2 = 0;
double integral = 0;
double integral2 = 0;

union xAzimuth {
  byte b[4];
  float fval;
} x;

union yAzimuth {
  byte b[4];
  float fval;
} y;
//--------------------------------------------------------------------FUNCTION PROTOTYPES------------------------------------------------------------------------

//--------------------------------------------------------------------SETUP------------------------------------------------------------------------
void setup() {
  Wire.begin(72);                // join i2c bus with address #72
  Wire.onReceive(receiveEvent); // interrupt event for receiving i2c bytes
  pinMode(triggerPin, INPUT);
  pinMode(laserPin, OUTPUT);
  Serial.begin(115200);           // start serial for output
  Serial1.begin(111111);  // Aux serial port for control
  FreeflyAPI.begin();
  Serial.println("ATMega Initialized");
}

//--------------------------------------------------------------------LOOP------------------------------------------------------------------------
void loop() {
  counter = millis();
  timer = counter;
  digitalWrite(laserPin, LOW);
 // if (digitalRead(triggerPin) == LOW) {
 //   if (trigger == 0) {
 //     Serial.println("Trigger fired");
  //  }
   // trigger = 1;
   // triggerCounter = 0;
   // digitalWrite(laserPin, HIGH);
 // }
 // else {
   // digitalWrite(laserPin, LOW);
   // trigger = 0;
  //}

  if (counter % 10 == 0) { //slow down the output to gimbal
    counter = 0;

    if (isNewMessage == 1) {
      //      Serial.println("message array: ");
      for (int i = 0; i < sizeof(message); i++) {
        message[i] = newMessage[i];
        //        Serial.print("Index is: ");
        //        Serial.print(i);
        //        Serial.print(" Byte is: ");
        //        Serial.println( (uint8_t)message[i]);
      }

      switch (message[msgType]) {
        case 1: //This case is scope auto correction
          //Serial.println("-------------Correction message received-------------");
          lastCommand = 5;
          x.b[0] = message[8];
          x.b[1] = message[10];
          x.b[2] = message[12];
          x.b[3] = message[14];
          y.b[0] = message[16];
          y.b[1] = message[18];
          y.b[2] = message[20];
          y.b[3] = message[22];

          //          Serial.print("Byte 1: ");
          //          Serial.println(x.b[0], DEC );
          //
          //          Serial.print("Byte 2: ");
          //          Serial.println(x.b[1], DEC );
          //
          //          Serial.print("Byte 3: ");
          //          Serial.println(x.b[2], DEC );
          //
          //          Serial.print("Byte 4: ");
          //          Serial.println(x.b[3], DEC );
          //
          //
          //          Serial.print("X float: ");
          //          Serial.println(x.fval, 10);
          //
          //          Serial.print("Byte 1: ");
          //          Serial.println(y.b[0], DEC );
          //
          //          Serial.print("Byte 2: ");
          //          Serial.println(y.b[1], DEC );
          //
          //          Serial.print("Byte 3: ");
          //          Serial.println(y.b[2], DEC );
          //
          //          Serial.print("Byte 4: ");
          //          Serial.println(y.b[3], DEC );
          //
          //          Serial.print("Y float: ");
          //          Serial.println(y.fval, 10);
          //          Serial.println();


          // if (x.fval > 1000) {
          //  panCommandValue = -0.25;   //changed the sign value, this should avoid the jerk in the negative x-axis
         //}
         // else if (x.fval < -1000) {
         //   panCommandValue = +0.25;   //changed the sign value
         // }
         // else {
            currentTime = millis()/1e6;
            integral += .06 *x.fval*(100/1e6); //delta time isn't working so the average being 100 is used
            //integral = integral + ki*x.fval*100
            panCommandValue = -1*((0.00020992*x.fval) + integral); // Kp was intially 0.00012
            //Serial.println(currentTime-lastTime);
         // }
         // Serial.print("x.fval: ");
          FreeflyAPI.control.pan.value = panCommandValue;
//----------------------------------------------------------------
        //  if (y.fval > 1000) {
        //    tiltCommandValue = 0.25;
        //  }
        //  else if (y.fval < -1000) {
        //    tiltCommandValue = -0.25;
        //  }
        //  else {
           // currentTime2 = millis()/1e6;
            integral2 += .06*y.fval*(100/1e6); // Ki was initially .032 but adjusted to compensate for better firmware
            tiltCommandValue = (0.00020992*y.fval) + integral2;
            
        //  }
        
          Serial.println(y.fval);
          FreeflyAPI.control.pan.value = panCommandValue;
          FreeflyAPI.control.tilt.value = tiltCommandValue;
         if ((x.fval<250 and x.fval>-250) and (y.fval<250 and y.fval>-250)) {
            digitalWrite(laserPin, HIGH);
    }
    else {
          digitalWrite(laserPin, LOW);
    }
         // }
          //Serial.print("Integral: ");
          //Serial.println(integral);
          //Serial.print("Pan value is: ");
          //Serial.println(panCommandValue);
         //Serial.print("Tilt value is: ");
          //Serial.println(tiltCommandValue);
          //Serial.print("Delta_Time: ");
          //Serial.println(currentTime-lastTime);
          aimingTimer = millis();
          lastTime = currentTime;
          break;

        case 3: //This case is for manual DPAD commands

        //clear the auto correction variables for next target
          lastTime = 0;
          currentTime = 0;
          currentTime2 = 0;
          integral = 0;
          integral2 = 0;
          
          if ((timer - dpadDebounce) > 20) { //add some delay to prevent double taps from the xbox controller
            dpadDebounce = millis();
            if (message[panOrTilt] == 131) {
              Serial.println("DPAD Pan command received");
              FreeflyAPI.control.tilt.type = RATE;
              FreeflyAPI.control.tilt.value = 0.0;
              if (message[directionByte] == 1) {

                if (lastCommand == 0) { // setting this == 3 should set the movement to only move when pressing down
                  lastCommand = 3;
                  FreeflyAPI.control.pan.type = RATE;
                  FreeflyAPI.control.pan.value = manualPanRate;
                  
                }

                else {
                  lastCommand = 0;
                  FreeflyAPI.control.pan.type = RATE;    //set to zero and see if that allows for movement only when button is pressed 
                  FreeflyAPI.control.pan.value = 0.0;

                }
              }
              else if (message[directionByte] == 255) {

                if (lastCommand == 0) {
                  lastCommand = 4; 
                  FreeflyAPI.control.pan.type = RATE;
                  FreeflyAPI.control.pan.value = -manualPanRate;
                  
                }

                else {
                  lastCommand = 0;
                  FreeflyAPI.control.pan.type = RATE;
                  FreeflyAPI.control.pan.value = 0.0;

                }
              }
            }
            else if (message[panOrTilt] == 132) {
              Serial.println("DPAD Tilt command received");
              FreeflyAPI.control.pan.type = RATE;
              FreeflyAPI.control.pan.value = 0.0;

              if (message[directionByte] == 255) {

                if (lastCommand == 0) {
                  lastCommand = 1;
                  FreeflyAPI.control.tilt.type = RATE;
                  FreeflyAPI.control.tilt.value = manualTiltRate;

                }

                else {        //This causes the pan motion to stop when hitting left and right on dpad
                  lastCommand = 0;
                  FreeflyAPI.control.tilt.type = RATE;
                  FreeflyAPI.control.tilt.value = 0.0;

                }
              }
              else if (message[directionByte] == 1) {

                if (lastCommand == 0) {
                  lastCommand = 2;
                  FreeflyAPI.control.tilt.type = RATE;
                  FreeflyAPI.control.tilt.value = -manualTiltRate;

                }

                else {    //this  causes the pan motion to stop when hitting left and right on dpad
                  lastCommand = 0;
                  FreeflyAPI.control.tilt.type = RATE;
                  FreeflyAPI.control.tilt.value = 0.0;

                }
              }
            }
          }
          break;

        default:
          //Serial.println("Didn't match");
          //          Serial.print("Message type is flagged as: ");
          //          Serial.println(message[msgType]);
          //          for (int i = 0; i < sizeof(message); i++) {
          //            Serial.print("Index is: ");
          //            Serial.print(i);
          //            Serial.print(" Byte is: ");
          //            Serial.println( (uint8_t)message[i]);
          //          }
          break;
      }

      isNewMessage = 0;
    }

#ifndef UNO_BOARD
    // Get Received Messages
    int i = 64;
    uint8_t c;
    while (Serial1.available() > 0)
    {
      c = Serial1.read();
      QX_StreamRxCharSM(QX_COMMS_PORT_UART, c);
    }
#endif
    
    //    // Send control packet
    FreeflyAPI.send();

    // Empty the send buffer
    for (int i = 0; i < sizeof(UART_Tx_Buf); i++) {
      if (BufRemove(1, &UART_Tx_Buf[i]) == 0) break;
#ifdef UNO_BOARD
      Serial.write(UART_Tx_Buf[i]);
#else
      Serial1.write(UART_Tx_Buf[i]);
#endif
    }
  }
  if (((timer - aimingTimer) > 250) && lastCommand == 5) {
    FreeflyAPI.control.tilt.value = 0.0;
    FreeflyAPI.control.pan.value = 0.0; //Stop the motor from spinning for pan
    FreeflyAPI.send();
    lastCommand = 0;
    //Serial.println("Auto correction stopped");
  }
  isProcessing = 0;
}
//--------------------------------------------------------------------FUNCTIONS------------------------------------------------------------------------

//receiveEvent runs once per byte received
void receiveEvent(int howMany) {
  //Serial.println("----------New byte starting----------");
  //if (isProcessing == 0) {
  //Tell the loop that a new message has arrived if it has finished processing the previous one
  //if (isNewMessage == 0) {
  isNewMessage = 1;
  //    Serial.println("New message starting");
  //}

  //Start reading the message
  while (Wire.available()) {
    char c = Wire.read();
    if (c == 2) {
      //Serial.println("New message starting");
      index = 0;
    }
    newMessage[index] = c;

    //Serial.print("index value: ");
    //Serial.print(index);
    //Serial.print(" byte is: ");
    //Serial.println((uint8_t)newMessage[index]);
    if (index > 41) {
      index = 0;
    }
    else {
      index++;
    }
  }
}

//----------------------------------------------------------------------------
