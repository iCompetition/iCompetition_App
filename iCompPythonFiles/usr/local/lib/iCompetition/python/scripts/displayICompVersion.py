#!/usr/bin/python3

##displays version information to console.  provides app version and pulls version for db schema

import sys 
sys.path.append("/usr/local/lib/iCompetition/python")
sys.path.append("/usr/local/lib/iCompetition/python/crypt")
from iComp_util import getConf
from iComp_db import db_schemaVersion
from iComp_util import *
from credManagement import *
outFmt = ("{:25s}: {}\n")
roPwd = idecrypt(getCred("iCompRead"))
schema = db_schemaVersion(roPwd)
sys.stdout.write("\n")
sys.stdout.write(outFmt.format("iCompetition App Version", getConf()['version']))
sys.stdout.write(outFmt.format("iCompeition DB Version", str(schema)))
sys.stdout.write("\n")