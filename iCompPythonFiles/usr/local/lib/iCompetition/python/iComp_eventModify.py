##########
##User functions for iComp
##########

##Standard Imports
import sys
import logging

##iCompImports
from iComp_db import *
from iComp_util import *

##logging
eventModFuncLog = logging.getLogger('eventModFuncLog')
eventModFuncLog.setLevel(logging.DEBUG)
logHandler = logging.handlers.RotatingFileHandler('/var/log/iComp/eventModifyFunctions.log', maxBytes=100000, backupCount=10)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logHandler.setFormatter(formatter)
eventModFuncLog.addHandler(logHandler)

##Functions
def get_preModifiedEventDetails(userNum,eventNum,weekNum,token,roPwd):
  """
  Get modifiable results prior to modification request
  INPUT
    userNum/int  - iComp account number
    eventNum/int - iComp event number
    weekNum/int  - week number to modify
    token/string - auth token
  OUTPUT
    results/dict - information about week
    success   
    userName 
    eventName
    track  
    points  
    position
    inc  
  """
  eventModFuncLog.info("get_preModifiedEventDetails - checking auth token")
  if not validateToken(token):
    eventModFuncLog.warning("get_preModifiedEventDetails - invalid auth token used")
    return {
             'success' : False
           }
  else:
    try:
      eventModFuncLog.info("get_preModifiedEventDetails - pulling information")
      results = db_getResultsForWeek(eventNum,userNum,weekNum,roPwd)
      return results
    except Exception as e:
      eventModFuncLog.error("get_preModifiedEventDetails - an error has occured")
      eventModFuncLog.error("get_preModifiedEventDetails - ERROR: " + str(e))
      return {
               'success' : False
             }


def get_changeRequests(roPwd):
  """
  pull the list of requested changes
  OUTPUT
    dictionary
      changeCnt/int - number of requests
      html/string   - html for display 
  """
  eventModFuncLog.info("get_changeRequestsHtml - pulling requested changes")
  chgList = db_getChgReqList(roPwd)
  if len(chgList) < 1:
    return {
            'changeCnt' : 0,
            'html'      : None
           }
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
    return {
            'changeCnt' : len(chgList),
            'html'      : htmlStr
           }      


def set_eventWeekModifyTrue(eventNum,userNum,weekNum,points,position,incidents,token,roPwd,altPwd):
  """
  create new change request for week scores
  INPUT
    eventNum/int  - iComp event number
    userNum/int   - iComp account number
    weekNum/int   - week number
    points/int    - new points value
    position/int  - new position value
    incidents/int - new incidents value
    token/string  - auth token
  OUTPUT
    success/boolean - function sucess
    message/string  - function success message
  """
  eventModFuncLog.info("get_preModifiedEventDetails - validating token")
  if not validateToken(token):  
    eventModFuncLog.warning("get_preModifiedEventDetails - invalid token used!")
    return {
             'success' : False,
             'message' : "Invalid or expired token was used"
           }
  else:
    try:
      eventModFuncLog.info("get_preModifiedEventDetails - pulling current week scores")
      oldResults = db_getResultsForWeek(eventNum,userNum,weekNum,roPwd)
      eventModFuncLog.info("get_preModifiedEventDetails - adding modification request to DB")
      cReq = db_addChangeReqToDB(eventNum,userNum,weekNum,points,position,incidents,oldResults['points'],oldResults['position'],oldResults['inc'],altPwd)
      return {
               'success' : cReq,
               'message' : 'modification request entered'
             }
    except Exception as e:
      eventModFuncLog.error("get_preModifiedEventDetails - error occured adding request to database")
      eventModFuncLog.error("get_preModifiedEventDetails - ERROR: " + str(e))
      return {
               'success' : False,
               'message' : 'ERROR: ' + str(e)
             }


def set_changeRequestResponse(requestNum,approvalStatus,admToken,altPwd):
  """
  Set the status of a change request as approved or denied
  INPUT
    requestNum/int     - change request number 
    approvalStatus/int - approve or deny (0/1)
    admtoken/string    - admin auth token
  OUTPUT
    success/boolean    - function success
  """
  eventModFuncLog.info("set_changeRequestResponse - validating token")
  if not validateAdmToken(admToken):
    eventModFuncLog.warning("set_changeRequestResponse - someone tried to approve change request with invalid or expired administrator token!")
    return False
  else:
    if int(approvalStatus) == 0:
      try:
        dbCall = db_approveChgReq(requestNum,altPwd)
        return dbCall
      except Exception as e:
        eventModFuncLog.error("set_changeRequestResponse - error approving change request")
        eventModFuncLog.error("set_changeRequestResponse - ERROR: " + str(e))     
        return False   
    elif int(approvalStatus) == 1:
      try:
        dbCall = db_rejectChgReq(requestNum,altPwd)
        return dbCall
      except Exception as e:
        eventModFuncLog.error("set_changeRequestResponse - error approving change request")
        eventModFuncLog.error("set_changeRequestResponse - ERROR: " + str(e))     
        return False
    else:
      eventModFuncLog.error("set_changeRequestResponse - an invalid approval status of " + str(approvalStatus) + " wass provided")
      return False