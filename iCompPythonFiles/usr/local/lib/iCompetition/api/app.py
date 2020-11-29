from flask import Flask, jsonify, request
from flask_cors import CORS
from flask import request
import sys
import os
import re
import json
import logging
import logging.handlers
sys.path.append("/usr/local/lib/iCompetition/python")
sys.path.append("/usr/local/lib/iCompetition/python/crypt")
from credManagement import getCred
from iComp_util import *
from iComp_db import *

##Logging config
if not os.path.exists('/var/log/iComp/'):
  os.mkdir('/var/log/iComp/')
apiLog = logging.getLogger('APILOG')
apiLog.setLevel(logging.DEBUG)
logHandler = logging.handlers.RotatingFileHandler('/var/log/iComp/api.log', maxBytes=100000, backupCount=10)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logHandler.setFormatter(formatter)
apiLog.addHandler(logHandler)

##pathing check
ensureTokenDirsExist()

##config setup
confDict = getConf()
fl_bonus = int(confDict['fastLabBonusAmount'])

##Host Run Info Variables
app = Flask(__name__)
CORS(app)
hostIP = '0.0.0.0'
portNum = 5001

apiLog.info("Init iCompAPI - iCompetition " + confDict['version'])
apiLog.info("HostIP: " + hostIP)
apiLog.info("HostPort:" + str(portNum))
apiLog.info("Gathering DB account information")
roPwd = idecrypt(getCred("iCompRead"))
altPwd = idecrypt(getCred("iCompAlt"))

##Schema check
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

"""
Safe Util Endpoints
"""
@app.route('/iComp/reachable', methods=['GET'])
def apiReachable():
  return json.dumps({'hello' : True})

@app.route('/iComp/version', methods=['GET'])
def sendVersionInfo():
  return json.dumps({'version' : confDict['version']})



"""
AUTH ENDPOINTS 
"""
@app.route('/iComp/auth/checkToken', methods=['POST'])
def authCheckToken():
  token = request.form['token']
  if validateToken(token):
    return json.dumps({'result':True})
  else:
    return json.dumps({'result':False})


@app.route('/iComp/auth/checkResetToken', methods=['POST'])
def authCheckToken_pwdReset():
  token = request.form['token']
  if validatePwdToken(token):
    return json.dumps({'result':True})
  else:
    return json.dumps({'result':False})


@app.route('/iComp/auth/adminStatus', methods=['POST'])
def authAdminStatus():
  token = request.form['token']
  un = request.form['un']
  isAdmin = db_authAdminStatus(un, roPwd)
  if validateToken(token) and isAdmin == 1:
    adminToken = generateAdminToken()
    return json.dumps({'result':True, 'adminToken':adminToken})
  else:
    return json.dumps({'result':False})
  
 
""" 
USER ACCOUNT ENDPOINTS
"""

@app.route('/iComp/users/createUser', methods=['POST'])
def createAccount():
  uName = request.form['userName']
  fName = request.form['firstName']
  lName = request.form['lastName']
  pwd   = request.form['password']
  email = request.form['email']
  
  if not iCompUtils_validateEmail(email):
    return json.dumps({'result':False,'message':'Invalid Email Format'})
  
  apiLog.info("Create accout attempt:")
  apiLog.info("\tUN:" + uName)
  apiLog.info("\tFN:" + fName)
  apiLog.info("\tLN:" + lName)
  createUser = db_createAccount(uName,fName,lName,pwd,email,altPwd)
  if not createUser['result']:
    return json.dumps({'result':False,'message':createUser['message']})
  elif createUser['result']:
    return json.dumps({'result':True,'message':createUser['message']})


@app.route('/iComp/users/login', methods=['POST'])
def loginUser():
  u = request.form['userName']
  p = dbHasher(request.form['password'])
  login = db_loginUser(u,p,roPwd)
  try:
    if login:
      apiLog.info("User \'" + u + "\' logged into iComp")
      token = generateToken()
      return json.dumps({'result':True, 'token':token})
    else:
      apiLog.info("User \'" + u + "\' tried logged into iComp")
      return json.dumps({'result':False, 'message':'Username or Password Incorrect'})
  except TypeError:
    return json.dumps({'result':False, 'message':'Username or Password Incorrect'})  


