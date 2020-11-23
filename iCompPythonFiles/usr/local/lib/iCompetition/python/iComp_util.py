##Util Functions used by iCompAPI

import re
import smtplib
import random
import string
import datetime
import os
from os.path import isfile,join
import subprocess
import hashlib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from simplecrypt import encrypt, decrypt


##Variables
tokenPath = "/usr/local/lib/iCompetition/.tokens/"
lock = "icomp"
token_ttl    = 3000
admToken_ttl = 10
pwdToken_ttl = 15

##RE Test Cases
emailTestCase = "[\w\.][\w\d\.]+@[\w][\w\d]+\.[\w\d]{2,}"


def getConf():
  confDir = []

  fh = open("/etc/iCompetition/iComp.conf",'r')
  tmp = fh.readlines()
  fh.close()

  for i in range(len(tmp)):
    conf[tmp[i].split(':')[0].strip()] = tmp[i].split(':')[2].strip()
  
  return confDir



##valuidate email addr
def iCompUtils_validateEmail(email):
  testCase = re.compile(emailTestCase)
  if testCase.match(email):
    return True
  else:
    return False


##password reset email
def sendPassResetEmail(email, userName, token):
  mail_content = """
                 <html><head></head>
                   <body>
                    <p>You have requested to reset your password for iCompetition for UserName: """ + userName + """.
                       Click the link below to reset. </p>
                       <p><a href='https://toastysilverfish.site:8002/resetPass.html?userName=""" + userName + """&validation=""" + token + """' >Reset Password</a></p>
                   </body>
                 </html>
                 """                       
  sendEmail = "noReply.iComp@gmail.com"
  sendPass = "UNKtMS5fWrm6gvnpGQfI"
  message = MIMEMultipart()
  message['From'] = sendEmail
  message['To']   = email
  message['Subject'] = "iCompetition Password Change Request"
  message.attach(MIMEText(mail_content, 'html'))
  session = smtplib.SMTP('smtp.gmail.com', 587)
  session.starttls()
  session.login(sendEmail, sendPass)
  text = message.as_string()
  session.sendmail(sendEmail, email, text)
  session.quit()


##Token functions
def generateToken():
  chars = string.ascii_letters + string.digits
  token = ''.join((random.choice(chars) for i in range(24)))
  expire = (datetime.datetime.now() + datetime.timedelta(minutes=token_ttl)).strftime("%m%d%Y%H%M")
  fh = open(tokenPath + token,'w')
  fh.write(expire)
  fh.close()
  return token


def generateAdminToken():
  chars = string.ascii_letters + string.digits
  token = ''.join((random.choice(chars) for i in range(24)))
  expire = (datetime.datetime.now() + datetime.timedelta(minutes=admToken_ttl)).strftime("%m%d%Y%H%M")
  fh = open(tokenPath + ".adm/" + token,'w')
  fh.write(expire)
  fh.close()
  return token


def generatePwdResetToken():
  chars = string.ascii_letters + string.digits
  token = ''.join((random.choice(chars) for i in range(24)))
  expire = (datetime.datetime.now() + datetime.timedelta(minutes=pwdToken_ttl)).strftime("%m%d%Y%H%M")
  fh = open(tokenPath + ".pwd/" + token,'w')
  fh.write(expire)
  fh.close()
  return token


def validateToken(token):
  path = tokenPath + token
  curTime = datetime.datetime.now().strftime("%m%d%Y%H%M")
  if not os.path.exists(path):
    return False
  else:
    fh = open(path,'r')
    tokenExpire = fh.read()
    fh.close()
    if curTime >= tokenExpire:
      os.remove(path)
      return False
    else:
      return True


def validateAdmToken(token):
  path = tokenPath + ".adm/" + token
  curTime = datetime.datetime.now().strftime("%m%d%Y%H%M")
  if not os.path.exists(path):
    return False
  else:
    fh = open(path,'r')
    tokenExpire = fh.read()
    fh.close()
    if curTime >= tokenExpire:
      os.remove(path)
      return False
    else:
      return True


def validatePwdToken(token):
  path = tokenPath + ".pwd/" + token
  curTime = datetime.datetime.now().strftime("%m%d%Y%H%M")
  if not os.path.exists(path):
    return False
  else:
    fh = open(path,'r')
    tokenExpire = fh.read()
    fh.close()
    if curTime >= tokenExpire:
      os.remove(path)
      return False
    else:
      return True


def clearToken(token):
  curTime = datetime.datetime.now().strftime("%m%d%Y%H%M")
  if not os.path.exists(tokenPath + token):
    if not os.path.exists(tokenPath + ".adm/adm_" + token):
      if not os.path.exists(tokenPath + ".pwd/" + token):
        return True
      else:
        os.remove(tokenPath + ".pwd/" + token)
        return False
    else:
      os.remove(tokenPath + ".adm/adm_" + token)
      return False
  else:
    os.remove(tokenPath + token)
    return False


def clearAllTokens():
  call = subprocess.call("rm " + tokenPath + "*",shell=True)
  call = subprocess.call("rm " + tokenPath + ".adm/*",shell=True)
  call = subprocess.call("rm " + tokenPath + ".pwd/*",shell=True)


def ensureTokenDirsExist():
  if os.path.exists(tokenPath):
    pass
  else:
    os.makedirs(tokenPath)
  if os.path.exists(tokenPath + ".adm/"):
    pass
  else:
    os.makedirs(tokenPath + ".adm/")
  if os.path.exists(tokenPath + ".pwd/"):
    pass
  else:
    os.makedirs(tokenPath + ".pwd/")    


##crypt functions
def iencrypt(pwd):
  return encrypt(lock, pwd)


def idecrypt(pwd):
  return decrypt(lock, pwd).decode('utf-8')


def dbHasher(pwd):
  return hashlib.md5(pwd.encode('utf-8')).hexdigest()


##others
def getVersionInformation():
  vFileMatch = "^v\d{1,2}_\d{2,3}_\d{2,3}\.txt"
  pyDir      = "/usr/local/lib/iCompetition/python"
  apiDir     = "/usr/local/lib/iCompetition/api"
  webDir     = "/var/www/iCompetition"
  rv         = {}
  
  #python
  pyFiles = [f for f in os.listdir(pyDir) if isfile(join(pyDir,f))]  
  for i in range(len(pyFiles)):
    if re.match(vFileMatch,pyFiles[i]):
      tmp = pyFiles[i].split('.')[0]
      versionNum = tmp.split('_')[0] + '.' + tmp.split('_')[1] + '.' + tmp.split('_')[2]
      rv['python'] = versionNum
      break

  #api
  apiFiles = [f for f in os.listdir(pyDir) if isfile(join(pyDir,f))]  
  for i in range(len(apiFiles)):
    if re.match(vFileMatch,apiFiles[i]):
      tmp = apiFiles[i].split('.')[0]
      versionNum = tmp.split('_')[0] + '.' + tmp.split('_')[1] + '.' + tmp.split('_')[2]
      rv['api'] = versionNum
      break
  
  #web
  webFiles = [f for f in os.listdir(pyDir) if isfile(join(pyDir,f))]  
  for i in range(len(webFiles)):
    if re.match(vFileMatch,webFiles[i]):
      tmp = webFiles[i].split('.')[0]
      versionNum = tmp.split('_')[0] + '.' + tmp.split('_')[1] + '.' + tmp.split('_')[2]
      rv['presentation'] = versionNum
      break  

  return rv
  
  