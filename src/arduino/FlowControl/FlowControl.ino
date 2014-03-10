int LED = 13;
int ENABLE_FLOW_PIN = 2;
int DISABLE_FLOW_PIN = 3;
int override = 10;
int speaker = 4;
boolean flowing = false;
boolean broken = false;

int PULSE_MILLISECONDS = 500;
int AUTO_OFF_TICS = 100000;
int ticsSinceChange = 0;

void setup() {
  pinMode(LED, OUTPUT);
  pinMode(LED, OUTPUT);
  Serial.begin(9600);
  Serial.write("I am peachy");
  disableFlow();
  speakOk();
}

void speakOk(){
  tone(4,262,500);
  tone(4,392,250);
  tone(4,523,250);
}

void speakBad() {
  tone(4,523,250);
  tone(4,392,250);
  tone(4,262,500);
}

void enableFlow() {
  digitalWrite(ENABLE_FLOW_PIN, HIGH);
  flowing = true;
  ticsSinceChange = 0;
  delay(PULSE_MILLISECONDS);
  digitalWrite(ENABLE_FLOW_PIN, LOW);
  
}

void disableFlow(){
  digitalWrite(DISABLE_FLOW_PIN, HIGH);
  flowing = false;
  ticsSinceChange = 0;
  delay(PULSE_MILLISECONDS);
  digitalWrite(DISABLE_FLOW_PIN, LOW);
}


void loop() {
  ticsSinceChange++;
  char data = Serial.read();
  if (data == '0' && flowing) {
    disableFlow();
  } else if (data == '1' && !flowing) {
    enableFlow();
  } else if (ticsSinceChange > AUTO_OFF_TICS) {
      disableFlow();
      speakBad();
  }
}
