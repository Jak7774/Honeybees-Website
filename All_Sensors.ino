/*
   -------------------------------------------------------------------------------------
   All Sensors
   Read All Sensors from the BeeHive and send to Pi for processing
   Jack Elkes
   11NOV2023
   -------------------------------------------------------------------------------------
*/

#include <OneWire.h>
#include <DallasTemperature.h>
#include <Arduino.h>
#include <Wire.h>
#include "Adafruit_SHT31.h"
#include <HX711_ADC.h>

#include <HX711_ADC.h>
#if defined(ESP8266)|| defined(ESP32) || defined(AVR)
#include <EEPROM.h>
#endif

/* --- Setup Temperature Sensors --- */
#define ONE_WIRE_BUS 2 // Temp pins on D2 
OneWire oneWire(ONE_WIRE_BUS); 
DallasTemperature sensors(&oneWire);

/* --- Seupt Humidity Sensors ---*/
Adafruit_SHT31 sht31 = Adafruit_SHT31(); float temp[2]; float humid[2];

/* Analogue Transmission of Data */
void TCA9548A(uint8_t bus){
  Wire.beginTransmission(0x71);  // TCA9548A address is 0x70
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
  //Serial.print(bus);
}

/* --- Setup Scale Sensors --- */
const int HX711_dout = 5; //mcu > HX711 dout pin
const int HX711_sck = 6; //mcu > HX711 sck pin

//HX711 constructor:
HX711_ADC LoadCell(HX711_dout, HX711_sck);
unsigned long t = 0;
const int calVal_eepromAdress = 0;

/* -----------------------------
  Setup Sensors
  -----------------------------*/

void setup(void) {
  // Start Serial Communication for Debugging
  Serial.begin(9600);

  sensors.begin(); // temp sensors

  // SHT31 Sensors
  //sht31.begin(0x44);
  Wire.begin(); // I2C Multiplexer
  
  if (! sht31.begin(0x44) && ! sht31.begin(0x45)) {   // Set to 0x45 for alternate i2c addr
    Serial.println("Couldn't find SHT31");
    //while (1) delay(1);
  }

  // Scales
  float calibrationValue; // calibration value
  //calibrationValue = 696.0; // uncomment this if you want to set this value in the sketch
#if defined(ESP8266) || defined(ESP32)
  EEPROM.begin(512); // uncomment this if you use ESP8266 and want to fetch this value from eeprom
#endif
  EEPROM.get(calVal_eepromAdress, calibrationValue); // uncomment this if you want to fetch this value from eeprom

  LoadCell.begin();
  //LoadCell.setReverseOutput();
  unsigned long stabilizingtime = 2000; // tare preciscion can be improved by adding a few seconds of stabilizing time
  boolean _tare = false; //set this to false if you don't want tare to be performed in the next step
  LoadCell.start(stabilizingtime, _tare);
  if (LoadCell.getTareTimeoutFlag()) {
    //Serial.println("Timeout, check MCU>HX711 wiring and pin designations");
  }
  else {
    LoadCell.setCalFactor(calibrationValue); // set calibration factor (float)
    //Serial.println("Startup is complete");
  }
}

/* -----------------------------
  Loop to Read Sensors and send to Serial
  -----------------------------*/

void loop(void) {
  // Call below to issue a global temp and request to all sensors
  sensors.requestTemperatures();

  // Temp Sensors
  /* --- First Sensor --- */
  //Serial.print("temp1");
  Serial.print(sensors.getTempCByIndex(0));
  Serial.print(", ");
  /* --- Second Sensor --- */
  Serial.print(sensors.getTempCByIndex(1));
  Serial.print(", ");

  // SHT31 Humidity Sensors
  for (int i = 0; i < 2; i++) {
    TCA9548A(i);
    temp[i] = sht31.readTemperature();
    humid[i] = sht31.readHumidity();
    Serial.print(humid[i]);
    Serial.print(", ");
    Serial.print(temp[i]);
    Serial.print(", ");
  }

  /* --- Weight Sensor Output --- */
  static boolean newDataReady = 0;
  if (LoadCell.update()) newDataReady = true;

  // get smoothed value from the dataset:
  if (newDataReady) {
    if (millis() > t ) {
      float w = LoadCell.getData();
      Serial.print(w);
      newDataReady = 0;
      t = millis();
    }
  }
  Serial.println(" ");
  delay(1000);
}
