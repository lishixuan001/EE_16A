/*
  EE16A Touchscreen Week 2: Capacitive Touchscreen
  
  Test the capacitive touchscreen switch circuit. 
  You should see a capacitor discharging on the oscilloscope.
 */

int control_switch = P6_0; //select thhe control pin

// The setup function runs once when you press reset or power the LaunchPad
void setup() {
  // Initialize digital pin P6_0 as an output.
  pinMode(control_switch, OUTPUT);
}

// The loop function runs over and over again forever while the Launchpad has power
void loop() {
  digitalWrite(control_switch, HIGH);   // set the control output to HIGH
  delay(3);                 // wait for 3ms
  digitalWrite(control_switch, LOW);    // set the control output to LOW
  delay(3);                 // wait for 3ms
}
