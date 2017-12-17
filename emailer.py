from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

'''
  This class should handle all of the emailing routines.
'''
class Emailer:
  
  def __init__(self, bodyMsg = ''):
    self.msg = MIMEMultipart()
    
    with (r'~/Config/Email.txt', 'r') as configFile:
      Configuration = configFile.readlines()
      [self.fromAdd,self.fromPwd] = Configuration[1]
      self.toAdd = Configuration[2]
      self.msg['FROM']     = self.fromAdd
      self.msg['TO']       = self.toAdd
    self.msg['SUBJECT']  = "Motion Detected"
    body = bodyMsg
    self.msg.attach(MIMEText(body,'plain'))
    print('Emailer setup')
  
  
  def SendEmail(self, file_path):
    attachment = open(file_path,"rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % file_path)
    self.msg.attach(part)
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(self.msg['FROM'], self.fromPwd)
    text = self.msg.as_string()
    
    server.sendmail(self.msg['FROM'] , self.msg['TO'] , text)
    server.quit()
    print('email success')
