import time
from subprocess import call
import os
from datetime import datetime
from os.path import basename



'''
  This class should handle all of the file IO
  '''
class FileHelper:
  
  def __init__(self):

    print('file helper up and running')
  
  def cvt2mp4(self):
    with open(time.strftime("%Y%m%d_%H%M%S") + ".mp4", 'w') as outFile:
      print(outFile.name)
      call("MP4Box -add " + "./temp.h264" + outFile.name , shell = True)
      return outFile.name



