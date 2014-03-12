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
