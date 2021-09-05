#!/usr/bin/python3

##Script handles update related functions for iCompetition

##imports
import sys
import os
import logging
import json
import requests
import warnings
import argparse
import subprocess
from urllib.request import urlopen
from zipfile import ZipFile

sys.path.append("/usr/local/lib/iCompetition/python")
from iComp_util import getConf
from iComp_util import list_iCompVersionsInGit

##Supress Warning(s)
warnings.filterwarnings('ignore','InsecureRequestWarning')

##logging
adminFuncLog = logging.getLogger('adminFuncLog')
adminFuncLog.setLevel(logging.DEBUG)
logHandler = logging.handlers.RotatingFileHandler('/var/log/iComp/adminfunctions.log', maxBytes=100000, backupCount=10)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logHandler.setFormatter(formatter)
adminFuncLog.addHandler(logHandler)

##Variables
currentVersion = getConf['version']
downloadDir    = '/tmp/iCompetition_updates/'
devnull        = open(os.devnull, 'w')

def getParms():
  parser = argparse.ArgumentParser(description='iCompetition Update Script.')
  parser.add_argument('-l','--list',action='store_true',default=False,help='List available iCompetition versions')
  parser.add_argument('-v','--version',default='NONE',help='New iCompetition version to update to')
  return parser.parse_args()


def list_gitVersions():
  gitVersions = list_iCompVersionsInGit()
  sys.stdout.write('\nAvaliable iCompetition Versions:\n')
  for i in range(len(gitVersions)):
    if gitVersions[i].strip() == currentVersion.strip():
      sys.stdout.write('\t- ' + gitVersions[i] + ' << Your Version\n')
    else:
      sys.stdout.write('\t- ' + gitVersions[i] + '\n')
  
  sys.stdout.write('\n')


def check_versionIsValid(version):
  avaVers = list_iCompVersionsInGit()
  if version.strip() in avaVers:
    return True
  else:
    return False


def download_versionZip(downloadVersion):
  '''
  Directory will be places at:
  /tmp/iCompetition_updates/iCompetition_<version>/iCompetition_App-iCompetition_<version>
  '''
  try:
    os.makedirs(downloadDir + 'iCompetition_' + downloadVersion,0o777)
    zipDownload = urlopen('https://github.com/iCompetition/iCompetition_App/archive/refs/tags/iCompetition_' + '.zip')
    tempZip     = open(downloadDir + '/iCompetition_' + downloadVersion + '.zip', "wb")
    tempZip     = tempZip.write(zipDownload.read())
    tempZip.close()
    zipFile     = ZipFile(downloadDir + '/iCompetition_' + downloadVersion + '.zip')
    zipFile.extractall(path=downloadDir + 'iCompetition_' + downloadVersion)
    zipFile.close()
    if os.path.exists(downloadDir + 'iCompetition_' + downloadVersion):
      return True
    else:
      return False
  except Exception as e:
    adminFuncLog.error("Failed to download new verion")
    adminFuncLog.error(str(e))
    return False


def copy_applicationFiles(downloadVersion):
  pythonPathDownload  = downloadDir + 'iCompetition_' + downloadVersion + 'iCompPythonFiles/usr/local/lib/iCompetition/python/'
  apiPathDownload     = downloadDir + 'iCompetition_' + downloadVersion + 'iCompPythonFiles/usr/local/lib/iCompetition/api/'
  webPathDownload     = downloadDir + 'iCompetition_' + downloadVersion + 'iCompWebFiles/etc/apache2/sites-available/'
  webConfPathDownload = downloadDir + 'iCompetition_' + downloadVersion + 'iCompWebFiles/var/www/iCompetition/'
  profilePathDownload = downloadDir + 'iCompetition_' + downloadVersion + 'iCompSystemFiles/etc/profile.d/'
  sysdPathDownload    = downloadDir + 'iCompetition_' + downloadVersion + 'iCompSystemFiles/etc/systemd/'
  pythonAppPathBase   = '/usr/local/lib/iCompetition/'
  WebAppPathBase      = '/var/www/iCompetition/'
  apacheConfDirect    = '/etc/apache2/sites-available'
  iCompConfDirect     = '/etc/iCompetition/'
  profileDirect       = '/etc/profile.d/'
  sysdDirect          = '/etc/systemd/system/'


  



def main():
  parms = getParms
  if parms.list or parms.version == 'NONE':
    list_gitVersions()
  elif parms.version != 'NONE':
    if check_versionIsValid(parms.verion):
      sys.stdout.write("Given version invalid\n")
    else:
      perform_updateToNewVersion(parms.version)




if __name__ == '__main__':
  def main()





