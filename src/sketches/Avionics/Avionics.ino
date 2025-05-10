/*
  This sketch runs all avionics needed during TinySense experiments.
*/
#include <Adafruit_LittleFS.h>
#include <Adafruit_Sensor.h>
#include <Arduino_PAG7920.h>
#include <InternalFileSystem.h>
#include <LKOpticFlow.h>
#include <SPI.h>
#include <bluefruit.h>
#include "Adafruit_BMP3XX.h"
#include "ICM42688.h"

// BLE Service
BLEDfu bledfu;    // OTA DFU service
BLEDis bledis;    // device information
BLEUart bleuart;  // uart over ble
BLEBas blebas;    // battery

float currResults[3];
#define SEALEVELPRESSURE_HPA (1013.25)

// Pin Setup
#define CAMERA_CS 6
#define CAMERA_INT 1
#define IMU_CS 5
#define PRES_CS 9
#define OF_WIDTH 40   // Width of optic flow data array
#define OF_HEIGHT 30  // Height of optic flow data array
#define OF_PATCH 10   // Size of patch in optic flow

OpticFlowProvider<OF_WIDTH, OF_HEIGHT, OF_PATCH> opticFlow;

// QVGA: lineLength = 320, lineCount = 240
// QQVGA: lineLength = 160, lineCount = 120
// Changing resolution requires a power-off/power-on restart
const uint16_t lineLength = 160;
const uint16_t lineCount = 120;
const uint8_t skipFactor = lineLength / OF_WIDTH;
uint32_t frameNum;
unsigned char data[lineLength * lineCount];
unsigned long currTime;
unsigned long initTime;

Adafruit_BMP3XX bmp;
ICM42688 IMU(SPI, IMU_CS);

// Run once to initialize camera
void setup() {
  Serial.begin(500000);
  while (!Serial);

  // Begin camera
  if (!Camera.begin(lineLength, lineCount, 100, CAMERA_CS, CAMERA_INT)) {
    Serial.println("Failed to initialize camera!");
    while (1) {
    }
  }
  delay(100);

  // Begin IMU
  int status = IMU.begin();
  if (status < 0) {
    Serial.println("Failed to initialize IMU!");
    while (1) {
    }
  }

  // Begin BMP pressure sensor
  if (!bmp.begin_SPI(PRES_CS)) {
    Serial.println("Failed to initialize pressure sensor!");
    while (1) {
    }
  }

  // Set up oversampling and filter initialization
  bmp.setTemperatureOversampling(BMP3_NO_OVERSAMPLING);
  bmp.setPressureOversampling(BMP3_OVERSAMPLING_2X);
  bmp.setIIRFilterCoeff(BMP3_IIR_FILTER_COEFF_3);
  bmp.setOutputDataRate(BMP3_ODR_200_HZ);

  // Setup bluefruit
  Bluefruit.configPrphBandwidth(BANDWIDTH_MAX);
  Bluefruit.begin();
  Bluefruit.setTxPower(4);  // Check bluefruit.h for supported values
  Bluefruit.Periph.setConnectCallback(connect_callback);
  Bluefruit.Periph.setDisconnectCallback(disconnect_callback);
  // To be consistent OTA DFU should be added first if it exists
  bledfu.begin();
  // Configure and Start Device Information Service
  bledis.setManufacturer("Adafruit Industries");
  bledis.setModel("Bluefruit Feather52");
  bledis.begin();
  // Configure and Start BLE Uart Service
  bleuart.begin();
  // Start BLE Battery Service
  blebas.begin();
  blebas.write(100);
  // Set up and start advertising
  startAdv();
  frameNum = 0;
  initTime = millis();
}

void startAdv(void) {
  // Advertising packet
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();
  // Include bleuart 128-bit uuid
  Bluefruit.Advertising.addService(bleuart);
  // Secondary Scan Response packet (optional)
  // Since there is no room for 'Name' in Advertising packet
  Bluefruit.ScanResponse.addName();
  /* Start Advertising
   * - Enable auto advertising if disconnected
   * - Interval:  fast mode = 20 ms, slow mode = 152.5 ms
   * - Timeout for fast mode is 30 seconds
   * - Start(timeout) with timeout = 0 will advertise forever (until connected)
   *
   * For recommended advertising interval
   * https://developer.apple.com/library/content/qa/qa1931/_index.html
   */
  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Scanner.setInterval(160, 80);    // in unit of 0.625 ms
  Bluefruit.Advertising.setFastTimeout(30);  // number of seconds in fast mode
  Bluefruit.Advertising.start(0);  // 0 = Don't stop advertising after n seconds
}

// Repeats infinitely.
void loop() {
  // Get framerate
  if (frameNum != 0 && frameNum % 100 == 0) {
    currTime = millis();
    Serial.println("Frequency: " + String(100.0 / ((currTime - initTime) /
    1000.0))); initTime = currTime;
  }

  // Read IMU
  IMU.getAGT();
  currResults[1] = IMU.gyrX();

  // Read pressure sensor
  currResults[2] = bmp.readAltitude(SEALEVELPRESSURE_HPA);

  // Read Optic Flow
  Camera.readFrame(data);
  opticFlow.update(data, skipFactor);
  currResults[0] = opticFlow.getXVelocity();
  frameNum++;

  // Print out data
  bleuart.write((char*)currResults, 12);
}

/**
 * BLEUART FUNCTIONS
 *
 */
// callback invoked when central connects
void connect_callback(uint16_t conn_handle) {
  // Get the reference to current connection
  BLEConnection* connection = Bluefruit.Connection(conn_handle);
  char central_name[32] = {0};
  connection->getPeerName(central_name, sizeof(central_name));
  Serial.print("Connected to ");
  Serial.println(central_name);
}
/**
 * Callback invoked when a connection is dropped
 * @param conn_handle connection where this event happens
 * @param reason is a BLE_HCI_STATUS_CODE which can be found in ble_hci.h
 */
void disconnect_callback(uint16_t conn_handle, uint8_t reason) {
  (void)conn_handle;
  (void)reason;
  Serial.println();
  Serial.print("Disconnected, reason = 0x");
  Serial.println(reason, HEX);
}
