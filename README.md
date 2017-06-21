# image-capture-opencv
Python (v2) utility for image capture, frame subtraction, (e.g. for ESPI)


Capture realtime frames from camera, perform reference frame subtraction
Intended for use with ESPI experiment at Belmont university

## Requirements:
 * OpenCV, can be installed via `pip install opencv-python`. 
 * (optional) IDS camera kit: https://github.com/ncsuarc/ids

## Running:
Run `python2 capture.py`

Controls are pretty rudimentary; they are single-key keyboard commands, entered either in the terminal window or in the image window:

      D = difference image: take reference image & subtract
      C = clear settings: clear reference image, reset contrast/brightness
      G = toggle grayscale
      T = toggle time averaging
      I = toggle invert
      K = toggle crop (Draw box with mouse first, then press K)
      N = toggle de-noising (slow)
      Up/Down arrows = more/less contrast
      Left/Right arrows = less/more brightness
      V = 'music video mode': subtract previous frame
      S = save image to espi_image.jpg
      R = start/stop recording video to espi_movie.mp4v
      Q = quit

I invite pull requests with improved (e.g. GUI) controls, and/or any other improvements! 

<hr>
Code taken from the following tutorials...

  * Built from Tutorial "Getting Started with Videos": http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_gui/py_video_display/py_video_display.html
  *  Time-averaging tutorial: https://opencvpython.blogspot.com/2012/07/background-extraction-using-running.html

  * De-noising: http://docs.opencv.org/master/d5/d69/tutorial_py_non_local_means.html#gsc.tab=0

  * Cropping: http://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/

  * Contrast/brightness contols: http://docs.opencv.org/2.4/doc/tutorials/core/basic_linear_transform/basic_linear_transform.html
