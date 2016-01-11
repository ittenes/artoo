# ArToo
Balancing robot -  Face detection - Raspberry pi 2 - ServoBlaster - Picamera
OpenCV face tracking on the Raspberry Pi using Python
Core code borrowed from Pan / http://www.instructables.com/id/Pan-Tilt-face-tracking-with-the-raspberry-pi/?ALLSTEPS

# Instalation

## ServoBlaster
Install OpenCV for python: sudo apt-get install python-opencv
Get the wonderful servoblaster servo driver for the raspberry pi by Richard Hirst: 
https://github.com/richardghirst/PiBits/tree/master/ServoBlaster

You can download all the files as a zip archive and extract them to a folder somewhere on the pi.
To install the servo blaster driver open a terminal and CD into the directory where you extracted the servoblaster files
and follow the intrucciones of Richard


## Other libreries
### Python-Opencv and Python-Picamera

Requires a Raspberry Pi computer running an up-to-date raspbian distro and a
RPI camera module installed and configured. The dependencies below may be 
required depending on your previous installs.

    cd ~
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install python-opencv python-picamera