@app.route('/iComp/users/getUserInfo', methods=['GET'])
def getUserInfo():
  parser = request.args
  u = parser['userName']
  t = parser['token']
  if validateToken(t):
    userInfo = db_getUsrInfo(u,roPwd)
    apiLog.info("userMenu refresh occured for " + u)
    return json.dumps(userInfo)
  else:
    return False


@app.route('/iComp/users/requestPassReset', methods=['GET'])
def initPasswordEmail():
  parser = request.args
  u = parser['userName']
  apiLog.info("password email triggered for user: " + u)
  getUsrEmail = db_initPasswordEmail(u, roPwd)
  token = generatePwdResetToken()
  sendPassResetEmail(getUsrEmail, u, token)
  return "sent"


@app.route('/iComp/users/resetPassword', methods=['POST'])
def resetUserPassword():
  u = request.form['userName']  
  t = request.form['token']
  p = request.form['pw']
  apiLog.info("Password reset init for " + u)
  if validatePwdToken(t):
    if db_changePass(p,u,altPwd):
      clearToken(t)
      return json.dumps({'result':True})
    else:
      return json.dumps({'result':False})


@app.route('/iComp/users/changePassword', methods=['POST'])
def changeUserPassword():
  userName = request.form['userName']  
  curPass  = request.form['curPass']
  newPass  = request.form['newPass']
  token    = request.form['auth']
  
  if validateToken(token):
    if db_loginUser(userName,dbHasher(curPass),roPwd):
      if db_changePass(newPass,userName,altPwd):
        return json.dumps({'success': True})
      else:
        return json.dumps({'success': False, 'message' : 'Failed to submit password change'})
    else:
      return json.dumps({'success': False, 'message' : 'Current password was not valid'})
  else:
    return json.dumps({'success': False, 'message' : 'auth token was not valid'})


@app.route('/iComp/users/changeEmail', methods=['POST'])
def changeUserEmail():
  userName = request.form['userName']  
  curPass  = request.form['pass']
  newEmail = request.form['newEmail']
  token    = request.form['auth']
  
  if validateToken(token):
    if db_loginUser(userName,dbHasher(curPass),roPwd):
      if db_changeEmail(newEmail,userName,altPwd):
        return json.dumps({'success': True})
      else:
        return json.dumps({'success': False, 'message' : 'Failed to submit email change'})
    else:
      return json.dumps({'success': False, 'message' : 'Password was not valid'})
  else:
    return json.dumps({'success': False, 'message' : 'auth token was not valid'})

"""
EVENT RELATED ENDPOINTS
"""
@app.route('/iComp/events/eventCountCheck', methods=['GET'])
def userHasAnEvent():
  parser = request.args
  u = parser['userName']
  t = parser['token']
  if validateToken(t):
    evCheck = db_checkIfUserHasEvent(u,roPwd)
    apiLog.info("event count check occured for " + u)
    if len(evCheck) < 1:
      return json.dumps({'result':False})
    else:
      return json.dumps({'result':True})
  else:
    return json.dumps({'result':False})


@app.route('/iComp/events/getLiveEvents', methods=['GET'])
def pullLiveEvents():
  parser = request.args
  u = parser['userName']
  t = parser['token']
  if validateToken(t):  
    apiLog.info("pulling live events to userMenu")
    htmlStr = ""
    eventList = db_getLiveEvents(u,roPwd)  
    if len(eventList) > 0:
      for row in range(len(eventList)):
        name = eventList[row][0]
        num = eventList[row][1]
        htmlStr = htmlStr + "<option value=" + str(num) + ">" + name + "</option>"
        
      return json.dumps({'result' : True, 'message' : 'live events found', 'html' : htmlStr})
    else:
      return json.dumps({'result' : False, 'message' : 'no live events found', 'eventList' : ""})
  else:
    return json.dumps({'result' : False, 'message' : 'invalid auth', 'eventList' : ""})

  
