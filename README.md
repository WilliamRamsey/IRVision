# IRVision
IR vision is a library designed for building computer vision systems with multiple cameras.

## Threading archatecture
IRVision contains a setup script and two modes of operation.

### Stereo Calibration
The calibrate_procedure.py script contains a process for taking checkerboard calibration images and computing the mono and stereo camera matricies.

### Live detection
The live detection mode contains 4 primary processes:
- capture image
- detect keypoints and triangulate
- physics
- update GUI with latest triangulation

The recording thread polls the cameras for images and pushes these images to the capture object live

### Post detectino

## Classes

### Camera

Abstracts the hardware setup of a camera
Contains tools for taking images and calibrating using a checkerboard pattern.

### Stereo

Contains tools for capturing images from two cameras
Contains tools for calibrating the relitive positions of the cameras
Triangulates points in 3D based on the camera calibration

### Capture

A capture is the primary method of

### GUI

Second thread that polls from one capture at a time.