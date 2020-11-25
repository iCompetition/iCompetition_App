##Databse functions for iComp
## rw = read/write
### read  = iCompRead
### write = iCompAlt
## rights = userpwd

##imports
import pymysql
from iComp_util import dbHasher
from iComp_util import getConf

##Variables
roUser = 'iCompRead'
altUser = 'iCompAlt'

##Get db info
conf   = getConf()
dbName = conf['database_name']
dbIp   = conf['database_location']

def _dbConnect(rw,rights):
  #rw = read/write
  if rw.lower() == "read":
    return pymysql.connect(dbIp,roUser,rights,dbName,autocommit=True)
  elif rw.lower() == "write":
    return pymysql.connect(dbIp,altUser,rights,dbName,autocommit=True)
  else:
    pass


def _cursorConnect(db):
  return db.cursor()


def _dbClose(db, cr):
  cr.close()
  db.close()


def db_authAdminStatus(userName, rights):
  ##check username for admin status
  db = _dbConnect("read",rights)
  cr = db.cursor()
  cr.execute("select admin from users where userName = '" + userName + "';")
  isAdmin = (cr.fetchall())[0][0]
  _dbClose(db, cr)
  return isAdmin


def db_createAccount(userName,firstName,lastName,pwd,email,rights):
  userNum = 0
  db = _dbConnect("write",rights)
  cr = db.cursor()
  ##Check if user exists, if not return exists
  cr.execute("select userName from users where userName = '" + userName + "';")
  if len(cr.fetchall()) != 0:
    _dbClose(db,cr)
    return {'result':False,'message':"user exists"} 
  else:
    ##determine the UID Num
    cr.execute("select userNum from users order by userNum desc limit 1;")
    result = cr.fetchall()
    if len(result) == 0:
      userNum = 1
    else:
      userNum = (result[0][0] + 1)
    pwd = dbHasher(pwd) ##has pwd
    ##attmpt to add new user to database.
    try:
      cr.execute("insert into users values ('" + userName + "','" + firstName + "','" + lastName + "','" + pwd + "',0," + str(userNum) + ",'" + email + "');")
    except Exception as e:
      _dbClose(db,cr)
      return {'result':False,'message':str(e)}
    _dbClose(db,cr)
    return {'result':True,'message':"created"}      


def db_loginUser(userName,pwd,rights):
  db = _dbConnect("read",rights)
  cr = db.cursor()
  ##get the hashed user password and compare to provided one
  cr.execute("select password from users where username = '" + userName + "' limit 1;")
  result = cr.fetchone()
  _dbClose(db, cr)  
  try:
    if result[0] == pwd:
      return True
    else:
      return False
  except TypeError:
    return False


def db_getUsrInfo(userName, rights):
  isAdmin = "N"
  db = _dbConnect("read",rights)
  cr = db.cursor()
  cr.execute("select firstName, lastName, userNum, admin from users where userName = '" + userName + "';")
  results = cr.fetchall()
  _dbClose(db, cr)
  if results[0][3] == 1: 
    isAdmin = "Y"
  return {
          'firstName' : results[0][0],
          'lastName'  : results[0][1],
          'userNum'   : results[0][2], 
          'admin'     : isAdmin
          }


def db_changePass(newPass,userName,rights):
  try:
    db = _dbConnect("write",rights)
    cr = db.cursor()   
    cr.execute("update users set password = '" + dbHasher(newPass) + "' where userName = '" + userName + "';")
    _dbClose(db,cr)
    return True
  except Exception as e:
    return False  


def db_changeEmail(newEmail,userName,rights):
  try:
    db = _dbConnect("write",rights)
    cr = db.cursor()   
    cr.execute("update users set email = '" + newEmail + "' where userName = '" + userName + "';")
    _dbClose(db,cr)
    return True
  except Exception as e:
    return False 


def db_getUsrNum(userName,rights):
  db = _dbConnect("read",rights)
  cr = db.cursor()
  cr.execute("select userNum from users where userName = '" + userName + "';")
  results = cr.fetchone()
  _dbClose(db,cr)
  return results[0]


def db_initPasswordEmail(userName, rights):
  db = _dbConnect("read",rights)
  cr = db.cursor()
  cr.execute("select email from users where userName = '" + userName + "';")
  results = cr.fetchone()
  _dbClose(db, cr)
  return results[0]


