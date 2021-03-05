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
eventFuncLog = logging.getLogger('eventFuncLog')
eventFuncLog.setLevel(logging.DEBUG)
logHandler = logging.handlers.RotatingFileHandler('/var/log/iComp/eventFunctions.log', maxBytes=100000, backupCount=10)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logHandler.setFormatter(formatter)
eventFuncLog.addHandler(logHandler)

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
  eventFuncLog.info("get_iCompUserEventCount - checking auth token")
  if not validateToken(token):
    eventFuncLog.info("get_iCompUserEventCount - token invalid or expired")
    return False
  else:
    eventList = db_getRegisteredEvents(username,0,roPwd) 
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
  eventFuncLog.info("get_liveEventHtmlForUser - checking auth token")
  if not validateToken(token):
    eventFuncLog.info("get_liveEventHtmlForUser - invalid or expired token")
    eventFuncLog.warning("get_liveEventHtmlForUser - live event information pull was attempted for " + username + " using an invalid token")
    return {
             'result'  : False,
             'message' : "invalid or expired auth token.  Please log back in to iCompeition",
             'html'    : ""
           }
  else:
    eventFuncLog.info("get_liveEventHtmlForUser - pulling live event information")
    eventList = db_getLiveEvents(username,roPwd) 
    if len(eventList) > 0:
      eventFuncLog.info("get_liveEventHtmlForUser - building html for " + username)
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
  eventFuncLog.info("get_carListForEvent - pulling cars for event #" + str(eventNum))
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
    eventFuncLog.info("get_registeredEventsForUser - invalid or expired token")
    return {
             'html1' : 'invalid auth',
             'html2' : 'invalid auth'
           } 
  else:
    eventList = db_getRegisteredEvents(username,runningOrFinished,roPwd)
    eventFuncLog.info("get_registeredEventsForUser - building html")
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
      htmlStr = htmlStr + '<td><button type="button" class="mt-2 btn btn-outline-primary btn-sm w-100" onClick="eventDetail(' + str(eventList[row][0]) + ');">View Details</button></td>'   
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
  eventFuncLog.info("get_eventUnscoredWeeksForUser - getting unscored weeks for " + userName)
  userNum = db_getUsrNum(userName,roPwd)
  unscoredWeeks = db_getEventScheduleWeeks(eventNum,userNum,roPwd)
  eventFuncLog.info("get_eventUnscoredWeeksForUser - generating HTML")
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
  eventFuncLog.info("set_iCompUserAsEventParticipant - checking auth token")
  if not validateToken(token):
    eventFuncLog.info("set_iCompUserAsEventParticipant - invalid or expired token")
    eventFuncLog.warning("set_iCompUserAsEventParticipant - someone tried to register " + userName + " to an event with an invalid token")
    return {
             'result'  : False,
             'message' : 'invalid auth token'
           } 
  else:
    try:
      db_regForEvent(eventNum,userName,userNum,car,altPwd)
      eventFuncLog.info("set_iCompUserAsEventParticipant - " + userName + " registered for event #" + str(eventNum))
      return {
                'result'  : True,
                'message' : 'event register was successful'
             }
    except Exception as e:
      eventFuncLog.error("set_iCompUserAsEventParticipant - exception occured during event registration")
      eventFuncLog.error(str(e))
      return {
                'result'  : False,
                'message' : 'ERROR - ' + str(e)
             }    


