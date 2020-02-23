#include <OneWire.h> 
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 2 
#define LED_GREEN A1
#define LED_YELLOW A2
#define LED_RED A3
#define TIME_CRITICAL 60000//1*60*1000
#define TIME_SUPER_CRITICAL 120000 // 2*60*1000
unsigned long time;
OneWire oneWire(ONE_WIRE_BUS); 
DallasTemperature sensors(&oneWire);

void setup(void) 
{ 
 // start serial port 
 Serial.begin(9600); 
 Serial.println("Dallas Temperature IC Control Library Demo"); 
 // Start up the library 
 sensors.begin(); 
  pinMode(LED_GREEN,OUTPUT);
  pinMode(LED_YELLOW,OUTPUT);
  pinMode(LED_RED,OUTPUT);
} 
void loop(void) 
{ 
  time = millis();
  Serial.print("Time: ");
  Serial.println(time); //prints time since program started
  sensors.requestTemperatures(); // Send the command to get temperature readings 
  Serial.println(sensors.getTempCByIndex(0));
  delay(1000); 
  int temp = sensors.getTempCByIndex(0);
  Serial.println("Tempreature: ");
  Serial.println(temp);
   if (temp>=40 || time >= TIME_SUPER_CRITICAL)
  {
    //RED
    digitalWrite(LED_GREEN,LOW);
    digitalWrite(LED_YELLOW,LOW);
    digitalWrite(LED_RED,HIGH);
  }
  else if (temp>=36 || time >= TIME_CRITICAL)
  {
    //YELLOW
    digitalWrite(LED_GREEN,LOW);
    digitalWrite(LED_YELLOW,HIGH);
    digitalWrite(LED_RED,LOW);
  }
  else
  {
    //GREEN
    digitalWrite(LED_GREEN,HIGH);
    digitalWrite(LED_YELLOW,LOW);
    digitalWrite(LED_RED,LOW);
  }
  
} 
