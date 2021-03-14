#!/usr/bin/python3

##allows assignment of admin rights to iComp user

import argparse
import sys
import pymysql
import logging
import logging.handlers
sys.path.append("/usr/local/lib/iCompetition/python")
sys.path.append("/usr/local/lib/iCompetition/python/crypt")
from credManagement import *
from iComp_util import getConf

outFmt1 = "\n{}\n\n"

##logging
adminFuncLog = logging.getLogger('adminFuncLog')
adminFuncLog.setLevel(logging.DEBUG)
logHandler = logging.handlers.RotatingFileHandler('/var/log/iComp/adminfunctions.log', maxBytes=100000, backupCount=10)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logHandler.setFormatter(formatter)
adminFuncLog.addHandler(logHandler)

def getArguments():
  parser = parser = argparse.ArgumentParser(description='Grant user admin rights for icompetition')
  parser.add_argument('action',help="grant/revoke")
  parser.add_argument('-t','--type',help="type of admin permission: full, approve")
  parser.add_argument('-u','--userNum',help="User Number to give/take")
  return parser.parse_args()


def getDBInfo():
  conf     = getConf()
  dbName   = conf['database_name']
  dbIp     = conf['database_location']  
  userName = 'iCompAlt'
  userPass = idecrypt(getCred("iCompAlt"))
  return   {
             'name' : dbName,
             'ip'   : dbIp,
             'user' : userName,
             'pass' : userPass
           }


def grantAdmin(pTypeStr,dbInfo,userNum):
  db = pymysql.connect(dbInfo['ip'],dbInfo['user'],dbInfo['pass'],dbInfo['name'],autocommit=True)  
  cr = db.cursor()
  pType = 0

  if pTypeStr.upper() == "FULL":
    pType = 1
  elif pTypeStr.upper() == "APPROVE":
    pType = 2
  else:
    sys.stdout.write(outFmt1.format(pType + " is not a valid admin type"))
    sys.exit()

  try:
    cr.execute("select userName from users where userNum = " + str(userNum))
    result = cr.fetchall()
    if len(result) != 1:
      sys.stdout.write(outFmt1.format("userNum " + str(userNum) + " does not exist."))
      sys.exit()
  except Exception as e:
    sys.stdout.write(outFmt1.format("An error occured: \n" + str(e)))
    sys.exit()
  
  try:
    cr.execute("update users set admin = " + str(pType) + " where userNum = " + str(userNum))
    cr.execute("select userName from users where admin = 1 and userNum = " + str(userNum))
    if len(result) != 1:
      sys.stdout.write(outFmt1.format("Failed to grant admin rights to user"))
      sys.exit()    
    else:
      sys.stdout.write(outFmt1.format(result[0][0] + " has been granted " + pTypeStr + " admin privileges"))  
      adminFuncLog.info("CLI - " + pTypeStr + " admin rights have been given to userNum " + str(userNum))
  except Exception as e:
    sys.stdout.write(outFmt1.format("An error occured: \n" + str(e)))
    sys.exit()      


def revokeAdmin(dbInfo,userNum):
  db = pymysql.connect(dbInfo['ip'],dbInfo['user'],dbInfo['pass'],dbInfo['name'],autocommit=True)  
  cr = db.cursor()

  try:
    cr.execute("select userName from users where userNum = " + str(userNum))
    result = cr.fetchall()
    if len(result) != 1:
      sys.stdout.write(outFmt1.format("userNum " + str(userNum) + " does not exist."))
      sys.exit()
  except Exception as e:
    sys.stdout.write(outFmt1.format("An error occured: \n" + str(e)))
    sys.exit()
  
  try:
    cr.execute("update users set admin = 0 where userNum = " + str(userNum))
    cr.execute("select userName from users where admin = 0 and userNum = " + str(userNum))
    if len(result) != 1:
      sys.stdout.write(outFmt1.format("Failed to revoke admin rights to user"))
      sys.exit()    
    else:
      sys.stdout.write(outFmt1.format(result[0][0] + " has had admin privileges removed"))  
      adminFuncLog.info("CLI - admin rights have been revoked from userNum " + str(userNum))
  except Exception as e:
    sys.stdout.write(outFmt1.format("An error occured: \n" + str(e)))
    sys.exit()        


def main():
  parms  = getArguments()
  dbInfo = getDBInfo()

  if (parms.action).upper() == "GRANT":
    grantAdmin(parms.type,dbInfo,parms.userNum)
  elif (parms.action).upper() == "REVOKE":
    revokeAdmin(dbInfo,parms.userNum)
  else:
    sys.stdout.write(outFmt1.format(parms.action + " is not a valid action"))


if __name__ == '__main__':
  main()






