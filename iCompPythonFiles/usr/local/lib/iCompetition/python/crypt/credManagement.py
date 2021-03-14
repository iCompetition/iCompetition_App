import argparse
import sys
import os
sys.path.append('/usr/local/lib/iCompetition/python/')
from iComp_util import iencrypt
from iComp_util import idecrypt

def parseParms():
  parser = argparse.ArgumentParser(description='iCompCredStore')
  parser.add_argument("command", help="add or remove")
  parser.add_argument("-u","--username", help="username", default="zero")
  parser.add_argument("-p","--password", help="password", default="zero")
  return parser.parse_args()
  
def _storeCred(username,password):
  pwd = iencrypt(password)
  fh = open('/etc/iCompetition/.creds/.' + username,'wb')
  fh.write(pwd)
  fh.close()
  
def _removeCred(username):
  os.remove('/etc/iCompetition/.creds/.' + username)
  
def getCred(username):
  fh = open('/etc/iCompetition/.creds/.' + username,'rb')
  p = fh.read()
  fh.close()
  return p

def main():
  parm = parseParms()
  if parm.command.upper() == 'ADD':
    if parm.username != 'zero' and parm.password != 'zero':
      _storeCred(parm.username,parm.password)
    else:
      sys.stdout.write("username or password not populated")
  elif parm.command.upper() == 'REMOVE':
    if parm.username != 'zero':
      _removeCred(parm.username)
    else:
      sys.stdout.write("username not populated")

if __name__ == "__main__":
  main()

