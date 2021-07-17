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
  parser.add_argument('user',help="iCompAlt/iCompRead")
  parser.add_argument('password',help="New password to store")
  return parser.parse_args()


def alterPass(user,password):
  try:
    pwd = iencrypt(password)
    fh = open('/etc/iCompetition/.creds/.' + user,'wb')
    fh.write(pwd)
    fh.close() 
    return True
  except:
    return False


def main():
  parms   = getArguments()
  passChg = alterPass(parms.user,parms.password)
  if passChg:
    sys.stdout.write("Pass change complete.  if iCompetition is running, it will need to be restarted.")
  else:
    sys.stdout.write("Pass change failed")


if __name__ == '__main__':
  main()






