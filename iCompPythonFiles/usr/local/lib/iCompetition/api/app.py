###################################################
### START STANDARD IMPORTS
###################################################
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask import request
import sys
import os
import re
import json
import logging
import logging.handlers
###################################################
### END STANDARD IMPORTS
###################################################
###################################################
###################################################
### START ICOMPETITION IMPORTS
###################################################
sys.path.append("/usr/local/lib/iCompetition/python")
sys.path.append("/usr/local/lib/iCompetition/python/crypt")
from credManagement import getCred
from iComp_util import *
from iComp_db import *
from iComp_user import *
from iComp_event import *
from iComp_eventModify import *
from iComp_admin import *
###################################################
### END ICOMPETITION IMPORTS
###################################################
###################################################
###################################################
### START LOGGING CONFIG
###################################################
if not os.path.exists('/var/log/iComp/'):
  os.mkdir('/var/log/iComp/')
apiLog = logging.getLogger('APILOG')
apiLog.setLevel(logging.DEBUG)
logHandler = logging.handlers.RotatingFileHandler('/var/log/iComp/api.log', maxBytes=100000, backupCount=10)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logHandler.setFormatter(formatter)
apiLog.addHandler(logHandler)
###################################################
### END LOGGING CONFIG
###################################################
###################################################
###################################################
### START CONFIG AND PATHING CHECKS
###################################################
#1) PATHING CHECKS
ensureTokenDirsExist()

#2) CONFIG INFO PULL
confDict = getConf()
fl_bonus = int(confDict['fastLapBonusAmount'])

#3) API HOST RUN  VARIABLES
app = Flask(__name__)
CORS(app)
hostIP = '0.0.0.0'
portNum = 5001
###################################################
### END CONFIG AND PATHING CHECKS
###################################################
###################################################
###################################################
### START ICOMPEITION API INIT
###################################################
#1) INITIAL OUTPUT
apiLog.info("Init iCompAPI - iCompetition " + confDict['version'])
apiLog.info("HostIP: " + hostIP)
apiLog.info("HostPort:" + str(portNum))
#2) GIT DATABASE CREDENTIALS
apiLog.info("Gathering DB account information")
roPwd  = idecrypt(getCred("iCompRead"))
altPwd = idecrypt(getCred("iCompAlt"))
#3) CHECK DATABASE SCHEMA VERSION
dbSchema = db_schemaVersion(roPwd)
majorVer = confDict['version'].split('.')[0] + '.' +confDict['version'].split('.')[1]
apiLog.info("DBSchema Version: " + str(dbSchema))
if  majorVer != dbSchema:
  apiLog.error("DB Schema does not match the feature set version of iCompetition.  Please Update DB Schema to version " + majorVer)
  sys.exit(0)
else:
  pass
  apiLog.info("Complete")
  apiLog.info("Starting iCompAPI")
###################################################
### END ICOMPEITION API INIT
###################################################
###################################################
###################################################
### START UTILITY END POINTS
###################################################
@app.route('/iComp/reachable', methods=['GET'])
def apiReachable():
  return json.dumps(
                     {
                       'hello' : True
                     }
                   )

@app.route('/iComp/version', methods=['GET'])
def sendVersionInfo():
  return json.dumps(
                     {
                       'version' : confDict['version']
                     }
                   )
###################################################
### END UTILITY END POINTS
###################################################
###################################################
###################################################
### START AUTHORIZATION END POINTS
###################################################
@app.route('/iComp/auth/checkToken', methods=['POST'])
def authCheckToken():
  token = request.form['token']
  if validateToken(token):
    return json.dumps(
                       {
                         'result':True
                       }
                     )
  else:
    return json.dumps(
                       {
                         'result':False
                       }
                     )


@app.route('/iComp/auth/checkResetToken', methods=['POST'])
def authCheckToken_pwdReset():
  token = request.form['token']
  if validatePwdToken(token):
    return json.dumps(
                       {
                         'result':True
                       }
                     )
  else:
    return json.dumps(
                       {
                         'result':False
                       }
                     )