@app.route('/iComp/events/getEventCars', methods=['GET'])
def getEventCars():
  parser = request.args
  num = parser['eventNum']
  apiLog.info("getting cars for event " + str(num))
  htmlStr = ""
  carList = db_getEventCars(num,roPwd)
  for row in range(len(carList)):
    htmlStr = htmlStr + "<option value='" + carList[row][0] + "'>" + carList[row][0] + "</option>"
  return json.dumps({'html' : htmlStr})


@app.route('/iComp/events/registerForEvent', methods=['GET'])
def registerForEvent():
  success  = False
  parser   = request.args
  eventNum = parser['eventNum']
  userName = parser['userName']
  userNum  = parser['userNum']
  car      = parser['car']
  t        = parser['token']
  if validateToken(t):  
    apiLog.info(userName + " is attempting to register for event number " + str(eventNum))
    try:
      db_regForEvent(eventNum,userName,userNum,car,altPwd)
      success = True
      apiLog.info("success")
    except Exception as e:
      apiLog.warning("Failed - Error")
      apiLog.error(str(e))
    return json.dumps({'result' : success})
  else:
    return json.dumps({'result' : False})
    

@app.route('/iComp/events/pullRegisteredEvents', methods=['GET'])
def pullRegisteredEvents():
  parser = request.args
  u  = parser['userName']
  t = parser['token']
  if validateToken(t):    
    apiLog.info("Pulling event list for " + u)
    getEvents = db_getRegisteredEvents(u,0,roPwd)
    htmlStr2 = ""
    htmlStr = '<table class="table" >'
    htmlStr = htmlStr + '<thead class="bg-primary" ><tr>'
    htmlStr = htmlStr + '<th scope="col" >Event Num</th>'
    htmlStr = htmlStr + '<th scope="col" >Event Name</th>'
    htmlStr = htmlStr + '<th scope="col" >iRacing Series</th>'
    htmlStr = htmlStr + '<th scope="col" >Car Used</th>'
    htmlStr = htmlStr + '<th scope="col" >View Details</th>'
    htmlStr = htmlStr + '</tr></thead>'
    htmlStr = htmlStr + '<tbody>'
    for row in range(len(getEvents)):
      htmlStr = htmlStr + '<tr>'
      htmlStr = htmlStr + '<th scope="row">' + str(getEvents[row][0]) + '</th>'
      htmlStr = htmlStr + '<td>' + getEvents[row][1] + '</th>'
      htmlStr = htmlStr + '<td>' + getEvents[row][2] + '</td>'
      htmlStr = htmlStr + '<td>' + getEvents[row][3] + '</td>'
      htmlStr = htmlStr + '<td><button type="button" class="mt-2 btn btn-outline-primary btn-sm w-100" onClick="eventDetail(' + str(getEvents[row][0]) + ');">View Details</button></td>'   
      htmlStr = htmlStr + '</tr>'
      htmlStr2 = htmlStr2 + "<option value='" + str(getEvents[row][0]) + "'>" + getEvents[row][1] + "</option>"
    htmlStr = htmlStr + '</tbody>'
    htmlStr = htmlStr + '</table>'
  
    return json.dumps({'html' : htmlStr, 'html2' : htmlStr2})
  else:
    return json.dumps({'html' : "invalid auth", 'html2' : "invalid auth"})
  

@app.route('/iComp/events/schedule/getUserUnscoredWks', methods=['GET'])
def getEventScheduleWeeks():
  parser = request.args
  en  = parser['eventNum']
  u   = parser['userName']
  un = db_getUsrNum(u,roPwd)
  validWeeks = db_getEventScheduleWeeks(en,un,roPwd)
  htmlStr = ""
  for row in range(len(validWeeks)):
    htmlStr = htmlStr + "<option value='" + str(validWeeks[row][0]) + "'>Week " + str(validWeeks[row][0]) + "</option>"
  
  return json.dumps({'html' : htmlStr})