def db_checkIfUserHasEvent(userName, rights):
  db = _dbConnect("read",rights)
  cr = db.cursor()
  cr.execute("select userName from participants where userName = '" + userName + "';")
  results = cr.fetchall()
  _dbClose(db,cr)
  return results  


def db_getLiveEvents(userName,rights):
  query = """
        select name, eventNum 
        from event
        where live = 1
        and eventNum not in (select eventNum 
                             from participants
                             where userName = '""" + userName + """')
        order by eventNum;
        """
  db = _dbConnect("read",rights)
  cr = db.cursor()
  cr.execute(query)
  results = cr.fetchall()
  _dbClose(db,cr)
  return results


def db_getEventCars(eventNum,rights):
  db = _dbConnect("read",rights)
  cr = db.cursor()
  cr.execute("select vehicle from vehicles where eventNum = " + str(eventNum) + " order by vehicle;")
  results = cr.fetchall()
  _dbClose(db,cr)
  return results


def db_regForEvent(eventNum,userName,userNum,car,rights):
  db = _dbConnect("write",rights)
  cr = db.cursor()
  cr.execute("insert into participants values ('" + userName + "'," + eventNum + ",'" + car + "'," + userNum + ");")
  _dbClose(db,cr)
  return True


def db_getRegisteredEvents(userName,rights):
  query = """select e.eventNum, e.name, e.series, p.vehicle 
             from event e 
             inner join participants p 
             where e.eventNum = p.eventNum 
             and p.username = '""" + userName + """'
             order by e.eventNum;
             """
  db = _dbConnect("read",rights)
  cr = db.cursor()  
  cr.execute(query)
  results = cr.fetchall()
  _dbClose(db,cr)
  return results


def db_getEventScheduleWeeks(eventNum,userNum,rights):
  query = """
          select week
          from schedule
          where eventNum = """ + str(eventNum) + """
          and week not in (select week
                           from scoring
                           where eventNum = """ + str(eventNum) + """
                           and userNum = """ + str(userNum) + """)
          order by week
          """
  db = _dbConnect("read",rights)
  cr = db.cursor() 
  cr.execute(query)
  results = cr.fetchall()
  _dbClose(db,cr)
  return results  


def db_logScore(userName,eventNum,wkNum,pos,pnt,inc,lap,rights):
  db = _dbConnect("write",rights)
  cr = db.cursor()   
  cr.execute("insert into scoring values (" + eventNum + "," + wkNum + "," + userName + "," + pnt + "," + inc + "," + pos + ",0,'" + lap + "');")
  _dbClose(db,cr)


def db_getEventBaseInfo(eventNum,rights):
  db = _dbConnect("read",rights)
  cr = db.cursor()  
  cr.execute("select name, series, enableFastLapBonus from event where eventNum = " + str(eventNum) + ";")
  results = cr.fetchone()
  _dbClose(db,cr)
  return results


def db_pullEventFastLaps(eventNum,rights):
  db = _dbConnect("read",rights)
  cr = db.cursor()  
  cr.execute("select weekNum, laptime from topLap where eventNum = " + str(eventNum) + " order by weekNum;")
  results = cr.fetchall()
  _dbClose(db,cr)
  return results  


def db_getEventParticipants(eventNum,rights):
  db = _dbConnect("read",rights)
  cr = db.cursor()  
  cr.execute('select userNum, username from participants where eventNum = ' + str(eventNum) + ';')
  results = cr.fetchall()
  _dbClose(db,cr)
  return results  


def db_pullEventUserRank(eventNum,rights):
  userRankQuery = """
    select p.userNum, u.firstName, u.lastName, p.vehicle, sc.points, u.userName, sc.fastLap
    from participants p
    join scoring sc on p.userNum = sc.userNum
    join users u on sc.userNum = u.userNum
    where p.userNum in (
                        select userNum 
                        from scoring 
                        where eventNum = """ + str(eventNum) + """)
    and sc.eventNum = """ + str(eventNum) + """
    and p.eventNum = sc.eventNum
    order by p.userNum
    """  
  db = _dbConnect("read",rights)
  cr = db.cursor()   
  cr.execute(userRankQuery)
  results = cr.fetchall()
  _dbClose(db,cr)
  return results


