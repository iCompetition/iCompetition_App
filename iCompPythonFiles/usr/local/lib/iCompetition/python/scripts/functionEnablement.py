#!/usr/bin/python3

##enablement/disablement of iCompetition functions

import argparse
import os
import sys
import logging
import logging.handlers

##static variables
validActions   = ['enable','disable','status']

##logging
adminFuncLog = logging.getLogger('adminFuncLog')
adminFuncLog.setLevel(logging.DEBUG)
logHandler = logging.handlers.RotatingFileHandler('/var/log/iComp/adminfunctions.log', maxBytes=100000, backupCount=10)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logHandler.setFormatter(formatter)
adminFuncLog.addHandler(logHandler)

def getArguments():
  parser = parser = argparse.ArgumentParser(description='Enable/disable iCompetition Functions')
  parser.add_argument('action',help="enable/disable/status")
  parser.add_argument('function',help="adminweb")
  return parser.parse_args()


def adminMainWebPage(action):
  ##handles the availability of the admin.html
  if action.lower() == 'status':
    if os.path.exists('/var/www/iCompetition/admin.html'):
      sys.stdout.write("enabled\n")
    else:
      sys.stdout.write("disabled\n")
  elif action.lower() == 'enable':
    if os.path.exists('/var/www/iCompetition/admin.html'):
      sys.stdout.write("already enabled\n")
    else:
      adminFuncLog.info("Attempting to enable admin.html")
      try:
        os.popen('cp /usr/local/lib/iCompetition/templateHold/admin.html /var/www/iCompetition/admin.html')
        adminFuncLog.info("admin.html was enabled")
        sys.stdout.write("enabled\n")
      except Exception as e:
        adminFuncLog.info("admin.html enable was attempted but failed")
        adminFuncLog.error(str(e))
        sys.stdout.write("failed to enable\n")
        sys.stdout.write(str(e) + "\n")
  elif action.lower() == 'disable':
    if not os.path.exists('/var/www/iCompetition/admin.html'):
      sys.stdout.write("already disabled\n")    
    else:
      adminFuncLog.info("Attempting to disable admin.html")
      try:
        os.remove('/var/www/iCompetition/admin.html')
        adminFuncLog.info("admin.html was disabled")
        sys.stdout.write("disabled\n")        
      except Exception as e:
        adminFuncLog.info("admin.html disable was attempted but failed")
        adminFuncLog.error(str(e))
        sys.stdout.write("failed to disable\n")
        sys.stdout.write(str(e) + "\n")


def maintenanceWeb(action):
  ##handles the availability of the index.html
  if action.lower() == "status":
    if os.path.exists('/var/www/iCompetition/maint.txt'):
      sys.stdout.write("enabled\n")
    else:
      sys.stdout.write("disabled\n")
  elif action.lower() == "enable":
    if os.path.exists('/var/www/iCompetition/maint.txt'):
      sys.stdout.write("already enabled\n")
    else:
      try:
        os.popen('cp /usr/local/lib/iCompetition/templateHold/index_maintenance.html /var/www/iCompetition/index.html')
        os.popen('cp /usr/local/lib/iCompetition/templateHold/index_maintenance.html /var/www/iCompetition/maint.txt')
        adminFuncLog.info("web maintence mode has been enabled\n")
        sys.stdout.write("enabled\n")
      except Exception as e:
        adminFuncLog.info("there was an attempt to enable web maintence mode, but it failed\n")
        adminFuncLog.error(str(e))
        sys.stdout.write("failed to enable\n")
        sys.stdout.write(str(e) + "\n")
  elif action.lower() == "disable":
    if os.path.exists('/var/www/iCompetition/maint.txt'):
      try:
        os.remove('/var/www/iCompetition/maint.txt')
        os.popen('cp /usr/local/lib/iCompetition/templateHold/index.html /var/www/iCompetition/index.html')
        adminFuncLog.info("web maintence mode has been disabled\n")
        sys.stdout.write("disabled\n")        
      except Exception as e:
        adminFuncLog.info("there was an attempt to disable web maintence mode, but it failed\n")
        adminFuncLog.error(str(e))
        sys.stdout.write("failed to disable\n")
        sys.stdout.write(str(e) + "\n")        


def main():
  parms = getArguments()
  if (parms.action).lower() in validActions:
    pass
  else:
    sys.stdout.write(parms.action + " is not a valid action\n")
    sys.exit()

  if (parms.function).lower() == 'adminweb':
    adminMainWebPage((parms.action).lower())
  elif (parms.function).lower() == 'maintenanceweb':
    maintenanceWeb((parms.action).lower())
  else:
    sys.stdout.write((parms.function).lower() + " is not a valid function\n")
  

if __name__ == '__main__':
  main()