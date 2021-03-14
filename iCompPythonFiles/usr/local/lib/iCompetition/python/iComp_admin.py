##########
##admin functions for iComp
##########

##Standard Imports
import sys
import logging

##iCompImports
from iComp_db import *
from iComp_util import *

##logging
adminFuncLog = logging.getLogger('adminFuncLog')
adminFuncLog.setLevel(logging.DEBUG)
logHandler = logging.handlers.RotatingFileHandler('/var/log/iComp/adminfunctions.log', maxBytes=100000, backupCount=10)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logHandler.setFormatter(formatter)
adminFuncLog.addHandler(logHandler)

##Functions
def get_iCompUserList(admToken,roPwd):
  """
  Pull the list of iCompUsers
  INPUT
    admToken/string - admin auth token
  OUTPUT
    dictionary
      result/boolean      - function result
      userCount/int       - total count of users
      userListHtml/string - html for populating user list
  """
  userListHtml = ""
  adminFuncLog.info("get_iCompUserList - checking auth token")
  if not validateAdmToken(admToken):
    adminFuncLog.warning("get_iCompUserList - invalid auth token used!")
    adminFuncLog.warning("get_iCompUserList - invalid or expired admin token used to pull user list")
    return {
             'result'       : False,
             'userCnt'      : 0,
             'userListHtml' : "invalid token"
           }    
  else:
    adminFuncLog.info("get_iCompUserList - checking auth token")
    userList     = db_listUsers(roPwd)
    userCount    = len(userList)
    userListHtml = "<tr><th>UserName</th><th>UserNum</th></tr>"
    for row in range(len(userList)):
      userListHtml = userListHtml + "<tr><td>" + userList[row][0] + "</td><td>" + str(userList[row][1]) + "</td></tr>"  
  
    return {
             'result'       : True,
             'userCnt'      : userCount,
             'userListHtml' : userListHtml
           }


def get_iCompEventList(admToken,roPwd):
  """
  Pull the list of iComp Events
  INPUT
    admToken/string - admin auth token
  OUTPUT
    dictionary
      result/boolean       - function result
      eventCnt/int        - total count of users
      eventListHtml/string - html for populating user list
  """
  adminFuncLog.info("get_iCompEventList - checking auth token")
  if not validateAdmToken(admToken):
    adminFuncLog.warning("get_iCompEventList - invalid auth token used!")
    adminFuncLog.warning("get_iCompEventList - invalid or expired admin token used to pull user list")
    return {
             'result'       : False,
             'eventCnt'      : 0,
             'eventListHtml' : "invalid token"
           }    
  else:
    adminFuncLog.info("get_iCompEventList - pulling event list")
    eventList = db_listEvents(roPwd)
    eventCnt  = len(eventList)
    adminFuncLog.info("get_iCompEventList - generating html")
    eventListHtml = """
                     <tr>
                       <th>Event</th>
                       <th>Series</th>
                       <th>EventNum</th>
                       <th>isLive?</th>
                     </tr>
                    """
    for row in range(len(eventList)):
      eventListHtml = eventListHtml + """
                                       <tr>
                                         <td>""" + eventList[row][0]      + """</td>
                                         <td>""" + eventList[row][1]      + """</td>
                                         <td>""" + str(eventList[row][2]) + """</td>
                                         <td>""" + str(eventList[row][3]) + """</td>
                                       </tr>
                                     """    
    return {
             'result'        : True,
             'eventCnt'       : eventCnt,
             'eventListHtml' : eventListHtml
           }        


def get_iCompUserInformation(userName,token,roPwd):
  """
  pulls info for user
  INTPUT
    userName/string - iComp account name
    token/string    - auth token for adm
  OUTPUT
    dictionary
      result/boolean - function success
      html           - html for user info to display
  """
  adminFuncLog.info("get_iCompUserInformation - validating token")
  if validateAdmToken(token):
    adminFuncLog.info("get_iCompUserInformation - pulling info for account: " + userName)
    userInfo = db_getUserInfoForAdmin(userName,roPwd)
    adminFuncLog.info("get_iCompUserInformation - building html")
    html = "<tr><th>Col</th><th>Val</th></tr>"
    html = html + "<tr><td>USERNAME:</td><td>" + str(userInfo['userName']) + "</td></tr>"
    html = html + "<tr><td>USERNUM:</td><td>"  + str(userInfo['userNum']) + "</td></tr>"
    html = html + "<tr><td>FULLNAME:</td><td>" + str(userInfo['name']) + "</td></tr>"
    html = html + "<tr><td>EMAIL:</td><td>"    + str(userInfo['email']) + "</td></tr>"
    html = html + "<tr><td>ISADMIN:</td><td>"  + str(userInfo['isAdm']) + "</td></tr>"
    html = html + "<tr><td>EVENTCNT:</td><td>" + str(userInfo['eventCount']) + "</td></tr>"
    return {
            'result' : True,
            'html'   : html
           }
  else:
    adminFuncLog.warning("get_iCompUserInformation - invalid auth token used!")
    adminFuncLog.warning("get_iCompUserInformation - invalid or expired admin token used to pull user info")
    return {
            'result' : False,
            'html'   : "invalid auth"
           }


