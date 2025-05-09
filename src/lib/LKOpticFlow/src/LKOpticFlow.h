#ifndef OPTICFLOW_H_
#define OPTICFLOW_H_

#include <BasicLinearAlgebra.h>

template <uint16_t WIDTH, uint16_t HEIGHT, uint16_t PATCHSIZE>
class OpticFlowProvider
{
public:
  OpticFlowProvider();

  void update(uint8_t input[], int skipFactor = 1);
  float getXVelocity();
  float getYVelocity();

private:
  void performArraySkip(uint8_t input[], int skipFactor);
  void calculateVelocities(uint8_t input[], uint8_t row, uint8_t col);

  // User settings
  uint16_t patchRows = HEIGHT / PATCHSIZE;
  uint16_t patchCols = WIDTH / PATCHSIZE;
  
  // State
  BLA::Matrix<(PATCHSIZE - 2) * (PATCHSIZE - 2), 2> A;
  BLA::Matrix<(PATCHSIZE - 2) * (PATCHSIZE - 2)> b;
  float xVelocity;
  float yVelocity;
  uint8_t data[WIDTH * HEIGHT];
  uint8_t prev[WIDTH * HEIGHT];
};

#include "LKOpticFlow.ipp"

#endif
