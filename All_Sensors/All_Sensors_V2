#include <OneWire.h>
#include <DallasTemperature.h>
#include <Arduino.h>
#include <Wire.h>
#include "Adafruit_SHT31.h"
#include <HX711_ADC.h>
#if defined(ESP8266)|| defined(ESP32) || defined(AVR) #include <EEPROM.h> #endif

/* --- Setup Temperature Sensors --- */
#define ONE_WIRE_BUS 2 // Temp pins on D2 OneWire oneWire(ONE_WIRE_BUS); DallasTemperature sensors(&oneWire);

/* --- Seupt Humidity Sensors ---*/
Adafruit_SHT31 sht31 = Adafruit_SHT31(); float temp[2]; float humid[2];

void TCA9548A(uint8_t bus){
  Wire.beginTransmission(0x71);  // TCA9548A address is 0x70
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
  //Serial.print(bus);
}

/* --- Setup Scale Sensors --- */
const int DOUT_PIN = 5;
const int SCK_PIN = 6;

//float calibration = 22.20; // Calibration Factor HX711_ADC LoadCell(DOUT_PIN, SCK_PIN); const int calVal_eepromAddress = 0; unsigned long t = 0;

/* -----------------------------
  Setup Sensors
  -----------------------------*/

void setup(void) {
  // Start Serial Communication for Debugging
  Serial.begin(9600); delay(10);

  sensors.begin(); // temp sensors
  
  sht31.begin(0x44);

  // if (! sht31.begin(0x44)) {   // Set to 0x45 for alternate I2C address
  //   Serial.println("Couldn't find SHT31");
  //   while (1) delay(1);
  // }

  // SHT31 Sensors
  Wire.begin();

  // Scales
  LoadCell.begin();

  float calibrationValue;
#if defined(ESP8266) || defined(ESP32)
  EEPROM.begin(512);
#endif
  EEPROM.get(calVal_eepromAddress, calibrationValue); // 27MAY2021 Value = -22.75

  unsigned long stabilizingtime = 2000; // preciscion right after power-up can be improved by adding a few seconds of stabilizing time
  boolean _tare = false; //set this to false if you don't want tare to be performed in the next step
  LoadCell.start(stabilizingtime, _tare);
  if (LoadCell.getTareTimeoutFlag()) {
    Serial.println("Timeout, check MCU>HX711 wiring and pin designations");
    while (1);
  }
  else {
    LoadCell.setCalFactor(calibrationValue); // set calibration value (float)
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

  /* --- Second Sensor --- */
  Serial.print(", ");
  Serial.print(sensors.getTempCByIndex(1));

  Serial.print(", ");

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
  const int serialPrintInterval = 0;

  if (LoadCell.update()) newDataReady = true;

  if (newDataReady) {
    if (millis() > t + serialPrintInterval ) {
      float w = LoadCell.getData();
      Serial.print(w);
      newDataReady = 0;
      t = millis();
    }
  }

  Serial.println(" ");
  //delay(1000);
