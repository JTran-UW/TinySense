---
title: Optical Flow
---

Optical Flow was perfomed using the Lucas-Kanade method.  Typically, Lucas-Kanade is used for feature tracking by assuming motion in the local region around a feature is the same.  To estimate flow, we assume that all motion in the frame is due to motion by the robot, i.e. all motion in the frame is in the same direction.

Rather than computing LK optical flow on the entire frame, the TinySense reduces computation by selecting 10 equally spaced patches and averaging their flow vectors.  The below video compares TinySense optical flow with a gyroscope, which under pure rotation will produce the same measurement.  Note that due to difficulties storing captures at high data rates, this video contains flickering artifacts that were not present during the experiments.

<video controls width="800">
  <source src="assets/of.webm" type="video/webm">
  Your browser does not support the video tag.
</video>
