// This sketch parses a string from serial port in the format [x, y, fps] and reprints them along with current time (millis) as tab separated values

const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

int xOffset;
int yOffset;
float fps;

boolean newData = false;

//============

void setup() {
    Serial2.begin(115200); //for Pi
    Serial.begin(115200);  //for PC
}

//============

void loop() {
    recvWithStartEndMarkers();
    if (newData == true) {
        strcpy(tempChars, receivedChars);
            // this temporary copy is necessary to protect the original data
            //   because strtok() used in parseData() replaces the commas with \0
        parseData();
        showParsedData();
        newData = false;
    }
}

//============

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '[';
    char endMarker = ']';
    char rc;

    while (Serial2.available() > 0 && newData == false) {
        rc = Serial2.read();

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
    xOffset = atoi(strtokIndx);     // convert this part to an integer

    strtokIndx = strtok(NULL, ",");
    yOffset = atoi(strtokIndx);

    strtokIndx = strtok(NULL, ",");
    fps = atof(strtokIndx);

}

//============

void showParsedData() {
    Serial.print(xOffset);
    Serial.print("\t");
    Serial.print(yOffset);
    Serial.print("\t");
    Serial.print(fps);
    Serial.print("\t");
    Serial.println(millis());   
}
