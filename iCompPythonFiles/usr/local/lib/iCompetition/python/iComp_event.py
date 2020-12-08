##########
##Event functions for iComp
##########

##Standard Imports
import sys
import logging

##iCompImports
from iComp_db import *
from iComp_util import *

##logging
apiLog = logging.getLogger('APILOG')
apiLog.setLevel(logging.DEBUG)
logHandler = logging.handlers.RotatingFileHandler('/var/log/iComp/api.log', maxBytes=100000, backupCount=10)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logHandler.setFormatter(formatter)
apiLog.addHandler(logHandler)

##Functions
def get_eventCountForUser(username,token,roPwd):
  """
  Get the number of events that a user is registered for
  INPUT
    username/string - iComp account user name
    token/string    - authorization token
  OUTPUT
    eventCnt/int    - number events account is registered for
  """
  apiLog.info("get_iCompUserEventCount - checking auth token")
  if not validateToken(token):
    apiLog.info("get_iCompUserEventCount - token invalid or expired")
    return False
  else:
    eventList = db_getLiveEvents(username,roPwd) 
    return len(eventList)


def get_liveEventHtmlForUser(username,token,roPwd):
  """
  Gets information about the live events that a user can registered for
  INPUT
    username/string - iComp account user name
    token/string    - authorization token
  OUTPUT
    dictonary
      result/boolean  - success of function
      html/string     - event details in html
      message/string  - information about call

  """
  htmlStr = ""  
  apiLog.info("get_liveEventHtmlForUser - checking auth token")
  if not validateToken(token):
    apiLog.info("get_liveEventHtmlForUser - invalid or expired token")
    apiLog.warning("get_liveEventHtmlForUser - live event information pull was attempted for " + username + " using an invalid token")
    return {
             'result'  : False,
             'message' : "invalid or expired auth token.  Please log back in to iCompeition",
             'html'    : ""
           }
  else:
    apiLog.info("get_liveEventHtmlForUser - pulling live event information")
    eventList = db_getLiveEvents(username,roPwd) 
    if len(eventList) > 0:
      apiLog.info("get_liveEventHtmlForUser - building html for " + username)
      for row in range(len(eventList)):
        name = eventList[row][0]
        num  = eventList[row][1]
        htmlStr = htmlStr + "<option value=" + str(num) + ">" + name + "</option>"
      return {
               'result'  : True,
               'message' : "live eventlist pulled successfully",
               'html'    : htmlStr
             }
    else:
      return {
               'result'  : False,
               'message' : "no live events found for user",
               'html'    : htmlStr
             }


def get_carListForEvent(eventNum,roPwd):
  """
  Get the cars for a given event
  INPUT
    eventNum/int   - iComp event number
  OUTPUT
    htmlStr/string - html output for event cars list
  """
  htmlStr = ""
  apiLog.info("get_carListForEvent - pulling cars for event #" + str(eventNum))
  carList = db_getEventCars(eventNum,roPwd)
  for row in range(len(carList)):
    htmlStr = htmlStr + "<option value='" + carList[row][0] + "'>" + carList[row][0] + "</option>"  
  return htmlStr


def get_registeredEventsForUser(username,runningOrFinished,token,roPwd):
  """
  pull the events a user is registered for
  INPUT
    username/string       - iComp account name
    runningOrFinished/int - pull events that are currrently active or marked as finished 
      0 = running
      1 = finished
    token/string           - auth token
  OUTPUT
    dictionary
      html1/String         - eventInfo in html
      html2/String         - option menu html
  """
  htmlStr  = ""
  htmlStr2 = ""
  if not validateToken(token):
    apiLog.info("get_registeredEventsForUser - invalid or expired token")
    return {
             'html1' : 'invalid auth',
             'html2' : 'invalid auth'
           } 
  else:
    eventList = db_getRegisteredEvents(username,runningOrFinished,roPwd)
    apiLog.info("get_registeredEventsForUser - building html")
    htmlStr = '<table class="table" >'
    htmlStr = htmlStr + '<thead class="bg-primary" ><tr>'
    htmlStr = htmlStr + '<th scope="col" >Event Num</th>'
    htmlStr = htmlStr + '<th scope="col" >Event Name</th>'
    htmlStr = htmlStr + '<th scope="col" >iRacing Series</th>'
    htmlStr = htmlStr + '<th scope="col" >Car Used</th>'
    htmlStr = htmlStr + '<th scope="col" >View Details</th>'
    htmlStr = htmlStr + '</tr></thead>'
    htmlStr = htmlStr + '<tbody>'    
    for row in range(len(eventList)):
      htmlStr = htmlStr + '<tr>'
      htmlStr = htmlStr + '<th scope="row">' + str(eventList[row][0]) + '</th>'
      htmlStr = htmlStr + '<td>' + eventList[row][1] + '</th>'
      htmlStr = htmlStr + '<td>' + eventList[row][2] + '</td>'
      htmlStr = htmlStr + '<td>' + eventList[row][3] + '</td>'
      htmlStr = htmlStr + '<td><button type="button" class="mt-2 btn btn-outline-primary btn-sm w-100" onClick="eventDetail(' + str(getEvents[row][0]) + ');">View Details</button></td>'   
      htmlStr = htmlStr + '</tr>'
      htmlStr2 = htmlStr2 + "<option value='" + str(eventList[row][0]) + "'>" + eventList[row][1] + "</option>"
    htmlStr = htmlStr + '</tbody>'
    htmlStr = htmlStr + '</table>'
    
    return {
             'html1' : htmlStr,
             'html2' : htmlStr2
           }


