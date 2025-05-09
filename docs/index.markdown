---
title: Home
layout: default
hide_header: true
---

# TinySense: A Lighter Weight and More Power-efficient Avionics System for Flying Insect-scale Robots

![The TinySense next to the RoboFly and a pencil](assets/withrobo.jpg)

<div style="display: inline-block; margin: 10px 0px;">
<a href="https://arxiv.org/abs/2501.03416" style="border: 2px solid black; border-radius: 2px; padding: 5px 6px; margin-right: 6px;">
  <img src="assets/arxiv.png" height="20px" />
  <span style="color: black; margin-left: 3px;">Paper</span>
</a>

<a href="https://github.com/JTran-UW/tinysense" style="border: 2px solid black; border-radius: 2px; padding: 5px 6px;">
  <img src="assets/github.png" height="20px" />
  <span style="color: black; margin-left: 3px;">Code</span>
</a>
</div>

## Introduction
Due to their miniscule size, Flying Insect Robots (FIRs) are subject to SSWAP--Size, Speed, Weight, and Power--constraints that are not present on other scales of robots.  In the sensing domain, avionics for FIRs must be extremely small, light, and low-power, but also fast enough to perform state estimation on a robot that undergoes very fast motions.  **No sensor-autonomous FIR currently exists.**

<img src="assets/sensors.png" alt="The TinySense compared to a penny" style="display: block; margin: 0px auto;">

The TinySense consists of 3 sensors.  The first is the InvenSense ICM-42688-P Inertial Measurement Unit (IMU).  Second, in a departure from prior work, is a Bosch BMP390 pressure sensor replacing a power-hungry laser rangefinder.  Finally, a bulky optical flow sensor is replaced with a novel tiny global shutter camera by PixArt, while optical flow is computed on an Nordic nRF52840 microcontroller.  **At only 74mg and approximately 15mW, the TinySense presents the current smallest avionics system and is possibly capable of achieving FIR sensor autonomy.**

## Demonstrations
The TinySense was demonstrated on-board the Crazyflie, a quadrotor and the smallest commercially available sensor-autonomous flying robot.  In the videos below, an Adafruit nRF52840 Feather was attached to the top of the Crazyflie, and the TinySense is attached to its underside with the camera facing towards the floor.  The Crazyflie then flew up to an altitude of 1m, traveled forward 1m, and then landed.  The flights were also recorded by a motion capture system as a source of ground truth.
## Sensor Performance

The TinySense sensors perform comparably to the industy-standard sensors on the Crazyflie.  Note that the pressure sensor measures a sharp decline at the beginning of the experiment due to the spinning blades causing a pressure drop.

<video controls width="100%">
  <source src="assets/TinySense_Sensors.webm" type="video/webm">
  Your browser does not support the video tag.
</video>

<br>
## State Estimation

Using a Kalman Filter, the TinySense estimates pitch angle, velocity, and altitude to a high degree of accuracy.

<video controls width="100%">
  <source src="assets/TinySense_Estimates.webm" type="video/webm">
  Your browser does not support the video tag.
</video>
<br>
## Results
The RMS Error of the TinySense against the motion capture is comparable to the Crazyflie, especially in angle, which is most important for hovering tasks.

| Platform | Velocity (m/s) | Pitch Angle (deg) | Altitude (m)
| -------- | -------- | -------- | -------- |
| Crazyflie  | 0.075 ± 0.009  | 1.619 ± 0.267  | 0.021 ± 0.001 |
| TinySense | 0.186 ± 0.015 | 1.573 ± 0.166 | 0.136 ± 0.026 |

The TinySense shows significant reductions in weight and power compared to [prior work](https://ieeexplore.ieee.org/document/9811918).


|  | Weight (mg) | Power (mW) |
| -------- | -------- | -------- |
| Prior Work  | 187   | 21  |
| TinySense | 74 | 15.6 |

## Future Work

The RoboFly, the Autonomous Insect Robotics Lab's FIR, has an estimated maximum payload of 150 mg and a power capacity of 20 mW.  The TinySense shows it is capable of accurate state estimation within these constraints.  Aiming to prove the first sensor-autonomous FIR, we are currently working on integrating the TinySense on the RoboFly.

## Team

The TinySense was made by members of the [Autonomous Insect Robotics Lab](https://depts.washington.edu/airlab/) at the University of Washington.

<div style="display: grid; grid-template-columns: 1fr 1fr 1fr;">
  <div>
    <img src="assets/team/zhitao_yu.png" alt="Zhitao Yu" width="60%">
    <p>Zhitao Yu</p>
  </div>
  <div>
    <img src="assets/team/josh.jpeg" alt="Joshua Tran" width="60%">
    <p>Joshua Tran</p>
  </div>
  <div>
    <img src="assets/team/claire.jpg" alt="Claire Li"  width="60%">
    <p>Claire Li</p>
  </div>
  <div>
    <img src="assets/team/AaronWeberPicture.jpg" alt="Aaron Weber" width="60%">
    <p>Aaron Weber</p>
  </div>
  <div>
    <img src="assets/team/yash_new.png" alt="Yash Talwekar" width="60%">
    <p>Yash Talwekar</p>
  </div>
  <div>
    <img src="assets/team/fuller_portrait-1.jpg" alt="Sawyer Buckminster Fuller"  width="60%">
    <p>Sawyer Buckminster Fuller</p>
  </div>
</div>

## Citing

```
@article{yu2025tinysense,
  title={TinySense: A Lighter Weight and More Power-efficient Avionics System for Flying Insect-scale Robots},
  author={Yu, Zhitao and Tran, Joshua and Li, Claire and Weber, Aaron and Talwekar, Yash P and Fuller, Sawyer},
  journal={arXiv preprint arXiv:2501.03416},
  year={2025}
}
```
