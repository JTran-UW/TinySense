# Welcome to the TinySense Docs!

The TinySense is a ultra low-weight, low-power, low-computation avionics system for Flying Insect Robots (FIRs) made by the [Autonomous Insect Robotics Lab](https://depts.washington.edu/airlab/).  This codebase is divided into three sections:

## TinySense Code

Under `/src/*` folders, contains the libraries and sketches deployed to an [Adafruit nRF52840 Feather Express](https://www.adafruit.com/product/4062) during testing and experiments.  The `lib` folder contains the custom Lucas-Kanade library used to compute optical flow.  The `Arduino_PAG7920` library used in some sketches is not included in `lib`, as details regarding the PAG7920LT are confidential.

## Data and Plotting

Under `/experiments/`, contains the experimental data and processing and plotting scripts.  To generate graphs used in the paper, installed the requirements listed in `requirements.txt` on any virtual environment and run `python experiments/main.py`

## Docs

Source code for [TinySense website](https://jtran-uw.github.io/TinySense/).
