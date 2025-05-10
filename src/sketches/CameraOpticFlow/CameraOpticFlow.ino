/*
  This sketch sends optic flow data serially for processing by Arduino Serial Plotter.
*/

#include <Arduino_PAG7920.h>
#include <LKOpticFlow.h>

#define OF_WIDTH    40  // Width of optic flow data array
#define OF_HEIGHT   30  // Height of optic flow data array
#define OF_PATCH    10  // Size of patch in optic flow

OpticFlowProvider<OF_WIDTH, OF_HEIGHT, OF_PATCH> opticFlow;

// QVGA: lineLength = 320, lineCount = 240
// QQVGA: lineLength = 160, lineCount = 120
// Changing resolution requires a power-off/power-on restart
const uint16_t lineLength = 160;
const uint16_t lineCount = 120;
const uint8_t skipFactor = lineLength / OF_WIDTH;
uint32_t frameNum;

unsigned char data[lineLength * lineCount];

// Run once to initialize camera
void setup() {
  Serial.begin(500000);
  while (!Serial);

  if (!Camera.begin(lineLength, lineCount, 160, 6, 1)) {
    Serial.println("Failed to initialize camera!");
  }
  delay(100);

  frameNum = 0;
}

// Repeats infinitely.
void loop() {
  Camera.readFrame(data);
  opticFlow.update(data, skipFactor);
  frameNum++;

  Serial.println("xVel:" + String(opticFlow.getXVelocity() * 160));
  Serial.print(",");
  Serial.println("yVel:" + String(opticFlow.getYVelocity() * 160));
}
