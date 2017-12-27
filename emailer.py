from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

'''
  This class should handle all of the emailing routines.
'''
class Emailer:
  
  def __init__(self, subject ='', bodyMsg = ''):
    self.msg = MIMEMultipart()
    self.setup = 'Complete'
    try:
      with open(r'./Config/Email.txt', 'r') as configFile:
        Configuration = configFile.readlines()
        #print(Configuration)
        [self.fromAdd,self.fromPwd] = Configuration[1].split()
        self.toAdd = Configuration[2].strip()
        self.msg['FROM']     = self.fromAdd
        self.msg['TO']       = self.toAdd
        self.msg['SUBJECT']  = subject
        body = bodyMsg
        self.msg.attach(MIMEText(body,'plain'))
  
    Except:
        self.setup = 'Incomplete'
    print(self.setup)
  
  def SendEmail(self, file_path):
    self.Email_Status = 'Unsuccessful'
    if self.setup == 'Complete':
      try:
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
        self.setup = 'Succesful'
      
      Except:
        print('Hit an exception sending the email')
      print(self.setup)
