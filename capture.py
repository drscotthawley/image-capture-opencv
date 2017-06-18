#! /usr/bin/env python2
'''
capture.py   Author: Scott Hawley 

Capture realtime frames from camera, perform reference frame subtraction
Intended for use with ESPI experiment at Belmont university

Uses OpenCV, and can use IDS camera kit: https://github.com/ncsuarc/ids

Code taken from the following tutorials...

Built from Tutorial "Getting Started with Videos"
http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_gui/py_video_display/py_video_display.html

Time-averaging tutorial: https://opencvpython.blogspot.com/2012/07/background-extraction-using-running.html

De-noising: http://docs.opencv.org/master/d5/d69/tutorial_py_non_local_means.html#gsc.tab=0

Cropping: http://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/

Contrast/brightness contols: http://docs.opencv.org/2.4/doc/tutorials/core/basic_linear_transform/basic_linear_transform.html
'''

import numpy as np
import cv2

camera_type = 'local'  # choices: 'ids', or anything else for local/laptop camera


# generic routine to grab one frame from camera
def get_image():
	if ('ids'== camera_type):
		image, meta = cam.next()
		image = cv2.cvtColor(ref_img, cv2.COLOR_RGB2BGR)
	else:
		ret, image = cap.read()
	return image


#setup camera/video
if ('ids' == camera_type):
	import ids
	cam = ids.Camera()
	cam.color_mode = ids.ids_core.COLOR_RGB8    # Get images in RGB format
	cam.exposure = 5                            # Set initial exposure to 5ms
	cam.auto_exposure = True
	cam.continuous_capture = True               # Start image capture
else:											# use local/laptop camera
	cap = cv2.VideoCapture(0)


ref_img = get_image()
orig_ref = ref_img
result = ref_img 		# useful later


print "Controls:"
print "D = difference image: take reference image & subtract"
print "C = clear settings: clear reference image, reset contrast/brightness"
print "G = toggle grayscale"
print "T = toggle time averaging"
print "I = toggle invert"
print "K = toggle crop (Draw box with mouse first, then press K)"
print "N = toggle de-noising (slow)"
print "Up/Down arrows = more/less contrast"
print "Left/Right arrows = less/more brightness"
print "V = 'music video mode': subtract previous frame"
print "S = save image to espi_image.jpg"
print "R = start/stop recording video to espi_movie.mp4v"
print "Q = quit"

use_diff = True
use_gray = True
use_music_video_mode = False
use_time_avg = False
avg1 = np.float32(ref_img)
use_invert = False
use_denoise = False
use_cropping = False
use_noisy_subtract = False
contrast_alpha = np.array([1.0])
brightness_beta = np.array([0.0])
now_recording = False

# cropping stuff
refPt = []
setting_cropping = False
def click_and_crop(event, x, y, flags, param):
	# grab references to the global variables
	global refPt, cropping

	# if the left mouse button was clicked, record the starting
	# (x, y) coordinates and indicate that cropping specification is being
	# performed
	if event == cv2.EVENT_LBUTTONDOWN:
		refPt = [(x, y)]
		setting_cropping = True

	# check to see if the left mouse button was released
	elif event == cv2.EVENT_LBUTTONUP:
		# record the ending (x, y) coordinates and indicate that
		# the cropping operation is finished
		refPt.append((x, y))
		setting_cropping = False

		# draw a rectangle around the region of interest
		cv2.rectangle(result, refPt[0], refPt[1], (0, 255, 0), 2)
		cv2.imshow("frame", result)

cv2.namedWindow("frame")
cv2.setMouseCallback("frame", click_and_crop)  # register mouse events

