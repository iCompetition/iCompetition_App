import sys 
sys.path.append("/usr/local/lib/iCompetition/python")
sys.path.append("/usr/local/lib/iCompetition/python/crypt")
from iComp_db import db_schemaVersion
from iComp_util import *
from credManagement import *

roPwd = idecrypt(getCred("iCompRead"))

schema = db_schemaVersion(roPwd)

sys.stdout.write("\niCompeition Database is running schema version " + str(schema) + "\n\n")