@app.route('/iComp/events/logScore', methods=['GET'])
def logScoreForWeek():
  parser = request.args
  un  = parser['userNum']
  en  = parser['eventNum']
  wn  = parser['wkNum']
  pos = parser['pos']
  pnt = parser['pnt']
  inc = parser['inc']
  lap = parser['lap']
  t = parser['token']
  if validateToken(t):      
    try:
      if len(lap.split('.')) == 2:
        lap = "0." + lap
      db_logScore(un,en,wn,pos,pnt,inc,lap,altPwd)
      return json.dumps({'result':True})
    except Exception as e:
      return json.dumps({'result':False,'message':str(e)})
  else:
    json.dumps({'result':False,'message': 'invalid auth'})
    

@app.route('/iComp/events/pullDetails', methods=['GET'])
def pullEventDetailInfo():
  parser = request.args
  un  = parser['userNum']
  en  = parser['eventNum']
  curUn = parser['currentUserNum']
  
  ##Get base event info
  eventBaseInfo = db_getEventBaseInfo(en,roPwd)
  
  ##Set FLB enabled/disabled
  fastLapEnabled = False
  if str(eventBaseInfo[2]) == "1":
    fastLapEnabled = True
    
  ##Get and present single user schedule info
  scheduleResults = db_pullScheduleResults(en,un,roPwd)

  ##Pull fast time results here and return list as username,week,fastlap ordered by week
  eventFastLabTimes = db_pullEventFastLaps(en,roPwd)

  scheduleHtml = "<tr>"
  scheduleHtml = scheduleHtml + "<th>Week</th>"
  scheduleHtml = scheduleHtml + "<th>Track</th>"
  scheduleHtml = scheduleHtml + "<th>Position</th>"
  scheduleHtml = scheduleHtml + "<th>Points</th>"
  scheduleHtml = scheduleHtml + "<th>Inc</th>"
  scheduleHtml = scheduleHtml + "<th>Fast Lap</th>"
  scheduleHtml = scheduleHtml + "</tr>"
  droppedWk    = []
  wkScore      = []
  
  for i in range(len(scheduleResults)):
    if str(scheduleResults[i][3]) != '':
      wkScore.append(int(scheduleResults[i][3]))
    
  wkScore.sort(reverse=True)
  if len(wkScore) > 8:
    i = 8
    l = len(wkScore)
    while i < l:
      droppedWk.append(str(wkScore[i]))
      i = i + 1
    
  for row in range(len(scheduleResults)):
    week     = str(scheduleResults[row][0])
    track    = str(scheduleResults[row][1])
    position = str(scheduleResults[row][2])
    points   = str(scheduleResults[row][3])
    inc      = str(scheduleResults[row][4])
    chgReq   = str(scheduleResults[row][5])
    fastLap  = str(scheduleResults[row][6])
    fastLap_reformed = fastLap
    ##check for null fastlap
    if fastLap == "" or fastLap == 0 or fastLap is None:
      fastLap = "X.XX.XXX"
    else:
      pass

    ##check for sub 1.00.000 fastlap
    if fastLap.split('.')[0] == "0":
      fastLap_reformed = fastLap.split('.')[1] + "." + fastLap.split('.')[2]
    else:
      pass

    if points in droppedWk:
      ##HTML for dropped week
      scheduleHtml = scheduleHtml + "<tr class='highlight_grey' >"  
      scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Low score week dropped from total"><i class="fas fa-info-circle"></i></a>  ' + week + '</td>'
      scheduleHtml = scheduleHtml + "<td>" + track    + "</td>"
      if chgReq == '1' and position != '' and un.strip() == curUn.strip(): 
        scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Score modification pending approval"><i class="fas fa-sync"></i></a>  ' + week + '</td>'
      elif position != '' and un.strip() == curUn.strip():
        scheduleHtml = scheduleHtml + '<td><i class="far fa-edit" onClick="startScoreModify(' + en + ',' + un + ',' + week + ');" ></i>  ' + position + '</td>'
      else:
        scheduleHtml = scheduleHtml + '<td>' + position + '</td>'
      scheduleHtml = scheduleHtml + "<td>" + points   + "</td>"
      scheduleHtml = scheduleHtml + "<td>" + inc      + "</td>"
      scheduleHtml = scheduleHtml + "<td>" + fastLap_reformed      + "</td>"
      scheduleHtml = scheduleHtml + "</tr>"    
      del droppedWk[droppedWk.index(points)]
    else:
      ##HTML for counted week
      ## setup for if FLB is enabled, check fastLap against the fast time for week [i]
      if fastLapEnabled and row < len(eventFastLabTimes):
        if fastLap == eventFastLabTimes[row][1]:
          scheduleHtml = scheduleHtml + "<tr class='highlight_green'>"  
          scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Fastest Lap Bonus Applied For This Week"><i class="fas fa-stopwatch"></i></a>  ' + week + '</td>'
          scheduleHtml = scheduleHtml + "<td>" + track    + "</td>"
          if chgReq == '1' and position != '' and un.strip() == curUn.strip(): 
            scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Score modification pending approval"><i class="fas fa-sync"></i></a>  ' + week + '</td>'
          elif position != '' and un.strip() == curUn.strip():
            scheduleHtml = scheduleHtml + '<td><i class="far fa-edit" onClick="startScoreModify(' + en + ',' + un + ',' + week + ');" ></i>  ' + position + '</td>'
          else:
            scheduleHtml = scheduleHtml + '<td>' + position + '</td>'
          scheduleHtml = scheduleHtml + "<td>" + points   + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + inc      + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + fastLap_reformed      + "</td>"
          scheduleHtml = scheduleHtml + "</tr>"  
        else:
          scheduleHtml = scheduleHtml + "<tr>"  
          scheduleHtml = scheduleHtml + "<td>" + week     + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + track    + "</td>"
          if chgReq == '1' and position != '' and un.strip() == curUn.strip(): 
            scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Score modification pending approval"><i class="fas fa-sync"></i></a>  ' + week + '</td>'
          elif position != '' and un.strip() == curUn.strip():
            scheduleHtml = scheduleHtml + '<td><i class="far fa-edit" onClick="startScoreModify(' + en + ',' + un + ',' + week + ');" ></i>  ' + position + '</td>'
          else:
            scheduleHtml = scheduleHtml + '<td>' + position + '</td>'
          scheduleHtml = scheduleHtml + "<td>" + points   + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + inc      + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + fastLap_reformed      + "</td>"
          scheduleHtml = scheduleHtml + "</tr>"  
      else:
        scheduleHtml = scheduleHtml + "<tr>"  
        scheduleHtml = scheduleHtml + "<td>" + week     + "</td>"
        scheduleHtml = scheduleHtml + "<td>" + track    + "</td>"
        if chgReq == '1' and position != '' and un.strip() == curUn.strip(): 
          scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Score modification pending approval"><i class="fas fa-sync"></i></a>  ' + week + '</td>'
        elif position != '' and un.strip() == curUn.strip():
          scheduleHtml = scheduleHtml + '<td><i class="far fa-edit" onClick="startScoreModify(' + en + ',' + un + ',' + week + ');" ></i>  ' + position + '</td>'
        else:
          scheduleHtml = scheduleHtml + '<td>' + position + '</td>'
        scheduleHtml = scheduleHtml + "<td>" + points   + "</td>"
        scheduleHtml = scheduleHtml + "<td>" + inc      + "</td>"
        scheduleHtml = scheduleHtml + "<td>" + fastLap_reformed      + "</td>"
        scheduleHtml = scheduleHtml + "</tr>"          

  ## get and review ranking info
  rankingResults = db_pullEventUserRank(en,roPwd)   
  rankingInfo = [] ##[points][string]
  reviewed = []