def get_activeICompEvents(token,roPwd):
  """
  Get list of currently active iComp events
    INPUT
      token/string - adm auth token
    OUTPUT
      dictionary
        result/boolean - function success
        html/string    - list html to display
  """
  adminFuncLog.info("get_activeICompEvents - validating token")
  if not validateAdmToken(token):
    adminFuncLog.warning("get_activeICompEvents - invalid auth token used!")
    adminFuncLog.warning("get_activeICompEvents - invalid or expired admin token used to pull active event info")
    return {
            'result' : False,
            'html'   : "invalid auth"
           }
  else:
    adminFuncLog.info("get_activeICompEvents - pulling event list")
    eventList = db_listEvents_active(roPwd)
    adminFuncLog.info("get_activeICompEvents - building html")
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
    return {
             'result' : True,
             'html'   : html
           }    


def create_newICompEvent(eventName,eventSeries,weekTracks,cars,isLive,FLB_enabled,HCB_enabled,admToken,altPwd):
  """
  add a new iComp event to database
  INPUT
    eventName/string   - iComp event name
    eventSeries/string - associated iRacing series
    weekTracks/dict    - keys 1-13 for tracks for each week in series
    cars/list          - cars available in series
    isLive/int         - set event live or disabled (0/1)
    FLB_enabled/int    - set FLB enabled (0/1)
    HCB_enabled/int    - set HCB enabled (0/1)
    admToken/string    - auth token
  OUTPUT
    dictionary
      result/boolean   - function success
      message/string   - message for function success
  """
  w13 = False
  adminFuncLog.info("create_newICompEvent - checking auth token")
  if not validateAdmToken(admToken):
    adminFuncLog.warning("create_newICompEvent - invalid auth token used!")
    adminFuncLog.warning("create_newICompEvent - invalid or expired admin token used to create new event!")  
    return { 
             'result'  : False,
             'message' : "invalid or expired token used"
           }
  else:
    try:
      db_createEvent(eventName,eventSeries,weekTracks,w13,cars,isLive,altPwd,FLB_enabled, HCB_enabled) 
      return { 
               'result'  : True,
               'message' : "Event Created"
             }      
    except Exception as e:
      adminFuncLog.error("create_newICompEvent - en error occured creating event")                                 
      adminFuncLog.error("create_newICompEvent - ERROR: " + str(e))        
      return { 
               'result'  : False,
               'message' : "ERROR: " + str(e)
             }                               


def set_iCompEventAsFinished(eventNum,fl_bonus,token,roPwd,altPwd):
  """
  Set an iComp event as finished
  INPUT
    eventNum/int - iComp event number
    fl_bonus/int - bonus points for fast labs
    token/string - adm auth token
  OUTPUT
    result/boolean - function success
  """
  adminFuncLog.info("set_iCompEventAsFinished - validating auth token")
  if not validateAdmToken(token):
    adminFuncLog.warning("set_iCompEventAsFinished - invalid auth token used!")
    adminFuncLog.warning("set_iCompEventAsFinished - invalid or expired admin token used to finish event!")  
    return False,
  else:
    rankingResults    = db_pullEventUserRank(eventNum,roPwd)
    rankingInfo       = []
    reviewed          = []
    eventBaseInfo     = db_getEventBaseInfo(eventNum,roPwd)
    eventFastLabTimes = db_pullEventFastLaps(eventNum,roPwd)
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
  
        pointSum    = sum(tmpPoints) + bonus
        rankingInfo.append([pointSum,userFirst + "|" + userLast + "|" + userCar])

    rankingInfo.sort(reverse=True)
    driverInfo  = rankingInfo[0][1].split('|')
    driver      = driverInfo[0] + ' ' + driverInfo[1]
    finishEvent = db_finishEvent(eventNum, userNum, driver, altPwd)
    return finishEvent
