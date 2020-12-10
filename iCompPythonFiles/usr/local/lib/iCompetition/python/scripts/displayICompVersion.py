import sys 
sys.path.append("/usr/local/lib/iCompetition/python")
from iComp_util import getConf

sys.stdout.write("\nRunning iCompetition Application Version: " + getConf()['version'] + "\n\n")