def db_pullScheduleResults(eventNum,userNum,rights):
  scheduleQuery = """
    select sch.week, sch.track, ifnull(sc.position,''), ifnull(sc.points,''), ifnull(sc.inc,''), sc.changeRequested, sc.fastLap
      from schedule sch 
        left join scoring sc 
          on sch.week = sc.week
          and sch.eventNum = sc.eventNum 
          and sc.userNum = """ + str(userNum) + """
        where sch.eventNum = """ + str(eventNum) + """
        order by sch.week
    """
  db = _dbConnect("read",rights)
  cr = db.cursor()   
  cr.execute(scheduleQuery)
  results = cr.fetchall()
  _dbClose(db,cr)
  return results


def db_listUsers(rights):
  db = _dbConnect("read",rights)
  cr = db.cursor() 
  cr.execute("select userName, userNum from users order by userNum")
  results = cr.fetchall()
  _dbClose(db,cr)
  return results  


def db_listEvents(rights):
  db = _dbConnect("read",rights)
  cr = db.cursor() 
  cr.execute("select name, series, eventNum, live from event order by eventNum")
  results = cr.fetchall()
  _dbClose(db,cr)
  return results  


def db_createEvent(eName,eSeries,wkTracks,w13,cars,live,rights,fastLapBonus):
  eNum = 0
  carList = cars.split(",")
  db = _dbConnect("write",rights)
  cr = db.cursor()   
  cr.execute("select eventNum from event order by eventNum desc limit 1;")
  result = cr.fetchall()
  if len(result) == 0:
    eventNum = 1
  else:
    eventNum = (result[0][0] + 1)  
  cr.execute("insert into event values('" + eName + "','" + eSeries + "'," + str(eventNum) + "," + str(live) + "," + str(fastLapBonus) + ");")
  cr.execute("insert into schedule values (" + str(eventNum) + ",1,'"  + wkTracks['1'] + "');")
  cr.execute("insert into schedule values (" + str(eventNum) + ",2,'"  + wkTracks['2'] + "');")
  cr.execute("insert into schedule values (" + str(eventNum) + ",3,'"  + wkTracks['3'] + "');")
  cr.execute("insert into schedule values (" + str(eventNum) + ",4,'"  + wkTracks['4'] + "');")
  cr.execute("insert into schedule values (" + str(eventNum) + ",5,'"  + wkTracks['5'] + "');")
  cr.execute("insert into schedule values (" + str(eventNum) + ",6,'"  + wkTracks['6'] + "');")
  cr.execute("insert into schedule values (" + str(eventNum) + ",7,'"  + wkTracks['7'] + "');")
  cr.execute("insert into schedule values (" + str(eventNum) + ",8,'"  + wkTracks['8'] + "');")
  cr.execute("insert into schedule values (" + str(eventNum) + ",9,'"  + wkTracks['9'] + "');")
  cr.execute("insert into schedule values (" + str(eventNum) + ",10,'" + wkTracks['10'] + "');")
  cr.execute("insert into schedule values (" + str(eventNum) + ",11,'" + wkTracks['11'] + "');")
  cr.execute("insert into schedule values (" + str(eventNum) + ",12,'" + wkTracks['12'] + "');")  
  if w13:
    cr.execute("insert into schedule values (" + str(eventNum) + ",13,'" + wkTracks['13'] + "');")  
  for c in range(len(carList)):
    cr.execute("insert into vehicles values (" + str(eventNum) + ",'" + carList[c].strip() + "');")   
  _dbClose(db,cr)
 

def db_getUserInfoForAdmin(userName, rights):
  rd = {}
  db = _dbConnect("read",rights)
  cr = db.cursor()   
  cr.execute("select userName, firstName, lastName, admin, userNum, email from users where userName = '" + userName + "';")
  baseInfo = cr.fetchall()
  rd['userName'] = baseInfo[0][0]
  rd['name']     = baseInfo[0][1] + " " + baseInfo[0][2]
  if baseInfo[0][3] == '1' or baseInfo[0][3] == 1 :
    rd['isAdm']    = True
  else:
    rd['isAdm']    = False
  rd['userNum']  = baseInfo[0][4]
  rd['email']    = baseInfo[0][5]
  cr.execute("select count(userNum) from participants where userNum = " + str(rd['userNum']) + ";")
  eventCount = cr.fetchall()
  rd['eventCount'] = eventCount[0][0]
  _dbClose(db,cr)
  return rd
  