###if FLB is enable
## add fastlap to row selection
## compare fast lap tp fast lap list for each week
## if numbers match , add 10 points to tmpPoing.append for the week

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
        userFL = db_pullEventFastLapsForUser(en,userNum,roPwd)
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
    
  rankingHTML = "<tr>"
  rankingHTML = rankingHTML  + "<th>Rank</th>"
  rankingHTML = rankingHTML  + "<th>Driver</th>"
  rankingHTML = rankingHTML  + "<th>Car</th>"
  rankingHTML = rankingHTML  + "<th>Points</th>"
  rankingHTML = rankingHTML  + "</tr>"
  for row in range(len(rankingInfo)):
    points = rankingInfo[row][0]
    driverInfo = rankingInfo[row][1].split('|')
    driver = driverInfo[0] + ' ' + driverInfo[1]
    car    = driverInfo[2]
    rankingHTML = rankingHTML  + "<tr>"
    rankingHTML = rankingHTML  + "<td>" + str(row     + 1) + "</td>"
    rankingHTML = rankingHTML  + "<td>" + driver      + "</td>"
    rankingHTML = rankingHTML  + "<td>" + car         + "</td>"
    rankingHTML = rankingHTML  + "<td>" + str(points) + "</td>"
    rankingHTML = rankingHTML  + "</tr>"

  ##fill user results dropdown
  userSelDropDownHtml = []
  userPar = db_getEventParticipants(en,roPwd)
  for i in range(len(userPar)):
    if str(userPar[i][0]) == un:
      userSelDropDownHtml.append('<option value="' + str(userPar[i][0]) + '">#' + str(userPar[i][0]) + ' - ' + userPar[i][1] + '</option>')
  for i in range(len(userPar)):
    if str(userPar[i][0]) != un:
      userSelDropDownHtml.append('<option value="' + str(userPar[i][0]) + '">#' + str(userPar[i][0]) + ' - ' + userPar[i][1] + '</option>')
      
  return json.dumps({'schedule' : scheduleHtml, 'rankings': rankingHTML, 'eventName':eventBaseInfo[0], 'eventSeries':eventBaseInfo[1], 'driverSelect' : userSelDropDownHtml})


