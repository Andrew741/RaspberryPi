import time
import RPi.GPIO as GPIO
from subprocess import call
import string
import smtplib
import picamera
import os
from datetime import datetime
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


TempFileName = '.\Temp.h264'

GPIO.setwarnings (False)
GPIO.setmode (GPIO.BCM)

#pin 24 = motion sensor
GPIO.setup (24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

'''
  This class abstracts some of the Camera functions to an interface
  '''
class PiCamInterface:
  def __init__(self):
    print('setting up the camera')
    self.cam = picamera.PiCamera()
  
  def start_recording(self):
    #self.cam.start_recording(TempFileName)
    print('starting preview')
    self.cam.start_preview()
  def stop_recording(self):
    self.cam.stop_preview()
    #self.cam.stop_recording()



lastMotionTime = 0

motionDetected = False
   
def motion_callback( channel ):
  global motionDetected
  global lastMotionTime
  if motionDetected:
    motionDetected = False
    print ('motion stopped')
  else:
    lastMotionTime = time.time()
    motionDetected = True
    print ('motion started')

GPIO.add_event_detect(24, GPIO.BOTH, callback=motion_callback)

'''
  This class should handle all of the file IO
  '''
class FileHelper:
  
  def __init__(self, theFile):
    self.File = theFile
    print('file helper up and running')
  
  def cvt2mp4(self):
    self.File  = time.strftime("%Y%m%d_%H%M%S") + ".mp4"
    call("MP4Box -add " + TempFileName + self.File , shell = True)
    print(os.path.abspath(self.File))

'''
  This class should handle all of the emailing routines.
  '''
class Emailer:
  
  def __init__(self):
    
    self.msg = MIMEMultipart()
    self.msg['FROM']     = "notifier117@gmail.com"
    self.msg['TO']       = "avgbyron@gmail.com"
    self.msg['SUBJECT']  = "Motion Detected"
    body = "Todo Message Body"
    self.msg.attach(MIMEText(body,'plain'))
    print('Emailer setup')


  def SendEmail(self, file_helper):
    file_helper.cvt2mp4()
    attachment = open(file_helper.File,"rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % file_helper.File)
    msg.attach(part)
      
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(self.msg['FROM'], "GJaolhantians3:16")
    text = msg.as_string()
      
    server.sendmail(self.msg['FROM'] , self.msg['TO'] , text)
    server.quit()




#main body
pci = PiCamInterface()
Filer = FileHelper("./test.py")
Mailer = Emailer()

#state machine variables
'''States = {
  'idle'          : 0,
  'start_capture' : 1,
  'capture'       : 2,
  'stop_capture'  : 3,
  'send_email'	  : 4
}
'''
idle = 0
start_capture = 1
capture = 2
stop_capture = 3
send_email = 4

state = idle #States['idle']


while True:
  localTime = time.time()
    
  # IDLE STATE
  if state == idle: #States['idle']:
    if motionDetected:
      print("Motion Detected")
      state = start_capture #States['start_capture']

  # CAPTURE START
  elif state == start_capture: #States['start_capture']:
    pci.start_recording()
    state = capture #States['capture']

  # CAPTURING
  elif state == capture: #States['capture']:
    if localTime > (lastMotionTime + 5):
      state = stop_capture #States['stop_capture']

  # CAPTURE STOP
  elif state == stop_capture: #States['stop_capture']:
    pci.stop_recording()
    state = send_email #States['send_email']
    
  # SEND EMAIL
  elif state == send_email: #States['send_email']:
    time.sleep(1)
    Mailer.SendEmail(Filer)
    state = idle #States['idle']
    
  time.sleep(0.5)
  print(state)


GPIO.cleanup()
