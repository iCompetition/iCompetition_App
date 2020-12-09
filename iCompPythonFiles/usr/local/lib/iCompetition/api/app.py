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
fl_bonus = int(confDict['fastLabBonusAmount'])

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
if  majorVer > dbSchema:
  apiLog.error("DB Schema is too low for this version of iCompetition.  Please Update DB Schema to at least version " + majorVer)
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
                       'result'  : createAcct['results'],
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
  register = set_iCompUserAsEventParticipant(eventNum,userName,userNum,car,token,altPwd)
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
@app.route('/iComp/admin/listUsers', methods=['POST'])
def adm_listUsers():
  auth = request.form['auth']
  
  if validateAdmToken(auth):
    userList = db_listUsers(roPwd)
    userCount = len(userList)
    html = "<tr><th>UserName</th><th>UserNum</th></tr>"
    for row in range(len(userList)):
      html = html + "<tr><td>" + userList[row][0] + "</td><td>" + str(userList[row][1]) + "</td></tr>"
    
    return json.dumps({'result':True,'cnt':str(userCount),'html':html})
  else:
    return json.dumps({'result':False})
    

@app.route('/iComp/admin/listEvents', methods=['POST'])
def adm_listEvents():
  auth = request.form['auth']
  
  if validateAdmToken(auth):
    eventList = db_listEvents(roPwd)
    eventCnt  = len(eventList)
    html = """
            <tr>
              <th>Event</th>
              <th>Series</th>
              <th>EventNum</th>
              <th>isLive?</th>
            </tr>
           """
    for row in range(len(eventList)):
      html = html + """
                      <tr>
                        <td>""" + eventList[row][0]      + """</td>
                        <td>""" + eventList[row][1]      + """</td>
                        <td>""" + str(eventList[row][2]) + """</td>
                        <td>""" + str(eventList[row][3]) + """</td>
                      </tr>
                    """
    
    return json.dumps({'result':True,'cnt':str(eventCnt),'html':html})
  else:
    return json.dumps({'result':False})


@app.route('/iComp/admin/createEvent', methods=['POST'])
def adm_createEvent():
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
  w13 = False
  if validateAdmToken(auth):
    if wk13t.lower() != "norace":
      w13 = True
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
    try:
      db_createEvent(evName,evSeries,wkTracks,w13,cars,live,altPwd,fastLapBonus)
      return json.dumps({'result':True})
    except Exception as e:
      return json.dumps({'result':False,'message':str(e)})    

    
@app.route('/iComp/admin/clearTokens', methods=['POST'])  
def adm_clearTokens():
  auth = request.form['auth']
  if validateAdmToken(auth):
    clearAllTokens()
  return "apiContected"
  

@app.route('/iComp/admin/getUserInfo', methods=['POST'])
def adm_getUserInfo():
  auth     = request.form['auth']
  userName = request.form['un']
  html = "<tr><th>Col</th><th>Val</th></tr>"
  if validateAdmToken(auth):
    userInfo = db_getUserInfoForAdmin(userName,roPwd)
    html = html + "<tr><td>USERNAME:</td><td>" + str(userInfo['userName']) + "</td></tr>"
    html = html + "<tr><td>USERNUM:</td><td>"  + str(userInfo['userNum']) + "</td></tr>"
    html = html + "<tr><td>FULLNAME:</td><td>" + str(userInfo['name']) + "</td></tr>"
    html = html + "<tr><td>EMAIL:</td><td>"    + str(userInfo['email']) + "</td></tr>"
    html = html + "<tr><td>ISADMIN:</td><td>"  + str(userInfo['isAdm']) + "</td></tr>"
    html = html + "<tr><td>EVENTCNT:</td><td>" + str(userInfo['eventCount']) + "</td></tr>"
    return json.dumps({'result':True,'html':html})
  else:
    return json.dumps({'result':False})


@app.route('/iComp/admin/getActiveEvents', methods=['POST'])
def adm_getActiveEvents():
  auth = request.form['auth']
  if validateAdmToken(auth):
    eventList = db_listEvents_active(roPwd)
    html = """
            <tr>
              <th>Event</th>
              <th>EventNum</th>
              <th>Finish</th>
            </tr>
           """
    for row in range(len(eventList)):
      html = html + """
                      <tr>
                        <td>""" + str(eventList[row][0])      + """</td>
                        <td>""" + str(eventList[row][1])      + """</td>
                        <td>""" + """<button type=\"submit\" class=\"mt-2 mb-3 btn btn-outline-primary btn-lg w-100\" onClick=\"adm_finishEvent('""" + str(eventList[row][1]) + """');\" >Finish</button> """ + """</td>
                      </tr>
                    """
    
    return json.dumps({'result':True,'html':html})
  else:
    return json.dumps({'result':False})    


@app.route('/iComp/admin/finishEvent', methods=['POST'])
def adm_finishEvent():
  auth           = request.form['auth']
  eventNum       = request.form['event']
  rankingResults = db_pullEventUserRank(eventNum,roPwd)
  rankingInfo    = []
  reviewed       = []
  eventBaseInfo = db_getEventBaseInfo(eventNum,roPwd)
  ##Set FLB enabled/disabled
  fastLapEnabled = False
  if str(eventBaseInfo[2]) == "1":
    fastLapEnabled = True
  
  for row in range(len(rankingResults)):
    tmpPoints  = []
    bonus      = 0
    userNum    = rankingResults[row][0]
    userFirst  = rankingResults[row][1]
    userLast   = rankingResults[row][2]
    userCar    = rankingResults[row][3]
    fastLap    = rankingResults[row][6]
    if userNum not in reviewed:
      reviewed.append(userNum)
      for row2 in range(len(rankingResults)):
        if rankingResults[row2][0] == userNum:
          tmpPoints.append(rankingResults[row2][4])
      tmpPoints.sort()
      if len(tmpPoints) == 13:
        del tmpPoints[:5]
      elif len(tmpPoints) == 12:
        del tmpPoints[:4]
      elif len(tmpPoints) == 11:
        del tmpPoints[:3]
      elif len(tmpPoints) == 10:
        del tmpPoints[:2]
      elif len(tmpPoints) == 9:
        del tmpPoints[:1]
      else:
        pass

      if fastLapEnabled:
        bonus = 0
        userFL = db_pullEventFastLapsForUser(eventNum,userNum,roPwd)
        for i in range(len(eventFastLabTimes)):
          for j in range(len(userFL)):
            try:
              if eventFastLabTimes[i][1] == userFL[i][1]:
                if i < 9:
                  bonus = bonus + fl_bonus
                  break
                else:
                  pass
            except IndexError:
              pass

  pointSum = sum(tmpPoints) + bonus
  rankingInfo.append([pointSum,userFirst + "|" + userLast + "|" + userCar])
  rankingInfo.sort(reverse=True)
  driverInfo = rankingInfo[0][1].split('|')
  driver = driverInfo[0] + ' ' + driverInfo[1]

  if validateAdmToken(auth):  
    finishEvent = db_finishEvent(eventNum, userNum, driver, altPwd)
    return json.dumps({'result':finishEvent})
  else:
    return json.dumps({'result':False})
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