@app.route('/iComp/events/updateEventDisplayTable',methods=['GET'])
def updateEventDisplayTable():
  parser    = request.args
  token     = parser['token']
  which     = parser['display']
  u         = parser['user']
  getEvents = ""
  if validateToken(token):    
    if which == "act":
      apiLog.info("Pulling event list for " + u)
      getEvents = db_getRegisteredEvents(u,0,roPwd)
    elif which == "fin":
      apiLog.info("Pulling event list for " + u)
      getEvents = db_getRegisteredEvents(u,1,roPwd)
      
    htmlStrBase = '''
             <h2 class="mb-1 p-2 border-bottom border-primary text-light bg-dark">EVENTS</h2>
             <select class="mb-1 float-left" id='eventTypeSelect' onChange="changeEventDisplayType();">
             <option value="act">Active Events</option>
             <option value="fin">Finished Events</option>
             </select>
             '''
    htmlStr = '<table class="table" >'
    htmlStr = htmlStr + '<thead class="bg-primary" ><tr>'
    htmlStr = htmlStr + '<th scope="col" >Event Num</th>'
    htmlStr = htmlStr + '<th scope="col" >Event Name</th>'
    htmlStr = htmlStr + '<th scope="col" >iRacing Series</th>'
    htmlStr = htmlStr + '<th scope="col" >Car Used</th>'
    htmlStr = htmlStr + '<th scope="col" >View Details</th>'
    htmlStr = htmlStr + '</tr></thead>'
    htmlStr = htmlStr + '<tbody>'
    for row in range(len(getEvents)):
      htmlStr = htmlStr + '<tr>'
      htmlStr = htmlStr + '<th scope="row">' + str(getEvents[row][0]) + '</th>'
      htmlStr = htmlStr + '<td>' + getEvents[row][1] + '</th>'
      htmlStr = htmlStr + '<td>' + getEvents[row][2] + '</td>'
      htmlStr = htmlStr + '<td>' + getEvents[row][3] + '</td>'
      htmlStr = htmlStr + '<td><button type="button" class="mt-2 btn btn-outline-primary btn-sm w-100" onClick="eventDetail(' + str(getEvents[row][0]) + ');">View Details</button></td>'   
      htmlStr = htmlStr + '</tr>'
    htmlStr = htmlStr + '</tbody>'
    htmlStr = htmlStr + '</table>'

    return json.dumps({'html':htmlStrBase + htmlStr})


