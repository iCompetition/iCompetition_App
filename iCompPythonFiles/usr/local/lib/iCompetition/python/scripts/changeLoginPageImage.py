#!/usr/bin/python3

import argparse
import sys
import os
import os.path
import shutil
from datetime import datetime

def getArguments():
  parser = parser = argparse.ArgumentParser(description='Changes image for login page')
  parser.add_argument('imagePath',help="path to image or default")
  parser.add_argument('-d','--deleteOld',action="store_true",help="delete existing image.  false by deault",)
  return parser.parse_args()


def changeImage(path,deleteOld):
  timestamp = datetime.now().strftime("%m%d%Y%H%M")
  if not deleteOld:
    shutil.copy("/var/www/iCompetition/images/loginPageImage", "/var/www/iCompetition/images/loginPageImageOld_" + timestamp)
    sys.stdout.write("\nold image saved to /var/www/iCompetition/images/loginPageImageOld_" + timestamp + "\n")

  shutil.copy(path,"/var/www/iCompetition/images/loginPageImage")


def checkExists(path):
  if os.path.exists(path):
    return True
  else:
    return False


def main():
  parms = getArguments()
  if not checkExists:
    sys.stdout.write("\nprovided filepath does not exist")
    sys.exit()
  else:
    if (parms.imagePath).upper() == "DEFAULT":
      changeImage("/var/www/iCompetition/images/defaultImage/loginPageImageDefault.jpg",parms.deleteOld)
      sys.stdout.write("\nimage reset to default...\n\n")
    else:
      changeImage(parms.imagePath,parms.deleteOld)
      sys.stdout.write("\nimage has been changed...\n\n")


if __name__ == '__main__':
  main()