/*
  This sketch sends image data to ArduImageCapture from a PAG7920 camera.
  It was inspired heavily by Indreluuk's OV7670 library and the
  Arduino_OV7670 library.
*/

#include <Arduino_PAG7920.h>

// QVGA: lineLength = 320, lineCount = 240
// QQVGA: lineLength = 160, lineCount = 120
// Changing resolution requires a power-off/power-on restart
const uint16_t lineLength = 160;
const uint16_t lineCount = 120;
uint8_t data[lineLength * lineCount];
uint32_t frameNum;

/**
 * This pixel format is technically for RGB565, but because the PAG7920 puts out an 8-bit raw
 * data format that is not supported by ArduImageCapture, we had to translate these 8 bits to
 * RGB565 to send it over. More on this in sendFrame()
 */
const uint16_t pixelFormat = 0x01;

// Pixel byte parity check:
// Pixel Byte H: odd number of bits under H_BYTE_PARITY_CHECK and H_BYTE_PARITY_INVERT
// Pixel Byte L: even number of bits under L_BYTE_PARITY_CHECK and L_BYTE_PARITY_INVERT
//                                          H:RRRRRGGG
const uint8_t H_BYTE_PARITY_CHECK =  0b00100000;
const uint8_t H_BYTE_PARITY_INVERT = 0b00001000;
//                                          L:GGGBBBBB
const uint8_t L_BYTE_PARITY_CHECK =  0b00001000;
const uint8_t L_BYTE_PARITY_INVERT = 0b00100000;
// Since the parity for L byte can be zero we must ensure that the total byet value is above zero.
// Increasing the lowest bit of blue color is OK for that.
const uint8_t L_BYTE_PREVENT_ZERO  = 0b00000001;

const uint16_t COLOR_GREEN = 0x07E0;
const uint16_t COLOR_RED = 0xF800;

uint8_t VERSION = 0x10;
uint8_t COMMAND_NEW_FRAME = 0x01 | VERSION;
uint8_t COMMAND_DEBUG_DATA = 0x03 | VERSION;


unsigned long currTime;
unsigned long initTime;

// Run once to initialize camera
void setup() {
  Serial.begin(2000000);
  while (!Serial);

  int result = Camera.begin(lineLength, lineCount, 100, 6, 1);
  if (result) {
    Serial.println("Failed to initialize camera: " + String(result));
  } else {
    Serial.println("Initialized camera");
    Serial.println(String(result));
  }
 
  delay(100); 
  frameNum = 0;
  initTime = millis();
}

// Repeats infinitely. Gets data from camera and displays image using ArduimageCapture
void loop() {
  Camera.readFrame(data);
  sendFrame();
  frameNum++;
}

/**
 * Sends frame data to ArduimageCapture.
 * 
 * CLARIFICATION ON THE BIT OPERATIONS DONE HERE
 * In RGB, if all values R, G, and B are equal, the color comes out grey/monochrome. 
 * Thus, to convert the monochrome 8-bit pixel from the PAG7920 to RGB565, we shift 
 * it 3 bits to the right to fit it into a 5-bit format, put this value into the R, G,
 * and B places in the RGB565 format, and send these two bytes.
 */
void sendFrame() {
  uint8_t pixel;
  uint8_t pixelH;
  uint8_t pixelL;

  commandStartNewFrame(pixelFormat);
  for (uint16_t i = 0; i < lineCount; i++) {
    for (uint16_t j = 0; j < lineLength; j++) {
      pixel = data[i * lineLength + j];
      pixelH = (pixel & 0xF8) | (pixel >> 5);
      pixelL = ((pixel << 3) & 0xE0) | (pixel >> 3);
  
      Serial.write(formatRgbPixelByteH(pixelH));
      Serial.write(formatRgbPixelByteL(pixelL));
    }
  }
}

// RRRRRGGG
uint8_t formatRgbPixelByteH(uint8_t pixelByteH) {
  // Make sure that
  // A: pixel color always slightly above 0 since zero is end of line marker
  // B: odd number of bits for H byte under H_BYTE_PARITY_CHECK and H_BYTE_PARITY_INVERT to enable error correction
  if (pixelByteH & H_BYTE_PARITY_CHECK) {
    return pixelByteH & (~H_BYTE_PARITY_INVERT);
  } else {
    return pixelByteH | H_BYTE_PARITY_INVERT;
  }
}

// GGGBBBBB
uint8_t formatRgbPixelByteL(uint8_t pixelByteL) {
  // Make sure that
  // A: pixel color always slightly above 0 since zero is end of line marker
  // B: even number of bits for L byte under L_BYTE_PARITY_CHECK and L_BYTE_PARITY_INVERT to enable error correction
  if (pixelByteL & L_BYTE_PARITY_CHECK) {
    return pixelByteL | L_BYTE_PARITY_INVERT | L_BYTE_PREVENT_ZERO;
  } else {
    return (pixelByteL & (~L_BYTE_PARITY_INVERT)) | L_BYTE_PREVENT_ZERO;
  }
}

void commandStartNewFrame(uint8_t pixelFormat) {
  uint8_t newCommand = 0x00;
  uint8_t commandLength = 4;
  Serial.write(newCommand); // New command
  Serial.write(commandLength); // Command length
  uint8_t checksum = 0;
  checksum = sendNextCommandByte(checksum, COMMAND_NEW_FRAME);
  checksum = sendNextCommandByte(checksum, lineLength & 0xFF); // lower 8 bits of image width
  checksum = sendNextCommandByte(checksum, lineCount & 0xFF); // lower 8 bits of image height
  checksum = sendNextCommandByte(checksum, 
      ((lineLength >> 8) & 0x03) // higher 2 bits of image width
      | ((lineCount >> 6) & 0x0C) // higher 2 bits of image height
      | ((pixelFormat << 4) & 0xF0));
  Serial.write(checksum);
}

void commandDebugPrint(const String debugText) {
  if (debugText.length() > 0) {
    uint8_t newCommand = 0x00;
    Serial.write(newCommand);
    Serial.write((uint8_t) debugText.length() + 1);
    uint8_t checksum = 0;
    checksum = sendNextCommandByte(checksum, COMMAND_DEBUG_DATA);
    for (uint16_t i = 0; i < debugText.length(); i++) {
      checksum = sendNextCommandByte(checksum, debugText[i]);
    }

    Serial.write(checksum);
  }
}

uint8_t sendNextCommandByte(uint8_t checksum, uint8_t commandByte) {
  Serial.write(commandByte);
  return checksum ^ commandByte;
}
