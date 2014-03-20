int LED = 13;
int ENABLE_FLOW_PIN = 2;
int DISABLE_FLOW_PIN = 3;
int OVERRIDE_PIN = 10;
int speaker = 4;
int FLOW_INDICATOR_PIN = 12;
boolean flowing = false;
boolean broken = false;


int PULSE_MILLISECONDS = 500;
long AUTO_OFF_TICS = 1000l * 60l * 5l; // 5 Minutes
long lastUpdateTime = millis();

// branch spesific variabls:
#include <Servo.h>

Servo valve_servo;  // create servo object to control a servo 

int potPinOpen = 0;  // analog pin used to connect the potentiometer that sets the open postion of the valve
int potPinClosed = 1; // analog pin used to connect the potentiometer that sets the closed postion of the valve
int val;    // variable to read the value from the analog pin 
int openTime = 100;  
int closedTime = 100;



void setup() {
  pinMode(LED, OUTPUT);
  pinMode(FLOW_INDICATOR_PIN, OUTPUT);
  pinMode(ENABLE_FLOW_PIN, OUTPUT);
  pinMode(DISABLE_FLOW_PIN, OUTPUT);
  pinMode(OVERRIDE_PIN, INPUT);
  Serial.begin(9600);
  Serial.write("I am peachy");
  disableFlow();
  speakOk();
  valve_servo.attach(7);  // rylan - attaches the servo on pin 7 to the servo object 
}

void servo_valve_on() // rylan added this !
{
  for (int loopCount = 0; loopCount <= openTime; loopCount += 1){   
  val = analogRead(potPinOpen);            // reads the value of the potentiometer (value between 0 and 1023) 
  val = map(val, 0, 1023, 0, 179);     // scale it to use it with the servo (value between 0 and 180) 
  valve_servo.write(val);                  // sets the servo position according to the scaled value 
  delay(10);
}
}

void servo_valve_off()  // rylan added this too 
{
  for (int loopCount = 0; loopCount <= closedTime; loopCount += 1){   
  val = analogRead(potPinClosed);            // reads the value of the potentiometer (value between 0 and 1023) 
  val = map(val, 0, 1023, 0, 179);     // scale it to use it with the servo (value between 0 and 180) 
  valve_servo.write(val);                  // sets the servo position according to the scaled value 
  delay(10);
}
}





void speakOk(){
  tone(4,523,250);
  delay(250);
  tone(4,768,250);
  delay(250);
  tone(4,1068,250);
  delay(250);
}

void speakBad() {
  tone(4,523,250);
  delay(250);
  tone(4,440,500);
  delay(500);
}

void enableFlow() {
  if (!flowing){
    digitalWrite(ENABLE_FLOW_PIN, HIGH);
    digitalWrite(FLOW_INDICATOR_PIN, HIGH);
    servo_valve_on(); // rylan was here :)
    flowing = true;
    broken = false;
    delay(PULSE_MILLISECONDS);
    digitalWrite(ENABLE_FLOW_PIN, LOW);
  }
}

void disableFlow(){
  if (flowing){
    digitalWrite(DISABLE_FLOW_PIN, HIGH);
    digitalWrite(FLOW_INDICATOR_PIN, LOW);
    servo_valve_off(); // rylan 
    flowing = false;
    broken  =false;
    delay(PULSE_MILLISECONDS);
    digitalWrite(DISABLE_FLOW_PIN, LOW);
  }
}

void toggleFlow(){
  lastUpdateTime = millis();
  if (flowing){
      disableFlow();
    } else {
      enableFlow();
    }
    delay(1000);
}

void loop() {
  digitalWrite(LED, LOW);
  char data = Serial.read();
  digitalWrite(LED, HIGH);
  boolean override = digitalRead(OVERRIDE_PIN);
  if (override == HIGH ){
    toggleFlow();
  } else {
    if (data == '0') {
      lastUpdateTime = millis();
      disableFlow();
    } else if (data == '1') {
      lastUpdateTime = millis();
      enableFlow();
      broken = false;
    } else if ( millis() - lastUpdateTime  > AUTO_OFF_TICS && !broken) {
        disableFlow();
        speakBad();
        broken = true;
    }
  }
}