@app.route('/iComp/event/modify/getResultsPreModify', methods=['GET'])
def pullResultsPreModify():
  parser = request.args
  token = parser['token']
  event  = parser['eventNum']
  user  = parser['userNum']
  week = parser['week']
  
  if validateToken(token):
    try:
      results = db_getResultsForWeek(event,user,week,roPwd)
      return json.dumps(results)
    except Exception as e:
      apiLog.error(str(e))
      return {'success':False}
  else:
    return {'success':False}


@app.route('/iComp/event/modify/reqChange', methods=['GET'])
def addChangeReq():
  parser = request.args
  token  = parser['token']
  event  = parser['eventNum']
  user   = parser['userNum']
  week   = parser['week']
  pnt    = parser['pnt']
  pos    = parser['pos']
  inc    = parser['inc']

  if validateToken(token):  
    try:
      oldResults = db_getResultsForWeek(event,user,week,roPwd)
      cReq = db_addChangeReqToDB(event,user,week,pnt,pos,inc,oldResults['points'],oldResults['position'],oldResults['inc'],altPwd)
      return json.dumps({"success" : cReq})
    except Exception as e:
      apiLog.error(str(e))
      return {'success':False}
  else:
    return {'success':False}    
      

@app.route('/iComp/event/modify/getList', methods=['GET'])
def getChangeReq():
  rv = {}
  chgList = db_getChgReqList(roPwd)
  if len(chgList) < 1:
    return json.dumps({'cnt' : 0})
  else:
    htmlStr = '<tr> <th>REQ NUM</th> <th>EVT NUM</th> <th>WK NUM</th> <th>USR NUM</th> <th>USR NAME</th> <th>PNT CHG</th> <th>POS CHG</th> <th>INC CHG</th> <th>ACTION</th> </tr>'
    for i in range(len(chgList)):
      htmlStr = htmlStr + '<tr>\n'
      htmlStr = htmlStr + '<td>' + str(chgList[i][0]) + '</td>\n'
      htmlStr = htmlStr + '<td>' + str(chgList[i][9]) + '</td>\n'
      htmlStr = htmlStr + '<td>' + str(chgList[i][10]) + '</td>\n'
      htmlStr = htmlStr + '<td>' + str(chgList[i][1]) + '</td>\n'
      htmlStr = htmlStr + '<td>' + str(chgList[i][2]) + '</td>\n'
      htmlStr = htmlStr + '<td>' + str(chgList[i][3]) + '<i class="fas fa-arrow-right"></i>' + str(chgList[i][6]) + "</td>\n"
      htmlStr = htmlStr + '<td>' + str(chgList[i][4]) + '<i class="fas fa-arrow-right"></i>' + str(chgList[i][7]) + "</td>\n"
      htmlStr = htmlStr + '<td>' + str(chgList[i][5]) + '<i class="fas fa-arrow-right"></i>' + str(chgList[i][8]) + "</td>\n"
      htmlStr = htmlStr + '<td><i class="far fa-check-square mr-2" onClick="actOnChangeChg(' + str(chgList[i][0]) + ',true)"; ></i> <i class="far fa-times-circle mr-2" onClick="actOnChangeChg(' + str(chgList[i][0]) + ',false)"; ></i></td>\n'
      htmlStr = htmlStr + '</tr>\n'
  
  return json.dumps({'cnt' : len(chgList), 'html' : htmlStr})
      

@app.route('/iComp/event/modify/respond', methods=['POST'])
def appDenyReq():
  auth   = request.form['auth']
  reqNum = request.form['reqNum']
  appv   = request.form['appv']
  if validateAdmToken(auth):
    if int(appv) == 0:
      try:
        dbCall = db_approveChgReq(reqNum,altPwd)
        return json.dumps({'success' : dbCall})
      except Exception as e:
        apiLog.error(str(e))
        return json.dumps({'success' : False})
    elif int(appv) == 1:
      try:
        dbCall = db_rejectChgReq(reqNum,altPwd)
        return json.dumps({'success' : dbCall})
      except Exception as e:
        apiLog.error(str(e))
        return json.dumps({'success' : False})  
  else:
    return json.dumps({'success' : False})

"""
Admin Endpoints
"""

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

##Trigger Host - END
if __name__ == "__main__":
  apiLog.info("Starting iCompAPI In DEV MODE")
  app.run(host=hostIP, port= portNum)