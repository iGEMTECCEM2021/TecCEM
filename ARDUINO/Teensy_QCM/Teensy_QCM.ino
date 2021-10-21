#include <AD9833.h>          // Include the library for AD9833 module
#include <FreqCount.h>       // Include the library to count frequency
#define FNC_PIN 10           // Digital pin 10 for the frame synchronization 

int in1 = 8;                 // Pin to control positive direction of rotation of inlet motor.
int in2 = 7;                 // Pin to control negative direction of rotation of inlet motor
int in3 = 6;                 // Pin to control positive direction of rotation of outlet motor
int in4 = 5;                 // Pin to control negative direction of rotation of outlet motor
AD9833 gen(FNC_PIN);         // Configure the AD9833 FNC Pin
float pwm=1;                 // Initial freqeuncy of 1 Hz
float value_del=1;           // Initial delta time
int deltaT=1000000;          // Measurement time for frequency counter (1000000= 1 s)
int timepump=0;
int mode=0;
unsigned long startTime;
unsigned long endTime;
unsigned long duration;


void setup() {                              // Initial configuration
    gen.Begin();                            // Initialize AD9833
    gen.ApplySignal(SQUARE_WAVE,REG0,pwm);  // Type of signal, for this application it is needed a square wave
    gen.EnableOutput(true);                 // Enable AD9833 output
    Serial.begin(250000);                   // Serial communication speed (units: bauds)
    FreqCount.begin(deltaT);                // Initial delta time of measurement
    pinMode(in1, OUTPUT);                   // Configure all the motors pins as outputs.
    pinMode(in2, OUTPUT);
    pinMode(in3, OUTPUT);
    pinMode(in4, OUTPUT);
}


void fnReading(String cad){                  // Define function for reading serial communication 
  int pos; // pos is an integer
  int subpos; // subpos is an integer
  String label,value, sublabelf, sublabelt;  // label and value are strings
  cad.trim();                                // Separate what it receives
  cad.toLowerCase();                         // To avoid errors, everything is changed to lowercase
  pos = cad.indexOf(':');                    // The structure of communication is label:value, so it looks for ":"
  label= cad.substring(0,pos);               // A new string for the left side 
  value= cad.substring(pos+1);               // A new string for the right side
  if (label.equals("mot")){                  // Label "mot" refers to the value of the generated freqeuncy by AD98333
    pwm = value.toInt();                     // Define the new value
    gen.ApplySignal(SQUARE_WAVE,REG0,pwm);   // Updated generated frequency  
  }
  if (label.equals("del")){                  // Label "del" refers to delta of time       
    gen.ApplySignal(SQUARE_WAVE,REG0,pwm);   // Update generated freqeuncy
    value_del=value.toFloat();               // Convert to float
    deltaT=value_del*1000000;                // Conversion factor
    FreqCount.begin(deltaT);                 // Updated measurement time to count freqeuncy
    }
  if (label.equals("flo")){                  // Label "flo" refers to the type and time of flow
    subpos = value.indexOf(',');
    sublabelf=value.substring(0,subpos);
    sublabelt=value.substring(subpos+1);
    mode = sublabelf.toInt();                     
    timepump= sublabelt.toInt()*1000;        // Obtain time of the pump   
    if (sublabelf.equals("1")){              // Each mode does something
      mode=1; 
    }
    if (sublabelf.equals("2")){
      mode=2;
        }
  }
}

void loop()
{
    if (FreqCount.available()) {                   // If the function to count frequency is availabe, do the following:
      unsigned long count = FreqCount.read();      // Define the type of variable that measures the frequency   
      if (deltaT==1000000){                        // 1 second delta time
        Serial.println("add:" + String(count));    // "add" label will be read in Python
      }
      else if(deltaT==500000){                     // 0.5 second delta time
        Serial.println("add:" + String(count*2));  // Multiply times 2 in order to have frequency in Hz
        }
      else if(deltaT==250000){                     // 0.25 second delta time
        Serial.println("add:" + String(count*4));  // Multiply times 4 in order to have frequency in Hz
        }
      else if(deltaT==200000){                     // 0.2 second delta time
        Serial.println("add:" + String(count*5));  // Multiply times 5 in order to have frequency in Hz
        }
      else if(deltaT==100000){                     // 0.1 second delta time
        Serial.println("add:" + String(count*10)); // Multiply times 10 in order to have frequency in Hz
        }
    }  
    if(Serial.available()){                        // If serial communication is availabe, do the following:
      fnReading(Serial.readString());              // Call reading function
    }
    if (mode == 0){                           // Mode 0 just measures time
      startTime=millis();
    }
    if (mode == 1){                         // Mode 1 turns on both pumps
      endTime=millis();
      duration= endTime - startTime ;
      if (timepump<=duration){             // Turn off the pumps when mode is 0.
        mode=0;
    }
     if (timepump > duration){             // Compare times to turn on the pumps
        digitalWrite(in1, LOW);
        digitalWrite(in2, LOW);
        digitalWrite(in3, LOW);
        digitalWrite(in4, LOW);
    }
    }
    
    if (mode == 2){                        // Mode 2 turns on one pump and then the other one.
      endTime=millis();
      duration= endTime - startTime ;
      if (timepump<=duration){             // Turn off pumps
        mode=0;
        digitalWrite(in1, LOW);          
        digitalWrite(in2, LOW);
      }
      if (timepump > duration){            // Turn on pumps
        digitalWrite(in1, HIGH);
        digitalWrite(in2, LOW);
    }
  }
}
