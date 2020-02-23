#include <OneWire.h> 
#include <DallasTemperature.h>
#include <Adafruit_NeoPixel.h>

#define ONE_WIRE_BUS 2 
#define LED_PIN    3
#define LED_COUNT 12
#define TIME_CRITICAL 60000//1*60*1000
#define TIME_SUPER_CRITICAL 120000 // 2*60*1000
unsigned long time;
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
OneWire oneWire(ONE_WIRE_BUS); 
DallasTemperature sensors(&oneWire);


void setup(void) 
{ 
 // start serial port 
 Serial.begin(9600); 
 Serial.println("Dallas Temperature IC Control Library Demo"); 
 // Start up the library 
 sensors.begin(); 
 strip.begin();
} 

void set_color(int R, int G, int B){

  for (size_t i = 0; i < LED_COUNT; i++)
  {
    strip.setPixelColor(i, R, G, B);
    strip.show();
  }
  
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
   set_color(255,0,0);
  }
  else if (temp>=36 || time >= TIME_CRITICAL)
  {
    //YELLOW
    set_color(255,215,0);
  }
  else
  {
    //GREEN
    set_color(0,255,0);
  }
  
} 
