#include "LKOpticFlow.h"

template <uint16_t WIDTH, uint16_t HEIGHT, uint16_t PATCHSIZE>
OpticFlowProvider<WIDTH, HEIGHT, PATCHSIZE>::OpticFlowProvider() {}

/**
 * Calculates the average optic flow of the entire image.
 * 
 * @param prev the intensity values of the previous frame
 * @param curr the intensity values of the current frame
 */
template <uint16_t WIDTH, uint16_t HEIGHT, uint16_t PATCHSIZE>
void OpticFlowProvider<WIDTH, HEIGHT, PATCHSIZE>::update(uint8_t input[], int skipFactor)
{
  performArraySkip(input, skipFactor);

  xVelocity = 0;
  yVelocity = 0;
  for (int i = 0; i < HEIGHT; i += PATCHSIZE) {
    for (int j = 0; j < WIDTH; j += PATCHSIZE) {
      calculateVelocities(data, i, j);
    }
  }

  // Move data into previous data array
  memcpy(&prev[0], data, WIDTH * HEIGHT);
}


template <uint16_t WIDTH, uint16_t HEIGHT, uint16_t PATCHSIZE>
void OpticFlowProvider<WIDTH, HEIGHT, PATCHSIZE>::performArraySkip(uint8_t input[], int skipFactor)
{
  int i = 0;
  for (int y = 0; y < HEIGHT * skipFactor; y += skipFactor) {
    for (int x = 0; x < WIDTH * skipFactor; x += skipFactor) {
      data[i] = input[y * WIDTH * skipFactor + x]; 
      i++;
    }
  };
}

/**
 * Calculates the optic flow of a small region of the image and adds it to the average optic flow
 * of the entire image.
 * 
 * @param prev the intensity values of the previous frame
 * @param curr the intensity values of the current frame
 * @param A the x and y partial derivatives of the intensity at each pixel
 * @param b the difference between the intensities of the previous frame and the current frame
 * @param row the starting row of pixels to calculate the optic flow
 * @param col the starting col of pixels to calculate the optic flow
 */
template <uint16_t WIDTH, uint16_t HEIGHT, uint16_t PATCHSIZE>
void OpticFlowProvider<WIDTH, HEIGHT, PATCHSIZE>::calculateVelocities(uint8_t input[], uint8_t row, uint8_t col)
{
  // Initializes the A matrix (partial derivative of intensity with respect to x and y)
  // and b vector (partial derivative of intensity with respect to time)
  int index = 0;
  for (int i = row + 1; i < row + PATCHSIZE - 1; i++) { // ignores borders
    for (int j = col + 1; j < col + PATCHSIZE - 1; j++) {
        int flatIndex = i * WIDTH + j;
        A(index, 0) = (prev[flatIndex + 1] - prev[flatIndex - 1])/2;
        A(index, 1) = (prev[flatIndex + WIDTH] - prev[flatIndex - WIDTH])/2;
        b(index) =  prev[flatIndex] - input[flatIndex];
        index++;
    }
  }

  // Calculates the velocity vector with repect to x and y using Lucas-Kanade
  // if the image patch is textured enough (edges and smooth regions lead to 
  // singular matrices)
  BLA::Matrix<2, 2> product = ~A * A;
  if (Invert(product)) {
    BLA::Matrix<2, 1> z = ~A * b; 
    BLA::Matrix<2> v = product * z;
    xVelocity += v(0) / (patchRows * patchCols);
    yVelocity += v(1) / (patchRows * patchCols);
  }
}

template <uint16_t WIDTH, uint16_t HEIGHT, uint16_t PATCHSIZE>
float OpticFlowProvider<WIDTH, HEIGHT, PATCHSIZE>::getXVelocity()
{
  return xVelocity;
}

template <uint16_t WIDTH, uint16_t HEIGHT, uint16_t PATCHSIZE>
float OpticFlowProvider<WIDTH, HEIGHT, PATCHSIZE>::getYVelocity()
{
  return yVelocity;
}