@app.route('/iComp/auth/adminStatus', methods=['POST'])
def authAdminStatus():
  token = request.form['token']
  un = request.form['un']
  isAdmin = db_authAdminStatus(un, roPwd)
  if validateToken(token) and isAdmin == 1:
    adminToken = generateAdminToken()
    return json.dumps(
                       {
                         'result':True,
                         'adminToken':adminToken
                       }
                     )
  else:
    return json.dumps(
                       {
                         'result':False
                       }
                     )
###################################################
### END AUTHORIZATION END POINTS
###################################################  
################################################### 
###################################################
### START USER ACCOUNT END POINTS
################################################### 
@app.route('/iComp/users/createUser', methods=['POST'])
def createAccount():
  apiLog.info("ACCT CREATE EP")
  uName      = request.form['userName']
  fName      = request.form['firstName']
  lName      = request.form['lastName']
  pwd        = request.form['password']
  email      = request.form['email']
  createAcct = create_iCompAccount(uName,fName,lName,pwd,email,altPwd)
  return json.dumps(
                     {
                       'result'  : createAcct['result'],
                       'message' : createAcct['message']
                     }
                    )

@app.route('/iComp/users/login', methods=['POST'])
def loginUser():
  apiLog.info("USER LOGIN EP")
  u     = request.form['userName']
  p     = dbHasher(request.form['password'])
  login = validate_iCompUser(u,p,roPwd)
  try:
    if login:
      return json.dumps(
                        {
                          'result' : True, 
                          'token'  : login['token']
                        }
                       )
    else:
      return json.dumps(
                        {
                          'result'  : True, 
                          'message' : login['message']
                        }
                       )
  except TypeError:
    return json.dumps(
                      {
                        'result'  : True, 
                        'message' : login['message']
                      }
                     )


@app.route('/iComp/users/getUserInfo', methods=['GET'])
def getUserInfo():
  apiLog.info("GET USER INFO EP")
  parser = request.args
  u        = parser['userName']
  t        = parser['token']
  userInfo = get_iCompUserInfo(u,t,roPwd)

  if not userInfo:
    return False
  else:
    return json.dumps(userInfo)


@app.route('/iComp/users/requestPassReset', methods=['GET'])
def initPasswordEmail():
  apiLog.info("REQUEST PASS RESET EP")
  parser = request.args
  u = parser['userName']
  apiLog.info("password email triggered for user: " + u)
  getUsrEmail = db_initPasswordEmail(u, roPwd)
  token = generatePwdResetToken()
  sendPassResetEmail(getUsrEmail, u, token)
  return "sent"


@app.route('/iComp/users/resetPassword', methods=['POST'])
def resetUserPassword():
  apiLog.info("PASS RESET EP")
  u = request.form['userName']  
  t = request.form['token']
  p = request.form['pw']
  apiLog.info("Password reset init for " + u)
  pwdChg = set_iCompUserPassword(u,p,t,altPwd)
  if pwdChg:
    return json.dumps(
                       {
                          'result' : True
                       }
                     )
  else:
    return json.dumps(
                       {
                          'result' : False
                       }
                     )

@app.route('/iComp/users/changePassword', methods=['POST'])
def changeUserPassword():
  apiLog.info("CHANGE PASSWORD EP")
  userName = request.form['userName']  
  curPass  = request.form['curPass']
  newPass  = request.form['newPass']
  token    = request.form['auth']
  
  if validateToken(token):
    if validate_iCompUser(userName,dbHasher(curPass),roPwd):
      if set_iCompUserPassword(userName,newPass,token,altPwd):
        return json.dumps(
                           { 
                             'success' : True
                           }
                         )
      else:
        return json.dumps(
                          {
                            'success' : False, 
                            'message' : 'Failed to submit password change'
                          }
                         )
    else:
      return json.dumps(
                         {
                           'success': False, 
                           'message' : 'Current password was not valid'
                         }
                       )
  else:
    return json.dumps(
                       {
                         'success': False, 
                         'message' : 'auth token was not valid'
                       }
                     )


