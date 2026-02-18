
#include <Wire.h>
#include <Arduino.h>
#include <Adafruit_INA219.h>

Adafruit_INA219 ina219;
float current_mA=0;
float shuntvoltage_mV=0;
float busvoltage_V=0;
float loadvoltage_V = 0;
float power_mW = 0;

#define CALIBRATION_MODE 1 
#define SAMPLING_INTERVAL_MS 1000
/* 
1: 32V, 2A 
2: 32V, 1A 
3: 16V, 400mA 
*/

void setup() { 
    Serial.begin(115200);
    while (!Serial) {
        delay(1);
    }

    if (!ina219.begin()) {
        Serial.println("Failed to find INA219 chip");
        while (1) { delay(10); }
    }

    if (CALIBRATION_MODE == 1) {
        ina219.setCalibration_32V_2A();
    } else if (CALIBRATION_MODE == 2) {
        ina219.setCalibration_32V_1A();
    } else if (CALIBRATION_MODE == 3) {
        ina219.setCalibration_16V_400mA();
    }

}

void loop() { 
    current_mA = ina219.getCurrent_mA();
    shuntvoltage_mV = ina219.getShuntVoltage_mV();
    busvoltage_V = ina219.getBusVoltage_V();
    loadvoltage_V = busvoltage_V + (shuntvoltage_mV / 1000);
    power_mW = ina219.getPower_mW();

    Serial.print("Current:"); Serial.print(current_mA); Serial.println(" mA");
    Serial.print("Shunt Voltage:"); Serial.print(shuntvoltage_mV); Serial.println(" mV");
    Serial.print("Bus Voltage:"); Serial.print(busvoltage_V); Serial.println(" V");
    Serial.print("Load Voltage:"); Serial.print(loadvoltage_V); Serial.println(" V");
    Serial.print("Power:"); Serial.print(power_mW); Serial.println(" mW");

    delay(SAMPLING_INTERVAL_MS);

}