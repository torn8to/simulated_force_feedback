#include <BasicLinkedList.h>


const boolean THUMB_ENABLE = false;
const boolean FORCE_PROCESSING = false; // defaults to casted  raw reading

const unsigned short FSR_PIN_INDEX = 1;
const unsigned short FSR_PIN_MIDDLE = 2;
const unsigned short FSR_PIN_RING = 3;
const unsigned short FSR_PIN_PINKY = 4;
const unsigned short FSR_PIN_THUMB = 5;
const unsigned short INDEX_ENCA = 7;
const unsigned short INDEX_ENCB = 8;
const unsigned short MIDDLE_ENCA = 9;
const unsigned short MIDDLE_ENCB = 10;
const unsigned short RING_ENCA = 11;
const unsigned short RING_ENCB = 12;
const unsigned short PINKY_ENCA = 13;
const unsigned short PINKY_ENCB = 14;
const unsigned short THUMB_ENCA = 15;
const unsigned short THUMB_ENCB = 16;

const unsigned short INDEX_SERVO_PIN = 8;
const unsigned short MIDDLE_SERVO_PIN = 8;
const unsigned short RING_SERVO_PIN = 8;
const unsigned short PINKY_SERVO_PIN = 8;
const unsigned short THUMB_SERVO_PIN = 8;
// Positional Information (INDEX, MIDDLE, RING, PINKY, THUMB)

int encoderPosition = {0,0,0,0,0};
float detectedForce = {0.0,0.0,0.0,0.0,0.0};
float desiredForce = {0.0,0.0,0.0,0.0,0.0};

void getAllFsr(){
  if(FORCE_PROCESSING){
  }
  else{
    detected_force[0] = ((float) fsrReading(FSR_PIN_INDEX))/1000.0;
    detected_force[1] = ((float) fsrReading(FSR_PIN_MIDDLE))/1000.0;
    detected_force[2] = ((float) fsrReading(FSR_PIN_RING))/1000.0;
    detected_force[3] = ((float) fsrReading(FSR_PIN_PINKY))/1000.0;
    if(THUMB_ENABLE){
      detected_force[4] = ((float) fsrReading(FSR_PIN_INDEX))/1000.0;
    }
    else{
      detected_force[4] = 0.5;
    }
  }
}

int fsrReading(unsigned short PIN){
  // isolated like this to perform image_processing could change for ijndividiaulized outputs
  return analogRead(PIN);
}

String floatToString(float input)
{
  return String(input,4);
}

void serializeEncoderAndForce(){
  Serial.print("encoder ")
  for(int element:encoderPosition){
    serial.print(element);
    serial.print(" ");
  }
  Serial.print(": force ")
  for(float element:detectedForce){
    Serial.print(floatToString(element));
    Serial.print(" ");
  }
  Serial.print("\n")
}

void getSimualtionContactForces(){
  LinkedList<String> string_list;

  if(Serial){
    String str = Serial.readStringUntil("\n");
    /*
     dropt the messsage Header
     Split everything after the colon between spaces
    */
  }

}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(FSR_PIN_INDEX, INPUT);
  pinMode(FSR_PIN_MIDDLE, INPUT);
  pinMode(FSR_PIN_RING, INPUT);
  pinMode(FSR_PIN_PINKY, INPUT);
  pinMode(FSR_PIN_THUMB, INPUT);

  pinMode(INDEX_ENCA, INPUT);
  pinMode(INDEX_ENCB, INPUT);
  pinMode(MIDDLE_ENCA, INPUT);
  pinMode(MIDDLE_ENCB, INPUT);
  pinMode(RING_ENCA, INPUT);
  pinMode(RING_ENCB, INPUT);
  pinMode(PINKY_ENCA, INPUT);
  pinMode(PINKY_ENCB, INPUT);
  pinMode(THUMB_ENCA, INPUT);
  pinMode(THUMB_ENCB, INPUT);

  Serial.begin(115200);
  Serial.print("Pins Initialized");
}



void loop() {\

}