def get_eventUnscoredWeeksForUser(eventNum,userName,roPwd):
  """
  get the weeks a user still can log a score for an event
  INPUT
    eventNum/int    - iComp event number
    username/string - iComp account name
  OUTPUT
    htmlStr/string  - html for week logging list
  """
  htmlStr = ""
  apiLog.info("get_eventUnscoredWeeksForUser - getting unscored weeks for " + userName)
  unscoredWeeks = db_getEventScheduleWeeks(eventNum,userNum,roPwd)
  apiLog.info("get_eventUnscoredWeeksForUser - generating HTML")
  for row in range(len(unscoredWeeks)):
    htmlStr = htmlStr + "<option value='" + str(unscoredWeeks[row][0]) + "'>Week " + str(unscoredWeeks[row][0]) + "</option>"
  return htmlStr


def set_iCompUserAsEventParticipant(eventNum,userName,userNum,car,token,altPwd):
  """
  Set a user as registered for an event
  INPUT
    eventNum/string - event number
    userName/string - iComp account name
    userNum/string  - iComp account number
    car/string      - car used for event
    token/string    - auth token
  OUTPUT
    dictonary
      result/boolean - function success
      message/string - function result message
  """
  apiLog.info("set_iCompUserAsEventParticipant - checking auth token")
  if not validateToken(token):
    apiLog.info("set_iCompUserAsEventParticipant - invalid or expired token")
    apiLog.warning("set_iCompUserAsEventParticipant - someone tried to register " + userName + " to an event with an invalid token")
    return {
             'result'  : False,
             'message' : 'invalid auth token'
           } 
  else:
    try:
      db_regForEvent(eventNum,userName,userNum,car,altPwd)
      apiLog.info("set_iCompUserAsEventParticipant - " + userName + " registered for event #" + str(eventNum))
      return {
                'result'  : True,
                'message' : 'event register was successful'
             }
    except Exception as e:
      apiLog.error("set_iCompUserAsEventParticipant - exception occured during event registration")
      apiLog.error(str(e))
      return {
                'result'  : False,
                'message' : 'ERROR - ' + str(e)
             }    


def set_scoreForUserInEventWeek(userNum,eventNum,weekNum,position,points,incidents,fastLapTime,token,altPwd):
  """
  Log a user score for an event week
  INPUTS
    userNum/int         - iComp account user number
    eventNum/int        - iComp event number
    weekNum/int         - week of event
    position/int        - finish position for week
    points/int          - points earned for week
    incidents/int       - incidents for week
    fastLapTime/string  - fastest lap for the week (x.xx.xx)
    token/string        - auth token
  OUTPUT
    dictionary
      result/boolean     - function success
      message/string     - function success message
  """
  apiLog.info("set_scoreForUserInEventWeek - checking auth token")
  if not validateToken(token):
    apiLog.info("set_scoreForUserInEventWeek - invalid or expired token")
    apiLog.warning("set_scoreForUserInEventWeek - someone log score for " + userName + " to an event with an invalid token")
    return {
             'result'  : False,
             'message' : 'invalid auth'
           } 
  else:
    apiLog.info("set_scoreForUserInEventWeek - attempting to log score for " + userName)
    apiLog.info("event: "     + str(eventNum))
    apiLog.info("week: "      + str(weekNum))
    apiLog.info("fin pos: "   + str(position))
    apiLog.info("points: "    + str(points))
    apiLog.info("inc count: " + str(incidents))
    apiLog.info("fast lap: "  + str(fastLapTime))
    try:
      if len(fastLapTime.split('.')) == 2:
        fastLapTime = "0." + fastLapTime
      logScore = db_logScore(userNum,eventNum,weekNum,position,points,incidents,fastLapTime,altPwd)
      return {
               'result'  : True,
               'message' : 'Week result logged successfully'
             }
    except Exception as e:
      apiLog.error("set_scoreForUserInEventWeek - an exception occured while attempting to log a week score")
      apiLog.error("set_scoreForUserInEventWeek - ERROR: " + str(e))
      return {
               'result'  : False,
               'message' : 'ERROR: ' + str(e)
             }