while(True):  # Main loop over frames, to take video

	# Capture frame-by-frame
	img = get_image()

	#---------------- Our operations on the frame come here

	# crop first, for speed
	if (use_cropping) and (len(refPt)==2):
		cropped_img = img[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]	
		img = cropped_img	
		if (img.shape[0] < ref_img.shape[0]) and (img.shape[1] < ref_img.shape[1]):
			cropped_ref = ref_img[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
			ref_img = cropped_ref
		if (img.shape[0] < avg1.shape[0]) and (img.shape[1] < avg1.shape[1]):
			avg1 = np.float32(ref_img)

	result = img 

	if (use_diff):
		#safeguard against crashes when un-cropping
		if (img.shape[0] > ref_img.shape[0]) and (img.shape[1] > ref_img.shape[1]):
			ref_img = orig_ref
			avg1 = np.float32(ref_img)

		if (use_noisy_subtract):
			result = img - ref_img 
		else:
			result = cv2.subtract(img, ref_img)

	if (use_time_avg):
		cv2.accumulateWeighted(result,avg1,0.09)
		result = cv2.convertScaleAbs(avg1)

	if (use_gray):
		result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)  # convert to grayscale

	if (use_denoise):
		if (use_gray):
			cv2.fastNlMeansDenoising(result,result,10,7,21)
		else:
			cv2.fastNlMeansDenoisingColored(result,result,10,10,7,21)

	if (use_invert):
		result = (255-result)

	# contrast & brightness
	cv2.multiply(result, contrast_alpha, result)
	cv2.add(result, brightness_beta, result)

	#---- end of image processing operations
	

	# Display the resulting frame

	# if there's a cropping rectangle drawn, keep showing the rectangle
	if ((2==len(refPt)) and (not use_cropping)):
		cv2.rectangle(result, refPt[0], refPt[1], (0, 255, 0), 2)

	cv2.imshow("frame",result)   # show the image on the screen

	if (now_recording):
		if (not use_gray):
			video_out.write(result) 
		else:
			video_out.write(cv2.cvtColor(result, cv2.COLOR_GRAY2BGR))

	# keyboard controls
	key = cv2.waitKey(1) & 0xFF
	#if (key != 255):
	#	print "You pressed key = ",key
	if key == ord('q'):   # quit
		break
	elif key == ord('s'):  # save image
		cv2.imwrite( "espi_image.jpg", result );
	elif key == ord('d'): # diffeence image, replace reference image
		ref_img = img
		use_diff = True
		use_music_video_mode = False 
	elif key == ord('r'):   # record video
		now_recording = not now_recording
		if now_recording:
			print "Starting recording..."
			fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
			video_out = cv2.VideoWriter()
			frame_shape = (img.shape[1],img.shape[0])
			success = video_out.open('espi_movie.mp4v',fourcc, 15.0, frame_shape,True)
		else:
			print "Stopping recording."
			video_out.release()
			video_out = None 
	elif key == ord('c'): # clear settings
		use_diff = False
		use_gray = False
		use_music_video_mode = False
		use_time_avg = False
		avg1 = np.float32(ref_img)
		use_invert = False
		use_denoise = False
		use_cropping = False
		refPt = []
		ref_img = orig_ref
		avg1 = np.float32(ref_img)
		contrast_alpha = np.array([1.0])
		brightness_beta = np.array([0.0])
	elif key == ord('g'): # toggle grayscale
		use_gray = not use_gray
	elif key == ord('v'): # toggle 'cool music video mode'
		use_music_video_mode = not use_music_video_mode
		use_diff = use_music_video_mode
	elif key == ord('i'): # toogle invert
		use_invert = not use_invert
	elif key == ord('t'): # toggle time-averaging
		use_time_avg = not use_time_avg
		if (use_gray):
			avg1 = np.float32( cv2.cvtColor(result, cv2.COLOR_GRAY2BGR) )
		else:
			avg1 = np.float32(result)
	elif key == ord('n'): # toggle denoising (slow)
		use_denoise = not use_denoise
	elif (key == ord('k')) and (2==len(refPt)):  # cropping
		use_cropping = not use_cropping
		if (not use_cropping):
			ref_img = orig_ref
			avg1 = np.float32(ref_img)
	elif key == 0:  # up arrow
		contrast_alpha += 0.1
	elif key == 1:  # down arrow
		contrast_alpha -= 0.1
	elif key == 2:  # left arrow
		brightness_beta -= 5
	elif key == 3:  # right arrow
		brightness_beta += 5
	elif key == ord('p'): # toggle noisy subtraction (default is smooth)
		use_noisy_subtract = not use_noisy_subtract


	
	if (use_music_video_mode):
		ref_img = img 


# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