def db_getResultsForWeek(event,user,week,rights):
  query = """
  select u.username, e.name as eventName, sch.track, sc.points, sc.position, sc.inc
  from users u
  join scoring sc 
    on u.userNum = sc.userNum
  join event e 
    on sc.eventNum = e.eventNum
  join schedule sch 
    on sch.eventNum = sc.eventNum 
    and sch.Week = sc.week
  where sc.eventNum = """ + event + """
  and sc.userNum = """ + user + """
  and sc.week = """ + week + """
  """
  
  db = _dbConnect("read",rights)
  cr = db.cursor()    
  cr.execute(query)
  results = cr.fetchall()
  _dbClose(db,cr)
  return {
          'success'   : True, 
          'userName'  : results[0][0], 
          'eventName' : results[0][1],
          'track'     : results[0][2],
          'points'    : results[0][3],
          'position'  : results[0][4],
          'inc'       : results[0][5]
         }


def db_addChangeReqToDB(event,user,week,pnt,pos,inc,cPnt,cPos,cInc,rights):
  
  reqNum = 0  
  userName = ""
 
  db = _dbConnect("write",rights)
  cr = db.cursor()     

  cr.execute("select userName from users where userNum = " + str(user) + ";")
  userName = cr.fetchall()[0][0]

  cr.execute("select reqNum from requestedChanges order by reqNum desc limit 1;")
  result = cr.fetchall()
  if len(result) == 0:
    reqNum = 1
  else:
    reqNum = (result[0][0] + 1)
  
  insertQuery = """
                insert into requestedChanges
                values (""" + str(reqNum)   + """,
                        """ + str(user)     + """,
                       '""" + str(userName) + """',
                        """ + str(cPnt)     + """,
                        """ + str(cInc)     + """,
                        """ + str(cPos)     + """,
                        """ + str(pnt)      + """,
                        """ + str(inc)      + """,
                        """ + str(pos)      + """,
                        """ + str(event)      + """,
                        """ + str(week)      + """);
  """  
  cr.execute(insertQuery)
  cr.execute("update scoring set changeRequested = 1 where eventNum = " + str(event) + " and userNum = " + str(user) + " and week = " + str(week) + ";")
  _dbClose(db,cr)    
  return True


def db_getChgReqList(rights):
  
  query = """
          select reqNum, 
                 userNum, 
                 userName, 
                 curPoints, 
                 curInc, 
                 curPosition,
                 newPoints,
                 newInc, 
                 newPosition,
                 eventNum,
                 week
          from requestedChanges
          order by reqNum
          """
  
  db = _dbConnect("read",rights)
  cr = db.cursor()    
  cr.execute(query)
  results = cr.fetchall()
  _dbClose(db,cr)
  return results
  

def db_approveChgReq(reqNum, rights):
  db = _dbConnect("write",rights)
  cr = db.cursor() 
  query1 = """
          select userNum,
                 eventNum,
                 week,
                 newPoints,
                 newPosition,
                 newInc
          from requestedChanges
          where reqNum = """ + str(reqNum) + """;"""
          
  cr.execute(query1)
  chgResults = cr.fetchall()
  query2 = """
         update scoring
         set points = """    + str(chgResults[0][3]) + """,
             position = """  + str(chgResults[0][4]) + """,
             inc = """       + str(chgResults[0][5]) + """,
             changeRequested = 0
         where userNum = """ + str(chgResults[0][0]) + """
         and eventNum = """  + str(chgResults[0][1]) + """
         and week = """      + str(chgResults[0][2]) + """
         and changeRequested = 1;
         """
  cr.execute(query2)  
  query4 = "delete from requestedChanges where reqNum = " + reqNum + ";"
  cr.execute(query4) 
  _dbClose(db,cr)
  return True


def db_rejectChgReq(reqNum, rights):
  db = _dbConnect("write",rights)
  cr = db.cursor() 
  query0 = """
        select userNum,
               eventNum,
               week,
               newPoints,
               newPosition,
               newInc
        from requestedChanges
        where reqNum = """ + str(reqNum) + """;"""
  cr.execute(query0)
  chgResults = cr.fetchall()        
  query1 = """
         update scoring
         set changeRequested = 0
         where userNum = """ + str(chgResults[0][0]) + """
         and eventNum = """  + str(chgResults[0][1]) + """
         and week = """      + str(chgResults[0][2]) + """
         and changeRequested = 1;
         """
  cr.execute(query1)         
  query2 = "delete from requestedChanges where reqNum = " + reqNum + ";"
  cr.execute(query2)         
  _dbClose(db,cr)
  return True

