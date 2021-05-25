#include <OneWire.h>
#include <DallasTemperature.h>
#include "DHT.h"
#include "HX711.h"

/* --- Setup Temperature Sensors --- */
#define ONE_WIRE_BUS 2 // Temp pins on D2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

/* --- Seupt Humidity Sensors ---*/
#define DHTTYPE DHT22
#define DHTPIN1 3
#define DHTPIN2 4

DHT dht[] = {
  {DHTPIN1, DHT22},
  {DHTPIN2, DHT22},
};

/* --- Setup Scale Sensors --- */
#define DOUT_PIN 5
#define SCK_PIN 6

#define calibration -7050.0 // what is 0?

HX711 scale;

float humidity[2];
float temperature[2];

void setup(void)
{
  // Start Serial Communication for Debugging
  Serial.begin(9600);
  sensors.begin(); // temp sensors
  for (auto& sensor : dht) {
    sensor.begin();
  }
  scale.begin(DOUT_PIN, SCK_PIN); 
  scale.set_scale(calibration);
}

void loop(void){
  // Call below to issue a global temp and request to all sensors 
  sensors.requestTemperatures();
  
  // Temp Sensors
  /* --- First Sensor --- */
  //Serial.print("temp1");
  Serial.print(sensors.getTempCByIndex(0));
  
  /* --- Second Sensor --- */
  Serial.print(", ");
  Serial.print(sensors.getTempCByIndex(1));
  
  //DHT Humidity Sensors
  for (int i = 0; i < 2; i++) {
    temperature[i] = dht[i].readTemperature();
    humidity[i] = dht[i].readHumidity();
  }
  
  for (int i = 0; i < 2; i++) {
    Serial.print(F(", "));
    //Serial.print(i);
    //Serial.print(": ");
    Serial.print(humidity[i]);
    //Serial.print(F("%"));
    Serial.print(F(", "));
    //Serial.print(i + 3);
    //Serial.print(": ");
    Serial.print(temperature[i]);
  }

  Serial.print(", ");
  Serial.print(scale.get_units(), 1);
  
  Serial.println(" ");
  
  delay(1000);
}
