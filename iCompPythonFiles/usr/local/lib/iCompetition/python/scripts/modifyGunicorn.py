#!/usr/bin/python3

import argparse
import sys

def getArguments():
  parser = parser = argparse.ArgumentParser(description='Changes image for login page')
  parser.add_argument('-w','--workers',help="number of gunicorn processes",)
  return parser.parse_args()


def editWorkers(workers):
  
  try:
    int(workers)
  except:
    sys.stdout.write("workers must be int\n")
    sys.exit()
  
  fh = open('/etc/iCompetition/iCompGunicornConf.py', 'r')
  oldConf = fh.readlines()
  fh.close()

  rewrite = []
  for line in oldConf:
    if line.split("=")[0].strip() == 'workers':
      rewrite.append("workers   = " + str(workers) + "\n")
    else:
      rewrite.append(line)
  




def main():
  parms = getArguments()
  editWorkers(parms.workers)



if __name__ == '__main__':
  main()