@app.route('/iComp/users/changeEmail', methods=['POST'])
def changeUserEmail():
  apiLog.info("CHANGE EMAIL EP")
  userName = request.form['userName']  
  curPass  = request.form['pass']
  newEmail = request.form['newEmail']
  token    = request.form['auth']
  
  if validateToken(token):
    if validate_iCompUser(userName,dbHasher(curPass),roPwd):
      if set_iCompUserEmail(userName,newEmail,token,altPwd):
        return json.dumps(
                          {
                            'success': True
                          }
                         )
      else:
        return json.dumps(
                           {
                             'success': False,
                             'message' : 'Failed to submit email change'
                           }
                         )
    else:
      return json.dumps(
                         {
                           'success': False,
                           'message' : 'Password was not valid'
                         }
                       )
  else:
    return json.dumps(
                       {
                         'success': False,
                         'message' : 'auth token was not valid'
                       }
                     )
###################################################
### END USER ACCOUNT END POINTS
################################################### 
###################################################
###################################################
### START EVENT END POINTS
################################################### 
@app.route('/iComp/events/eventCountCheck', methods=['GET'])
def userHasAnEvent():
  apiLog.info("EVENT COUNT CHECK EP")
  parser = request.args
  u          = parser['userName']
  t          = parser['token']
  eventCount = get_eventCountForUser(u,t,roPwd)
  apiLog.info("event count check occured for " + u)
  if not eventCount or eventCount < 1:
    return json.dumps(
                       {
                         'result' : False
                       }
                     )
  elif eventCount >= 1:
    return json.dumps(
                       {
                         'result' : True,
                         'count'  : eventCount
                       }
                     )

@app.route('/iComp/events/getLiveEvents', methods=['GET'])
def pullLiveEvents():
  apiLog.info("GET LIVE EVENTS EP")
  parser = request.args
  u = parser['userName']
  t = parser['token']
  eventList = get_liveEventHtmlForUser(u,t,roPwd)
  return json.dumps(
                     {
                       'result'  : eventList['result'],
                       'message' : eventList['message'],
                       'html' : eventList['html']
                     }  
                  )
  
@app.route('/iComp/events/getEventCars', methods=['GET'])
def getEventCars():
  apiLog.info("GET EVENT CARS EP")
  parser        = request.args
  num           = parser['eventNum']
  eventCarsHtml = get_carListForEvent(num,roPwd)
  return json.dumps(
                     {
                       'html' : eventCarsHtml
                     }
                   )

@app.route('/iComp/events/registerForEvent', methods=['GET'])
def registerForEvent():
  apiLog.info("EVENT REGISTER EP")
  parser   = request.args
  eventNum = parser['eventNum']
  userName = parser['userName']
  userNum  = parser['userNum']
  car      = parser['car']
  t        = parser['token']
  register = set_iCompUserAsEventParticipant(eventNum,userName,userNum,car,t,altPwd)
  return json.dumps(
                     {
                       'result'  : register['result'],
                       'message' : register['message']
                     }
                   )

@app.route('/iComp/events/pullRegisteredEvents', methods=['GET'])
def pullRegisteredEvents():
  apiLog.info("PULL EVENT REGISTER EP")
  parser = request.args
  u  = parser['userName']
  t = parser['token']
  events = get_registeredEventsForUser(u,0,t,roPwd)
  return json.dumps(
                     {
                       'html' : events['html1'], 
                       'html2' : events['html2']
                     }
                   )

@app.route('/iComp/events/schedule/getUserUnscoredWks', methods=['GET'])
def getEventScheduleWeeks():
  apiLog.info("GET UNSCORED WEEKS EP")
  parser            = request.args
  en                = parser['eventNum']
  u                 = parser['userName']
  unscoredWeeksHtml = get_eventUnscoredWeeksForUser(en,u,roPwd)
  return json.dumps(
                     {
                       'html' : unscoredWeeksHtml
                     }
                   )

