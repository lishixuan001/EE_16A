unsigned int firstSensor = 0;    // first analog sensor
int handshake = 0;

void setup()
{
  // start serial port at 9600 bps:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
  }


//  establishContact();  // send a byte to establish contact until receiver responds
}

void loop()
{
  // if we get a valid byte, read analog ins:
  if (Serial.available() > 0) {
    handshake = Serial.read();
    //Serial.println(handshake,DEC);
    if (handshake == 9)//Ascii code for numerical 9
    {
       Serial.flush();
    }
    else
    {  
        if(handshake == 1 || handshake == 54)//54 is ascii code for 6 so serial monitor works
        {
          firstSensor = 0;
    
          for (int count = 0; count < 10 ; count ++)
          {  
            firstSensor += analogRead(A0);
            delay(1);
          }
          
          Serial.println(firstSensor/10,DEC);
          
        }
  }  
    
 
    //Serial.println(firstSensor/10,HEX);
    // delay 10ms to let the ADC recover:
    // send sensor values:


  }
}

void establishContact() {
  while (Serial.available() <= 0) {
    Serial.print('A');   // send a capital A
    delay(300);
  }
}

