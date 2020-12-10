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
userFuncLog = logging.getLogger('userFuncLog')
userFuncLog.setLevel(logging.DEBUG)
logHandler = logging.handlers.RotatingFileHandler('/var/log/iComp/userFunctions.log', maxBytes=100000, backupCount=10)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logHandler.setFormatter(formatter)
userFuncLog.addHandler(logHandler)

##Functions
def create_iCompAccount(uName,fName,lName,pwd,email,altPwd):
  """
  Create new iComp user account
  INPUT
    uname/string - account username
    fname/string - account users first name
    lname/string - account users last name
    pwd/string   - password for account
    email/string - email address for account
  OUTPUT
    dictionary
      result/boolean - did the account get created correctly
      message/string  - information about the success code
  """
  userFuncLog.info("create_iCompAccount - checking email formatting")
  if not iCompUtils_validateEmail(email):
    userFuncLog.info("create_iCompAccount - invalid email formatting")
    return {'result' : False, 'message' : 'invalid email format'}
  else:
    userFuncLog.info("create_iCompAccount - email OKAY")
    userFuncLog.info("create_iCompAccount - Create accout attempt:")
    userFuncLog.info("\tUN:" + uName)
    userFuncLog.info("\tFN:" + fName)
    userFuncLog.info("\tLN:" + lName)    
    createUser = db_createAccount(uName,fName,lName,pwd,email,altPwd)
    if not createUser['result']:
      userFuncLog.info("create_iCompAccount - create acct failed")
      userFuncLog.info("create_iCompAccount - " + createUser['message'])
      return {'result':False,'message':createUser['message']}
    elif createUser['result']:
      userFuncLog.info("create_iCompAccount - create acct sucess")
      return {'result':True,'message':createUser['message']}


def validate_iCompUser(uname,pwd,roPwd):
  """
  Validate iCompUser for login
  INPUT
    uname/string - account username
    pwd/string   - password for accoun
    OUTPUT
    dictionary
      result/boolean - did the account get created correctly
      message/string - information about the success code
      token/string   - access token for user, if login was successful
  """
  userFuncLog.info("validate_iCompUser - checking user for login")
  userLogin = db_loginUser(uname,pwd,roPwd)
  if userLogin:
    userFuncLog.info("validate_iCompUser - valid login for " + uname)
    userFuncLog.info("validate_iCompUser - generating token for " + uname)
    token = generateToken()
    return {
             'result'  : True, 
             'message' : 'login successful',
             'token'   : token
            }
  else:
    userFuncLog.info("validate_iCompUser - failed login for " + uname)
    return {
         'result'  : False, 
         'message' : 'Username or password was incorrect',
         'token'   : token
        }


def get_iCompUserInfo(username,token,roPwd):
  """
  Pull basic information for an iComp user account
  INPUT
    username/string - iComp acct name
    token/string    - auth string
  OUTPUT
    userInfo/Dict
  """
  userFuncLog.info("get_iCompUserInfo - checking auth token")
  if not validateToken(token):
    userFuncLog.warning("get_iCompUserInfo - invalid or expired token used")
    return False
  else:
    userFuncLog.info("get_iCompUserInfo - authorized token")
    userFuncLog.info("get_iCompUserInfo - pulling info for " + username)
    userInfo = db_getUsrInfo(username,roPwd)
    return userInfo


def set_iCompUserPassword(username,pwd,token,altPwd):
  """
  Set the password for an iComp account
  INPUT
    username/string - iComp acct name
    pwd/string      - password to use
    token/string    - auth string
  OUTPUT
    result/boolean  - change successful
  """
  userFuncLog.info("set_iCompUserPassword - checking auth token")
  if not validatePwdToken(token) and not validateToken(token) :  
    userFuncLog.warning("set_iCompUserPassword - invalid or expired token used")
    userFuncLog.warning("set_iCompUserPassword - invalid token used to attempt pwd change for " + username + "!")
    return False
  else:
    userFuncLog.info("set_iCompUserPassword - authorized token")
    chgPass = db_changePass(pwd,username,altPwd)
    if chgPass:
      userFuncLog.info("set_iCompUserPassword - pwd changed for " + username)
      clearToken(token)
      return True
    else:
      userFuncLog.info("set_iCompUserPassword - failed pwd changed for " + username)
      return False


def set_iCompUserEmail(username,email,token,altPwd):
  """
  Set the email forr an iComp Account
  INPUT
    username/string - iComp acct name
    email/string    - email address to use
    token/string    - auth string
  OUTPUT
    result/boolean  - change successful  
  """
  userFuncLog.info("set_iCompUserEmail - checking auth token")
  if not validateToken(token):  
    userFuncLog.warning("set_iCompUserEmail - invalid or expired token used")
    userFuncLog.warning("set_iCompUserEmail - invalid token used to attempt email change for " + username + "!")
    return False
  else:
    userFuncLog.info("set_iCompUserEmail - authorized token")
    chgPass = db_changeEmail(email,username,altPwd)
    if chgPass:
      userFuncLog.info("set_iCompUserEmail - email changed for " + username)
      clearToken(token)
      return True
    else:
      userFuncLog.info("set_iCompUserEmail - failed email changed for " + username)
      return False  