@app.route('/iComp/events/logScore', methods=['GET'])
def logScoreForWeek():
  apiLog.info("LOG SCORE EP")
  parser   = request.args
  un       = parser['userNum']
  en       = parser['eventNum']
  wn       = parser['wkNum']
  pos      = parser['pos']
  pnt      = parser['pnt']
  inc      = parser['inc']
  lap      = parser['lap']
  t        = parser['token']
  logScore = set_scoreForUserInEventWeek(un,en,wn,pos,pnt,inc,lap,t,altPwd)
  return json.dumps(
                     {
                       'result' : logScore['result'],
                       'message' : logScore['message']
                     }
                   )  
    
@app.route('/iComp/events/pullDetails', methods=['GET'])
def pullEventDetailInfo():
  apiLog.info("PULL EVENT DETAILS EP")
  parser       = request.args
  un           = parser['userNum']
  en           = parser['eventNum']
  curUn        = parser['currentUserNum']
  eventDetails = get_eventDetailInformation(un,en,curUn,fl_bonus,roPwd)
  return json.dumps(
                     {
                       'schedule'     : eventDetails['scheduleHtml'], 
                       'rankings'     : eventDetails['rankingHtml'], 
                       'eventName'    : eventDetails['eventName'], 
                       'eventSeries'  : eventDetails['eventSeries'], 
                       'driverSelect' : eventDetails['driverSelectHtml']
                     }
                   )

@app.route('/iComp/events/updateEventDisplayTable',methods=['GET'])
def updateEventDisplayTable():
  apiLog.info("UPDATE DISPLAY TABLE EP")
  parser    = request.args
  token     = parser['token']
  which     = parser['display']
  u         = parser['user']
  htmlStr   = update_eventDetailsDisplayTable(u,which,token,roPwd)
  return json.dumps(
                     {
                       'html' : htmlStr
                     }
                   )

@app.route('/iComp/event/modify/getResultsPreModify', methods=['GET'])
def pullResultsPreModify():
  apiLog.info("GET RESULTS PRE MODIFY EP")
  parser     = request.args
  token      = parser['token']
  event      = parser['eventNum']
  user       = parser['userNum']
  week       = parser['week']
  resultInfo = get_preModifiedEventDetails(user,event,week,token,roPwd)
  return json.dumps(resultInfo)

@app.route('/iComp/event/modify/reqChange', methods=['GET'])
def addChangeReq():
  apiLog.info("REQUEST SCORE CHANGE EP")
  parser      = request.args
  token       = parser['token']
  event       = parser['eventNum']
  user        = parser['userNum']
  week        = parser['week']
  pnt         = parser['pnt']
  pos         = parser['pos']
  inc         = parser['inc']
  makeRequest = set_eventWeekModifyTrue(event,user,week,pnt,pos,inc,token,roPwd,altPwd)
  return json.dumps(makeRequest) 
      
@app.route('/iComp/event/modify/getList', methods=['GET'])
def getChangeReq():
  apiLog.info("GET CHANGE REQUEST LIST EP")
  changes = get_changeRequests(roPwd)
  return json.dumps(
                     {
                       'cnt'  : changes['changeCnt'], 
                       'html' : changes['html']
                     }
                   )
      
@app.route('/iComp/event/modify/respond', methods=['POST'])
def appDenyReq():
  auth     = request.form['auth']
  reqNum   = request.form['reqNum']
  appv     = request.form['appv']
  appvDeny = set_changeRequestResponse(reqNum,appv,auth,altPwd)
  return json.dumps(
                     {
                       'success' : appvDeny
                     }
                   )
###################################################
### END EVENT END POINTS
################################################### 
###################################################
###################################################
### START ADMINISTRATION END POINTS
################################################### 
@app.route('/iComp/admin/clearTokens', methods=['POST'])  
def adm_clearTokens():
  auth = request.form['auth']
  if validateAdmToken(auth):
    clearAllTokens()
  return "apiContected"

