#!/usr/bin/python3

##Script handles update related functions for iCompetition

##imports
import sys
import os
import logging
import json
import requests
import warnings
sys.path.append("/usr/local/lib/iCompetition/python")
from iComp_util import getConf

##logging
adminFuncLog = logging.getLogger('adminFuncLog')
adminFuncLog.setLevel(logging.DEBUG)
logHandler = logging.handlers.RotatingFileHandler('/var/log/iComp/adminfunctions.log', maxBytes=100000, backupCount=10)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logHandler.setFormatter(formatter)
adminFuncLog.addHandler(logHandler)

##Variables
runningVersion = getConf()['version']