def set_scoreForUserInEventWeek(userNum,eventNum,weekNum,position,points,incidents,startPos,fastLapTime,token,altPwd):
  """
  Log a user score for an event week
  INPUTS
    userNum/int         - iComp account user number
    eventNum/int        - iComp event number
    weekNum/int         - week of event
    position/int        - finish position for week
    points/int          - points earned for week
    incidents/int       - incidents for week
    startPos/int        - started/qualified position
    fastLapTime/string  - fastest lap for the week (x.xx.xx)
    token/string        - auth token
  OUTPUT
    dictionary
      result/boolean     - function success
      message/string     - function success message
  """
  eventFuncLog.info("set_scoreForUserInEventWeek - checking auth token")

  ##Determine posGained
  posDiff = int(startPos) - int(position)
  if posDiff < 0:
    posDiff = 0
  else:
    pass

  if not validateToken(token):
    eventFuncLog.info("set_scoreForUserInEventWeek - invalid or expired token")
    eventFuncLog.warning("set_scoreForUserInEventWeek - someone log score for " + userNum + " to an event with an invalid token")
    return {
             'result'  : False,
             'message' : 'invalid auth'
           } 
  else:
    eventFuncLog.info("set_scoreForUserInEventWeek - attempting to log score for " + userNum)
    eventFuncLog.info("event: "     + str(eventNum))
    eventFuncLog.info("week: "      + str(weekNum))
    eventFuncLog.info("fin pos: "   + str(position))
    eventFuncLog.info("points: "    + str(points))
    eventFuncLog.info("inc count: " + str(incidents))
    eventFuncLog.info("fast lap: "  + str(fastLapTime))
    try:
      if len(fastLapTime.split('.')) == 2:
        fastLapTime = "0." + fastLapTime
      logScore = db_logScore(userNum,eventNum,weekNum,position,points,incidents,fastLapTime,startPos,str(posDiff),altPwd)
      return {
               'result'  : True,
               'message' : 'Week result logged successfully'
             }
    except Exception as e:
      eventFuncLog.error("set_scoreForUserInEventWeek - an exception occured while attempting to log a week score")
      eventFuncLog.error("set_scoreForUserInEventWeek - ERROR: " + str(e))
      return {
               'result'  : False,
               'message' : 'ERROR: ' + str(e)
             }

def get_eventDetailInformation(userNum,eventNum,currentUserNum,fastLapBonus,hardChargBonus,roPwd):
  """
  Get the scoring information for an event
  INPUT
    userNum/string   - iComp account name
    eventNum/string  - iComp event number
    currentUserNum   - User to pull results for
    fastLapBonus/int - bonus points for fast lap
  OUTPUT
    scheduleHtml/string - html for the schedule list
    rankingHtml/string  - html for the ranking information
    driverSelectHtml    - html for the driver select dropdown
    eventName/string    - name of event
    eventSeries         - iRacing series event covers
  """
  ##Get base event info
  eventFuncLog.info("get_eventDetailInformation - getting base event info")
  eventBaseInfo = db_getEventBaseInfo(eventNum,roPwd)
  ##Get and present single user schedule info
  eventFuncLog.info("get_eventDetailInformation - getting weekly results")
  scheduleResults = db_pullScheduleResults(eventNum,userNum,roPwd)  
  ##Get base ranking information
  eventFuncLog.info("get_eventDetailInformation - base ranking information")
  rankingResults = db_pullEventUserRank(eventNum,roPwd)      
  ##Pull fast time results here and return list as username,week,fastlap ordered by week
  eventFuncLog.info("get_eventDetailInformation - getting lap times")
  eventFastLabTimes = db_pullEventFastLaps(eventNum,roPwd)
  eventTopPosDif    = db_pullEventTopPosDif(eventNum,roPwd)  
  ##Set FLB enabled/disabled
  fastLapEnabled   = False
  hardChargEnabled = False
  if str(eventBaseInfo[2]) == "1":
    eventFuncLog.info("get_eventDetailInformation - FLB Enabled")
    fastLapEnabled = True
  if str(eventBaseInfo[3]) == "1":
    eventFuncLog.info("get_eventDetailInformation - HCB Enabled")
    hardChargEnabled = True    
  
  ##Generate schedule HTML
  eventFuncLog.info("get_eventDetailInformation - generating schedule html")
  scheduleHtml     = _generate_eventDetailScheduleHtml(scheduleResults,eventFastLabTimes,eventTopPosDif,userNum,currentUserNum,eventNum,fastLapEnabled,hardChargEnabled)
  eventFuncLog.info("get_eventDetailInformation - generating ranking html")
  rankingHtml      = _generate_eventDetailRankingHtml(rankingResults,eventFastLabTimes,eventTopPosDif,eventNum,fastLapBonus,hardChargBonus,fastLapEnabled,hardChargEnabled,roPwd)
  eventFuncLog.info("get_eventDetailInformation - generating driverSelect html")
  driverSelectHtml = _generate_eventDetailParticipantDropdownHtml(eventNum,userNum,roPwd)
  eventName        = eventBaseInfo[0]
  eventSeries      = eventBaseInfo[1]

  return {
            'scheduleHtml'     : scheduleHtml,
            'rankingHtml'      : rankingHtml,
            'driverSelectHtml' : driverSelectHtml,
            'eventName'        : eventName,
            'eventSeries'      : eventSeries
         }


