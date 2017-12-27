import time
import RPi.GPIO as GPIO
from subprocess import call
import string
import picamera
import os
from datetime import datetime
from os.path import basename
import emailer
import Cvt2Mp4



'''
  Variables visible to the whole file.
'''
lastMotionTime = 0      # timestamp of the last time motion was detected
motionDetected = False  # Boolean to keep track of state

# Broadcom pin IDs
MOTION_PIN    = 24
LED_POWER_PIN = 23
TempFileName = './temp.h264' # always save to this file

GPIO.setwarnings (False)
GPIO.setmode (GPIO.BCM)

#           PIN NUMBER      IN/OUT    Pull up or pull down resistor
GPIO.setup (MOTION_PIN,     GPIO.IN,  pull_up_down=GPIO.PUD_DOWN)
GPIO.setup (LED_POWER_PIN,  GPIO.OUT)



'''
This function gets called when either a rising edge or falling edge of the signal on the motion detector pin occurs.

The motion detector puts out 3.3V onto the motion detector pin whenever there is motion detected.

3.3V            -------------
               |             |
0.0V ----------              --------------
(no motion)      (motion)

It keeps track of the motion with the motionDetected variable, and switches it accordingly. It also saves off the system time of the last time that we got motion.
'''

def motion_callback( channel ):
  # Not great to use globals, but since this is an interrupt it's the only option.
  # In general, the only thing that interrupts should do is change a couple variables and then return. Don't call any functions or do  a ton of stuff in there or you can miss other important events.
  global motionDetected
  global lastMotionTime
  
  if motionDetected:
    motionDetected = False
  else:
    lastMotionTime = time.time()
    motionDetected = True


GPIO.add_event_detect(MOTION_PIN, GPIO.BOTH, callback=motion_callback)


#main body
PiCam = picamera.PiCamera()
Filer = Cvt2Mp4.FileHelper()
Mailer = emailer.Emailer()
Filer = Cvt2Mp4.FileHelper()

#state machine variables
'''States = {
  'idle'          : 0,
  'start_capture' : 1,
  'capture'       : 2,
  'stop_capture'  : 3,
  'send_email'	  : 4
  }
  '''
idle          = 0
start_capture = 1
capture       = 2
stop_capture  = 3
send_email    = 4

state = idle #States['idle']

TodoList = list()

TodoList.append(' Test the LED: Solution is to assemble')
TodoList.append(' Save off mp4s and .h264s to usb stick: Solution is to keep this script on the drive')
TodoList.append(' Live stream the view camera view')
TodoList.append(' Setup an ad hoc network to run this from: Warning, this will negate the email notifications (which is okay)')
TodoList.append(' Set up a cron job to email a summary once a day, with a number of videos recorded. Maybe have the cronjob do the count of mp4 files and send email')

for item in TodoList:
  print(item)


while True:
  localTime = time.time()

  # IDLE STATE
  if state == idle: #States['idle']:
    if motionDetected:
      print("Motion Detected")
      state = start_capture #States['start_capture']

  # CAPTURE START
  elif state == start_capture: #States['start_capture']:
    # turn on the LED so we can see
    GPIO.output(LED_POWER_PIN, GPIO.HIGH)
    PiCam.start_recording(TempFileName)
    state = capture #States['capture']
  
  # CAPTURING
  elif state == capture: #States['capture']:
    if localTime > (lastMotionTime + 10):
      state = stop_capture #States['stop_capture']

  # CAPTURE STOP
  elif state == stop_capture: #States['stop_capture']:
    PiCam.stop_recording()
    GPIO.output(LED_POWER_PIN, GPIO.LOW)
    state = send_email #States['send_email']
  
  # SEND EMAIL
  elif state == send_email: #States['send_email']:
    theMp4 = Filer.cvt2mp4()
    if not theMp4 == 'Error':
      Mailer.SendEmail(theMp4)
    state = idle #States['idle']

  time.sleep(0.5)
  print(state)


GPIO.cleanup()
