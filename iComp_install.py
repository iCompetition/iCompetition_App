#!/usr/lib/python3

#####installer for iCompetition
#####Requires root

##Imports
import os
import sys
import getpass
import errno

##Variables
dirsToCreate = [
               '/usr/local/lib/iCompetition/api',
               '/usr/local/lib/iCompetition/python',
               '/usr/local/lib/iCompetition/python/crypt',
               '/usr/local/lib/iCompetition/.tokens',
               '/usr/local/lib/iCompetition/.tokens/.adm',
               '/usr/local/lib/iCompetition/.tokens/.pwd',
               '/etc/iCompetition/.creds',
               '/var/www/iCompetition/css',
               '/var/www/iCompetition/js',
               '/var/www/iCompetition/images'
               ]

def CheckPrereq():
    #Check python version
    sys.stdout.write("Checking iComp prereqs...\n\n")
    sys.stdout.write("Python version meets requirements...")
    if sys.version_info[0] < 3:
        sys.stdout.write("FALSE\n\n")
        sys.stdout.write("iComp Requires Version 3 or higher\n\n")
    
    
    ##check user
    if getpass.getuser() == 'root':
        pass
    else:
        sys.stdout.write("\nroot user is required\n")
        sys.exit()



##Make directories
try:
    os.makedirs('/usr/local/lib/iCompetition/api')
except OSError, err:
    if err.errno != errno.EEXIST or not os.path.isdir(newdir): 
      raise    

