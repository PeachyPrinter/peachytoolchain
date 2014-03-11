int LED = 13;
int ENABLE_FLOW_PIN = 2;
int DISABLE_FLOW_PIN = 3;
int OVERRIDE_PIN = 10;
int speaker = 4;
boolean flowing = false;
boolean broken = false;


int PULSE_MILLISECONDS = 500;
long AUTO_OFF_TICS = 1000l * 60l;
long lastUpdateTime = millis();

void setup() {
  pinMode(LED, OUTPUT);
  pinMode(LED, OUTPUT);
  Serial.begin(9600);
  Serial.write("I am peachy");
  disableFlow();
  speakOk();
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
    flowing = true;
    broken = false;
    lastUpdateTime = millis();
    delay(PULSE_MILLISECONDS);
    digitalWrite(ENABLE_FLOW_PIN, LOW);
  }
}

void disableFlow(){
  if (flowing){
    digitalWrite(DISABLE_FLOW_PIN, HIGH);
    flowing = false;
    broken  =false;
    lastUpdateTime = millis();
    delay(PULSE_MILLISECONDS);
    digitalWrite(DISABLE_FLOW_PIN, LOW);
  }
}

void toggleFlow(){
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
      disableFlow();
      lastUpdateTime = millis();
    } else if (data == '1') {
      enableFlow();
      broken = false;
    } else if ( millis() - lastUpdateTime  > AUTO_OFF_TICS && !broken) {
        disableFlow();
        speakBad();
        broken = true;
    }
  }
}
