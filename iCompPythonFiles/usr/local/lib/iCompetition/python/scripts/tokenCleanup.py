#!/usr/bin/python3
import sys, os
sys.path.append('/usr/local/lib/iCompetition/python')
from iComp_util import validateToken, validateAdmToken, validatePwdToken

##normal token list
normalTokens = os.listdir('/usr/local/lib/iCompetition/.tokens')
normalTokens.remove('.adm')
normalTokens.remove('.pwd')

##Admin token list
adminTokens = os.listdir('/usr/local/lib/iCompetition/.tokens/.adm')

##pwd change token list
pwdTokens = os.listdir('/usr/local/lib/iCompetition/.tokens/.pwd')

##Remove expired tokens
if len(normalTokens) > 0:
  for i in range(len(normalTokens)):
    validateToken(normalTokens[i].strip())

if len(adminTokens) > 0:
  for i in range(len(adminTokens)):
    validateAdmToken(adminTokens[i].strip())

if len(pwdTokens) > 0:
  for i in range(len(pwdTokens)):
    validatePwdToken(pwdTokens[i].strip())