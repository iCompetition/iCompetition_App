#!/usr/bin/python3
import argparse
import requests

##Version api check command
##get list
#requests.get('https://api.github.com/repos/iCompetition/iCompetition_App/releases',verify=False)

##output list
#for i in range(len(t.json())):
#  print(t.json()[i].get('tag_name)

##updater script for iComp version
def getArguments():
  parser = parser = argparse.ArgumentParser(description='Changes image for login page')
  parser.add_argument('func',help="update / listVersions")
  parser.add_argument('--version',default='NONE',help="delete existing image.  false by deault",)
  return parser.parse_args()