def update_eventDetailsDisplayTable(userName,runningOrFinished,token,roPwd):
  """
  update the html for the event detail display table
  INPUT
    userName/string          - iComp account name
    runningOrFinished/string - pull current or finished events
    token/string             - auth token
  OUTPUT
    tableHtml/string      - html to update table with
  """  
  getEvents   = ""
  htmlStrBase = ""
  htmlStr     = ""
  eventFuncLog.info("update_eventDetailsDisplayTable - validating auth token")
  if not validateToken(token):    
    eventFuncLog.warning("update_eventDetailsDisplayTable - invalid token used to pull event details for " + userName)
    return "invalid or expired token"
  else:
    if runningOrFinished == "act":
      eventFuncLog.info("update_eventDetailsDisplayTable - Pulling event list for " + userName)
      getEvents = db_getRegisteredEvents(userName,0,roPwd)
    elif runningOrFinished == "fin":
      eventFuncLog.info("update_eventDetailsDisplayTable - Pulling event list for " + userName)
      getEvents = db_getRegisteredEvents(userName,1,roPwd)
      
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

  return htmlStrBase + htmlStr


def _generate_eventDetailParticipantDropdownHtml(eventNum,userNum,roPwd):
  """
  generate html for participant dropdown
  INPUT
    eventNum/int - iComp event number
  OUTPUT
    userDropdownHtml/list - html for user dropdown
  """
  userSelDropDownHtml = []
  userPar = db_getEventParticipants(eventNum,roPwd)
  for i in range(len(userPar)):
    if str(userPar[i][0]) == userNum:
      userSelDropDownHtml.append('<option value="' + str(userPar[i][0]) + '">#' + str(userPar[i][0]) + ' - ' + userPar[i][1] + '</option>')
  for i in range(len(userPar)):
    if str(userPar[i][0]) != userNum:
      userSelDropDownHtml.append('<option value="' + str(userPar[i][0]) + '">#' + str(userPar[i][0]) + ' - ' + userPar[i][1] + '</option>')  

  return userSelDropDownHtml

def _generate_eventDetailRankingHtml(rankingResults,eventFastLabTimes,eventTopPosDif,eventNum,fastLapBonus,hardChargBonus,fastLapEnabled,hardChargEnabled,roPwd):
  """
  Sort out and generate html for event ranking information
  INPUT
    rankingResults/list    - list of base tanking information
    eventFastLabTimes/list - list of fastest lap times for week
    eventNum/int           - iComp event number
    fastLapBonus/int       - point amount for FLB
    fastLapEnabled/boolean - if FLB is enabled
  OUTPUT
    scheduleHtml/string    - html for schedule information
  """
  ## get and review ranking info
  rankingResults = db_pullEventUserRank(eventNum,roPwd)   
  rankingInfo = [] ##[points][string]
  reviewed = []
  ###if FLB is enable
  ## add fastlap to row selection
  ## compare fast lap tp fast lap list for each week
  ## if numbers match , add 10 points to tmpPoing.append for the week
  for row in range(len(rankingResults)):
    tmpPoints  = []
    flBonus    = 0
    hcBonus    = 0
    userNum    = rankingResults[row][0]
    userFirst  = rankingResults[row][1]
    userLast   = rankingResults[row][2]
    userCar    = rankingResults[row][3]
    fastLap    = rankingResults[row][6]
    posGained  = rankingResults[row][7]
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
        flBonus = 0
        userFL = db_pullEventFastLapsForUser(eventNum,userNum,roPwd)
        for i in range(len(eventFastLabTimes)):
          for j in range(len(userFL)):
            try:
              if eventFastLabTimes[i][1] == userFL[i][1]:
                if i < 9:
                  flBonus = flBonus + fastLapBonus
                  break
                else:
                  pass
            except IndexError:
              pass

      if hardChargEnabled:
        hcBonus      = 0
        userHC       = db_pullEventTopPosDifForUser(eventNum,userNum,roPwd)
        retiredWeeks = []
        usrWeek      = 1
        while usrWeek < 9:
          weekPosGain = userHC[usrWeek-1][1]
          for i in range(len(eventTopPosDif)):
            try:
              if str(eventTopPosDif[i][1]) == str(weekPosGain) and str(weekPosGain) != "0" and str(weekPosGain) != "None" and i not in retiredWeeks:
                hcBonus = hcBonus + hardChargBonus
                retiredWeeks.append(i)
                break
              else:
                pass
            except IndexError:
              pass
          usrWeek = usrWeek + 1
      
      pointSum = sum(tmpPoints) + flBonus + hcBonus
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

  return rankingHTML


