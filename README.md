Set up:
---


1.  Set up the step motor by attaching the - on the controller board to any ground (pin 6), the + on the controller board to any 5v power (pin 4) and attach to any GPIO pin (pins 18,22,24,26)
2.  Set up the ultra sonic distance sensor by attching the vcc to the 3.3V (pin 17) and Gnd to any ground (pin 9). Next attach trig and echo to any GPIO pin (trig 15, echo 13)


How it works
---
- We set up a gui to interact with our tools.
- We define what one full rotation is based off step sequence
- we create a scan button that will do one full roation to the right while storing the distance (input from the ultra sonic sensor) and the rotation x 360.
- Plot and connect the points we gathered from the scan using matplotlib to create the 2d scan of our space

Usage
---
- Unfortunately I don't have a 3d printer to effeciently mount the sensor to the motor
- The picture is a example of the sensor pointed to the celling of the room. the distance will stay constant so we will get a circle but when we mount it our distances will be variable so we can see the walls/objects