@app.route('/iComp/admin/listUsers', methods=['POST'])
def adm_listUsers():
  apiLog.info("ADMIN - GET USER LIST EP")
  auth     = request.form['auth']
  userList = get_iCompUserList(auth,roPwd)
  return json.dumps(
                     { 
                       'result' : userList['result'],
                       'cnt'    : userList['userCnt'],
                       'html'   : userList['userListHtml']
                     }
                   )

@app.route('/iComp/admin/listEvents', methods=['POST'])
def adm_listEvents():
  apiLog.info("ADMIN - GET EVENT LIST EP")
  auth      = request.form['auth']
  eventList = get_iCompEventList(auth,roPwd)
  return json.dumps(
                     {
                       'result' : eventList['result'],
                       'cnt'    : eventList['eventCnt'],
                       'html'   : eventList['eventListHtml']
                     }
                   )

@app.route('/iComp/admin/createEvent', methods=['POST'])
def adm_createEvent():
  apiLog.info("ADMIN - CREATE EVENT EP")
  auth         = request.form['auth']
  evName       = request.form['en']
  evSeries     = request.form['es']
  wk1t         = request.form['w1']
  wk2t         = request.form['w2']
  wk3t         = request.form['w3']
  wk4t         = request.form['w4']
  wk5t         = request.form['w5']
  wk6t         = request.form['w6']
  wk7t         = request.form['w7']
  wk8t         = request.form['w8']
  wk9t         = request.form['w9']
  wk10t        = request.form['w10']
  wk11t        = request.form['w11']
  wk12t        = request.form['w12']
  wk13t        = request.form['w13']
  cars         = request.form['cars']
  live         = request.form['live']
  fastLapBonus = request.form['fastLapBonus']
  wkTracks = {
               '1'  : wk1t, 
               '2'  : wk2t, 
               '3'  : wk3t, 
               '4'  : wk4t, 
               '5'  : wk5t, 
               '6'  : wk6t, 
               '7'  : wk7t, 
               '8'  : wk8t, 
               '9'  : wk9t, 
               '10' : wk10t, 
               '11' : wk11t, 
               '12' : wk12t, 
               '13' : wk13t
             }
  createEvent = create_newICompEvent(evName,evSeries,wkTracks,cars,live,fastLapBonus,auth,altPwd)
  return json.dumps(
                     {
                       'result'  : createEvent['result'],
                       'message' : createEvent['message']
                     }
                   )
    
@app.route('/iComp/admin/getUserInfo', methods=['POST'])
def adm_getUserInfo():
  apiLog.info("ADMIN - GET USER INFO EP")
  auth     = request.form['auth']
  userName = request.form['un']
  html = "<tr><th>Col</th><th>Val</th></tr>"
  userInfo = get_iCompUserInformation(userName,auth,roPwd)
  return json.dumps(
                     {
                       'result' : userInfo['result'],
                       'html'   : userInfo['html']
                     }
                   )


@app.route('/iComp/admin/getActiveEvents', methods=['POST'])
def adm_getActiveEvents():
  apiLog.info("ADMIN - GET ACTIVE EVENT INFO EP")
  auth      = request.form['auth']
  eventList = get_activeICompEvents(auth,roPwd)
  return json.dumps(
                     {
                       'result': eventList['result'],
                       'html'  : eventList['html']
                     }
                   )
  
@app.route('/iComp/admin/finishEvent', methods=['POST'])
def adm_finishEvent():
  auth           = request.form['auth']
  eventNum       = request.form['event']
  finishEvent    = set_iCompEventAsFinished(eventNum,fl_bonus,auth,roPwd,altPwd)
  return json.dumps(
                    {
                      'result':finishEvent
                   }
                 )
  
###################################################
### END ADMINISTRATION END POINTS
################################################### 
###################################################
###################################################
### START RUN MAIN
################################################### 
if __name__ == "__main__":
  apiLog.info("Starting iCompAPI In DEV MODE")
  app.run(host=hostIP, port= portNum)
###################################################
### END RUN MAIN
################################################### 