def _generate_eventDetailScheduleHtml(scheduleResults,eventFastLabTimes,eventTopPosDif,userNum,curUserNum,eventNum,fastLapEnabled,hardChargEnabled):
  """
  Sort out and generate html for event details schedule information
  INPUT
    scheduleResults/list   - list of schedule results
    eventFastLabTimes/list - list of fastest lap times for week
    userNum/int            - iComp user number
    curUserNum/int         - user to look up results for
    eventNum/int           - iComp event number
    fastLapEnabled/boolean - if FLB is enabled
  OUTPUT
    scheduleHtml/string    - html for schedule information
  """
  scheduleHtml = "<tr>"
  scheduleHtml = scheduleHtml + "<th>Week</th>"
  scheduleHtml = scheduleHtml + "<th>Track</th>"
  scheduleHtml = scheduleHtml + "<th>Position</th>"
  scheduleHtml = scheduleHtml + "<th>Started</th>"
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
    startPos = str(scheduleResults[row][7])
    posGain  = str(scheduleResults[row][8])
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
      if chgReq == '1' and position != '' and userNum.strip() == curUserNum.strip(): 
        scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Score modification pending approval"><i class="fas fa-sync"></i></a>  ' + week + '</td>'
      elif position != '' and userNum.strip() == curUserNum.strip():
        scheduleHtml = scheduleHtml + '<td><i class="far fa-edit" onClick="startScoreModify(' + eventNum + ',' + userNum + ',' + week + ');" ></i>  ' + position + '</td>'
      else:
        scheduleHtml = scheduleHtml + '<td>' + position + '</td>'
      scheduleHtml = scheduleHtml + "<td>" + startPos   + "</td>"  
      scheduleHtml = scheduleHtml + "<td>" + points   + "</td>"
      scheduleHtml = scheduleHtml + "<td>" + inc      + "</td>"
      scheduleHtml = scheduleHtml + "<td>" + fastLap_reformed      + "</td>"
      scheduleHtml = scheduleHtml + "</tr>"    
      del droppedWk[droppedWk.index(points)]
    else:
      ##HTML for counted week   
      ## setup for if FLB is enabled, check fastLap against the fast time for week [i]
      if (fastLapEnabled and row <= len(eventFastLabTimes)):
        if fastLap == eventFastLabTimes[row][1] and (hardChargEnabled and str(posGain) == str(eventTopPosDif[row][1]) and str(posGain) != "0" and str(posGain) != "None"):
          scheduleHtml = scheduleHtml + "<tr class='highlight_green'>"  
          scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Fastest Lap and Hard Charge Bonuses Applied For This Week"><i class="fab fa-reddit-alien"></i></a>  ' + week + '</td>'
          scheduleHtml = scheduleHtml + "<td>" + track    + "</td>"
          if chgReq == '1' and position != '' and userNum.strip() == curUserNum.strip(): 
            scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Score modification pending approval"><i class="fas fa-sync"></i></a>  ' + week + '</td>'
          elif position != '' and userNum.strip() == curUserNum.strip():
            scheduleHtml = scheduleHtml + '<td><i class="far fa-edit" onClick="startScoreModify(' + eventNum + ',' + userNum + ',' + week + ');" ></i>  ' + position + '</td>'
          else:
            scheduleHtml = scheduleHtml + '<td>' + position + '</td>'
          scheduleHtml = scheduleHtml + "<td>" + startPos   + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + points   + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + inc      + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + fastLap_reformed      + "</td>"
          scheduleHtml = scheduleHtml + "</tr>"  
        elif fastLap == eventFastLabTimes[row][1]:
          scheduleHtml = scheduleHtml + "<tr class='highlight_green'>"  
          scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Fastest Lap Bonus Applied For This Week"><i class="fas fa-stopwatch"></i></a>  ' + week + '</td>'
          scheduleHtml = scheduleHtml + "<td>" + track    + "</td>"
          if chgReq == '1' and position != '' and userNum.strip() == curUserNum.strip(): 
            scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Score modification pending approval"><i class="fas fa-sync"></i></a>  ' + week + '</td>'
          elif position != '' and userNum.strip() == curUserNum.strip():
            scheduleHtml = scheduleHtml + '<td><i class="far fa-edit" onClick="startScoreModify(' + eventNum + ',' + userNum + ',' + week + ');" ></i>  ' + position + '</td>'
          else:
            scheduleHtml = scheduleHtml + '<td>' + position + '</td>'
          scheduleHtml = scheduleHtml + "<td>" + startPos   + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + points   + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + inc      + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + fastLap_reformed      + "</td>"
          scheduleHtml = scheduleHtml + "</tr>"     
        elif hardChargEnabled and str(posGain) == str(eventTopPosDif[row][1]) and str(posGain) != "0" and str(posGain) != "None":
          scheduleHtml = scheduleHtml + "<tr class='highlight_green'>"  
          scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Hard Charge Bonus Applied For This Week"><i class="fas fa-tachometer-alt"></i></a>  ' + week + '</td>'
          scheduleHtml = scheduleHtml + "<td>" + track    + "</td>"
          if chgReq == '1' and position != '' and userNum.strip() == curUserNum.strip(): 
            scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Score modification pending approval"><i class="fas fa-sync"></i></a>  ' + week + '</td>'
          elif position != '' and userNum.strip() == curUserNum.strip():
            scheduleHtml = scheduleHtml + '<td><i class="far fa-edit" onClick="startScoreModify(' + eventNum + ',' + userNum + ',' + week + ');" ></i>  ' + position + '</td>'
          else:
            scheduleHtml = scheduleHtml + '<td>' + position + '</td>'
          scheduleHtml = scheduleHtml + "<td>" + startPos   + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + points   + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + inc      + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + fastLap_reformed      + "</td>"
          scheduleHtml = scheduleHtml + "</tr>"                    
        else:
          scheduleHtml = scheduleHtml + "<tr>"  
          scheduleHtml = scheduleHtml + "<td>" + week     + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + track    + "</td>"
          if chgReq == '1' and position != '' and userNum.strip() == curUserNum.strip(): 
            scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Score modification pending approval"><i class="fas fa-sync"></i></a>  ' + week + '</td>'
          elif position != '' and userNum.strip() == curUserNum.strip():
            scheduleHtml = scheduleHtml + '<td><i class="far fa-edit" onClick="startScoreModify(' + eventNum + ',' + userNum + ',' + week + ');" ></i>  ' + position + '</td>'
          else:
            scheduleHtml = scheduleHtml + '<td>' + position + '</td>'
          scheduleHtml = scheduleHtml + "<td>" + startPos   + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + points   + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + inc      + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + fastLap_reformed      + "</td>"
          scheduleHtml = scheduleHtml + "</tr>"  
      else:
        if hardChargEnabled and str(posGain) == str(eventTopPosDif[row][1]) and str(posGain) != "0" and str(posGain) != "None":
          scheduleHtml = scheduleHtml + "<tr class='highlight_green'>"  
          scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Hard Charge Bonus Applied For This Week"><i class="fas fa-tachometer-alt"></i></a>  ' + week + '</td>'
          scheduleHtml = scheduleHtml + "<td>" + track    + "</td>"
          if chgReq == '1' and position != '' and userNum.strip() == curUserNum.strip(): 
            scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Score modification pending approval"><i class="fas fa-sync"></i></a>  ' + week + '</td>'
          elif position != '' and userNum.strip() == curUserNum.strip():
            scheduleHtml = scheduleHtml + '<td><i class="far fa-edit" onClick="startScoreModify(' + eventNum + ',' + userNum + ',' + week + ');" ></i>  ' + position + '</td>'
          else:
            scheduleHtml = scheduleHtml + '<td>' + position + '</td>'
          scheduleHtml = scheduleHtml + "<td>" + startPos   + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + points   + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + inc      + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + fastLap_reformed      + "</td>"
          scheduleHtml = scheduleHtml + "</tr>"  
        else:
          scheduleHtml = scheduleHtml + "<tr>"  
          scheduleHtml = scheduleHtml + "<td>" + week     + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + track    + "</td>"
          if chgReq == '1' and position != '' and userNum.strip() == curUserNum.strip(): 
            scheduleHtml = scheduleHtml + '<td><a href="#" data-toggle="tooltip" title="Score modification pending approval"><i class="fas fa-sync"></i></a>  ' + week + '</td>'
          elif position != '' and userNum.strip() == curUserNum.strip():
            scheduleHtml = scheduleHtml + '<td><i class="far fa-edit" onClick="startScoreModify(' + eventNum + ',' + userNum + ',' + week + ');" ></i>  ' + position + '</td>'
          else:
            scheduleHtml = scheduleHtml + '<td>' + position + '</td>'
          scheduleHtml = scheduleHtml + "<td>" + startPos   + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + points   + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + inc      + "</td>"
          scheduleHtml = scheduleHtml + "<td>" + fastLap_reformed      + "</td>"
          scheduleHtml = scheduleHtml + "</tr>"   

  return scheduleHtml