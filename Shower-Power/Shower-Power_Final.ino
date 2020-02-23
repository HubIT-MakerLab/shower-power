//importing necessary libraries
#include <OneWire.h> 
#include <DallasTemperature.h>
#include <Adafruit_NeoPixel.h>

//defining wire bus, pin of neopixel connection on arduiono and amount of LEDs of neopixel 
#define ONE_WIRE_BUS 2 
#define LED_PIN    3
#define LED_COUNT 12

//defining critical showertime limits, crititcal time starts after 1minute, super critical from 2min. using ardiuno "time" function
#define TIME_CRITICAL 60000//1*60*1000
#define TIME_SUPER_CRITICAL 120000 // 2*60*1000
unsigned long time;


Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
OneWire oneWire(ONE_WIRE_BUS); 
DallasTemperature sensors(&oneWire);

//runs once for initialising 
void setup(void) 
{ 
 // start serial port 
 Serial.begin(9600); 
 Serial.println("Dallas Temperature IC Control Library Demo"); 
 // Start up the library 
 sensors.begin(); 
 strip.begin();
} 

//function to set whole neopixel ring to one colour. Colour defined by arguments in RGB-mode
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
  Serial.println("Temperature: ");
  Serial.println(temp);
 
 //traffic-light system for either exceeding temperature or max shower time
   if (temp>=40 || time >= TIME_SUPER_CRITICAL)
  {
    //RED
   set_color(255,0,0);
  }
  else if (temp>=36 || time >= TIME_CRITICAL)
  {
    //YELLOW -- slightly less green to have a less greenish yellow
    set_color(255,215,0);
  }
  else
  {
    //GREEN
    set_color(0,255,0);
  }
  
} 
