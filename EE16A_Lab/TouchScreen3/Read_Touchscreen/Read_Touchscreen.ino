//PSU should be around ~1.0-1.6V. Board should run on 3.3V.
//Note: MSP430 Ground must be connected to PSU ground
//If the student is having issues: unplug the MSP430 power voltage

float a_factor = 5.0/4096.0; // Analog voltage scaling. 
                        // MSP430 analogRead goes to 4096. Online sheet is wrong.                  
int nSamples = 10;      // Number of samples to average over
int LED = GREEN_LED;    // LED output
int drive = P6_0;       // Control output for the drive switch
int clean = P6_1;       // Control output for the clean switch
int vOut = P6_2;        // Must be an analog pin
float threshold = 2.5;  // Threshold to define high or low

/* The setup() function runs every time the Arduino is powered
   on or the RESET button is pressed.*/
void setup() {
  // Start a serial connection to send data to the computer
  Serial.begin(9600);
  Serial.println("/--------Starting New Touchscreen Trial----------/");
  
  // Setup the digital pins as outputs 
  pinMode(LED, OUTPUT); 
  pinMode(drive, OUTPUT);
  pinMode(clean, OUTPUT);
  
  // Set the initial values of these pins to LOW (0V)
  digitalWrite(LED, LOW);
  digitalWrite(drive, LOW);
  digitalWrite(clean, LOW);  
}

/* The loop() function is executed over and over as long as the
   MSP430 is receiving power.*/
void loop () {
  // Take an average of nSamples touchscreen readings
  float sum = 0;
  for (int i = 0; i < nSamples; i++){
    sum += sense();
  }
  sum = sum/nSamples;
  
  // Print the average voltage for nSamples switching cycles
  Serial.print("Average voltage: ");
  Serial.print(sum);
  
  // Check if a touch was detected
  if (sum > threshold){
    // Print that that a touch was detected and turn on the LED
    Serial.print("      Touch detected!");
    digitalWrite(LED, HIGH);
  } else {
    // No touch detected, make sure the LED is off
    digitalWrite(LED, LOW);
  }
  Serial.print("\n");
}

/* sense() performs a full switching sequence and
outputs the voltage reading (float).*/
float sense() {
  // STEP 1: Drain all charge
  digitalWrite(clean, HIGH);
  
  delay(10);
  
  // STEP 2: Stop discharging
  digitalWrite(clean, LOW);
  
  // STEP 3: Charge Ctouchscreen
  digitalWrite(drive,HIGH);
  
  delay(10);  
  
  // STEP 4: Share charge with reference cap
  digitalWrite(drive,LOW);
  

  // Return the the voltage value read at the end of switching
  return (analogRead(vOut)*a_factor);
}
