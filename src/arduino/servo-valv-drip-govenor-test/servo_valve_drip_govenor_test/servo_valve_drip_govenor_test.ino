
/*

with a servo shaft conected to a ball valve 
use 2 pots one to set the open position and the other to set the closed position. 

*/



#include <Servo.h>

Servo valve_servo;  // create servo object to control a servo 

int potPinOpen = 0;  // analog pin used to connect the potentiometer that sets the open postion of the valve
int potPinClosed = 1; // analog pin used to connect the potentiometer that sets the closed postion of the valve
int val;    // variable to read the value from the analog pin 
int openTime = 300;  
int closedTime = 300;


void setup() 
{ 
  valve_servo.attach(7);  // attaches the servo on pin 7 to the servo object 
} 



void loop() 
{ 
  
servo_valve_on();

servo_valve_off(); 

} 



void servo_valve_on()
{
  for (int loopCount = 0; loopCount <= openTime; loopCount += 1){   
  val = analogRead(potPinOpen);            // reads the value of the potentiometer (value between 0 and 1023) 
  val = map(val, 0, 1023, 0, 179);     // scale it to use it with the servo (value between 0 and 180) 
  valve_servo.write(val);                  // sets the servo position according to the scaled value 
  delay(10);
}
}

void servo_valve_off()
{
  for (int loopCount = 0; loopCount <= closedTime; loopCount += 1){   
  val = analogRead(potPinClosed);            // reads the value of the potentiometer (value between 0 and 1023) 
  val = map(val, 0, 1023, 0, 179);     // scale it to use it with the servo (value between 0 and 180) 
  valve_servo.write(val);                  // sets the servo position according to the scaled value 
  delay(10);
}
}


