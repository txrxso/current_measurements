# current_measurements
Using the INA219 breakout board to measure current draw for 430.

## 1. Features
Code for Arduino Uno to get current reading values from INA219 breakout board, and send them via serial so a python script running at the same time can log the values and make plots. 

`data` - where data is logged and saved.
`python` - python script for logging and plotting
`src` - code for firmware to use INA219.

## 2. Configurations that need to be measured
### 2.1 Topology:
1. Gateway node only
2. Gateway and noise node 
3. Gateway and air quality node
4. Gateway, noise, and air quality node

### 2.2 Scenarios:
A. Heartbeats only (5 minute intervals)
B. Heartbeats (5 minute intervals) and 'mock' alerts every 12 minutes (~5 alerts per hour)
C. Heartbeats (5 minute intervals) and 'mock' alerts every 5 minutes (~12 alerts per hour)

### 2.3 Test plan: 
Collect data for combinations of: 
| Topology | Scenario | Data Collected (Y/N?) |
| -------- | -------- | -------- |
| 1 | A | No|
| 1 | B | No|
| 1 | C | No|
| 1 | D | No|
| 2 | A | No|
| 2 | B | No|
| 2 | C | No|
| 2 | D | No|
| 3 | A | No|
| 3 | B | No|
| 3 | C | No|
| 3 | D | No|
| 4 | A | No|
| 4 | B | No|
| 4 | C | No|
| 4 | D | No|


## Wiring Tutorial
https://learn.adafruit.com/adafruit-ina219-current-sensor-breakout/wiring 


## Rebuild configuration files 
`pio project init --ide vscode` 