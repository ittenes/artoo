#!/usr/bin/python

# Core code borrowed from
# http://instructables.com/id/Pan-Tilt-face-tracking-with-the-raspberry-pi
# and various other places

print("ServoBlaste and camara.py using python2 and OpenCV2")
print("Loading Please Wait ....")

# ***************** LETS GO *****************

from multiprocessing import Process, Queue
import io
import time
#import datetime
import picamera
import picamera.array
import cv2
import numpy as np

# open ServoBlaster
ServoBlaster = open('/dev/servoblaster', 'w')

# Camera Settings
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240

# Face pattern detection: I found tow archives in internet. I use the first, I think it's better. 
frontalface = cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")		# frontal face pattern detection
profileface = cv2.CascadeClassifier("lbpcascade_profileface.xml")		# profile face pattern detection

# You can try with these two files. If you see that work better let them
#profileface = cv2.CascadeClassifier("haarcascade_profileface.xml")		# side face pattern detection - another way -
#frontalface = cv2.CascadeClassifier("lbpcascade_frontalface.xml")		# frontal face pattern detection - another way -



# Initalizing servos varialbes
mov_1 = 0
mov_0 = 0


def P1(mov_1):  										# Servo 01 - Contrling the moviment of the head -  Pin17 -
	if mov_1 != 0:
		ServoBlaster.write('1=' + str(mov_1) + '\n')	
		ServoBlaster.flush()

def P0(mov_0):  										# Servo 00 - Controling the moviment of the neck - Pin 04 -
	if mov_0 != 0:
		ServoBlaster.write('0=' + str(mov_0) + '\n')
		ServoBlaster.flush()


# I don't erase this code in case of that you want initializate the function without variables
# Process(target=P1, args=()).start()
# Process(target=P0, args=()).start()


# this is de velocity of the servos moviment 
STEP = 1

#============================================================================================================

# CAMERA

#============================================================================================================
print("Initializing Camera ....")

# Save images to an in-program stream
stream = io.BytesIO()

# Initializing picamera
with picamera.PiCamera() as camera:
	camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT)
	camera.contrast = 50
	
	# initialize variables 
	face = [0,0,0,0]	# This will hold the array that OpenCV returns when it finds a face: (makes a rectangle)
	Cface = [0,0]		# Center of the face: a point calculated from the above variable
	lastface = 0		# int 1-3 used to speed up detection. The script is looking for a right profile face,-
						# 	a left profile face, or a frontal face; rather than searching for all three every time,-
						# 	it uses this variable to remember which is last saw: and looks for that again. If it-
						# 	doesn't find it, it's set back to zero and on the next loop it will search for all three.-
						# 	This basically tripples the detect time so long as the face hasn't moved much.

	# Looking for the face
	while(True):
		with picamera.array.PiRGBArray(camera) as stream:
			camera.capture(stream, format='bgr')
			image = stream.array
			# At this point the image is available as stream.array

			faceFound = False		# This variable is set to true if, on THIS loop a face has already been found
									# We search for a face three diffrent ways, and if we have found one already-
									# there is no reason to keep looking.

			# Looking for frontal face
			if not faceFound:
				if lastface == 0 or lastface == 1:
					fface = frontalface.detectMultiScale(image,1.3,4,(cv2.cv.CV_HAAR_DO_CANNY_PRUNING + cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT + cv2.cv.CV_HAAR_DO_ROUGH_SEARCH),(30,30))
					if fface != ():			# if we found a frontal face...
						lastface = 1		# set lastface 1 (so next loop we will only look for a frontface)
						for f in fface:		# f in fface is an array with a rectangle representing a face
							faceFound = True
							face = f

			# Looking for profile face
			if not faceFound:				# if we didnt find a face yet...
				if lastface == 0 or lastface == 2:	# only attempt it if we didn't find a face last loop or if-	
					pfacer = profileface.detectMultiScale(image,1.3,4,(cv2.cv.CV_HAAR_DO_CANNY_PRUNING + cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT + cv2.cv.CV_HAAR_DO_ROUGH_SEARCH),(30,30))
					if pfacer != ():		# if we found a profile face...
						lastface = 2
						for f in pfacer:
							faceFound = True
							face = f

			# Looking for left profile
			# this is another profile face search, because OpenCV can only-
			#	detect right profile faces, if the cam is looking at-
			#	someone from the left, it won't see them. So we just...
			if not faceFound:				# a final attempt
				if lastface == 0 or lastface == 3:	
					cv2.flip(image,1,image)	#	flip the image
					pfacel = profileface.detectMultiScale(image,1.3,4,(cv2.cv.CV_HAAR_DO_CANNY_PRUNING + cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT + cv2.cv.CV_HAAR_DO_ROUGH_SEARCH),(30,30))
					if pfacel != ():
						lastface = 3
						for f in pfacel:
							faceFound = True
							face = f

			if not faceFound:		# if no face was found...-
				lastface = 0		# 	the next loop needs to know
				face = [0,0,0,0]	# so that it doesn't think the face is still where it was last loop

			x,y,w,h = face
			# Cface = [(w/2+x),(h/2+y)]
			if lastface == 3:
				Cface = [(w/2+(CAMERA_WIDTH-x-w)),(h/2+y)]	# we are given an x,y corner point and a width and height, we need the center
			else:
				Cface = [(w/2+x),(h/2+y)]	# we are given an x,y corner point and a width and height, we need the center
			
			print str(Cface[0]) + "," + str(Cface[1])
			
			cv2.rectangle(image, (x,y), (x+w,y+h), cv2.cv.RGB(255, 0, 0), 3, 8, 0)	#painting the rectangle

			cv2.imshow("video", image) #show the image in a window
			cv2.waitKey(1)

			# Close Window if q pressed
			if cv2.waitKey(1) & 0xFF == ord('q'):
				cv2.destroyAllWindows()
				print("End Motion Tracking")
				break
#============================================================================================================

# SERVOS

#============================================================================================================


			if Cface[0] != 0:									# if the Center of the face is not zero- 
																# (meaning no face was found)
				if Cface[1] > 140:								# The camera is moved always the same distance
					for mov_1 in range(157, 155, (STEP*-1)):
						P1(mov_1) 
						time.sleep(.1)
					for mov_1 in range(151, 150 , (STEP*-1)):	# Stop de servos. 
						P1 (mov_1)
						
				if Cface[1] < 100:								# and diffrent dirrections depending on what- 
					for mov_1 in range(143, 145 , STEP):		# side of center if finds a face.
						P1 (mov_1)
						time.sleep(.1)
					for mov_1 in range(150, 151, STEP):			# Stop de servos. 
						P1(mov_1) 

				if Cface[0] > 180:								# and moves diffrent servos depending on what- 
					for mov_0 in range(157, 155, (STEP*-1)):	# axis we are talking about.
						P0(mov_0) 
						time.sleep(.1)
					for mov_0 in range(151, 150 , (STEP*-1)):	# Stop de servos. 
						P0(mov_0)
						
				if Cface[0] < 140:	
					for mov_2 in range(140, 143 , STEP):
						P0(mov_2)
						time.sleep(.1)
					for mov_2 in range(150, 151, STEP):
						P0(mov_2) 





