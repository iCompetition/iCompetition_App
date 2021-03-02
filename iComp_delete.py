import os
import shutil
import subprocess
import sys
trees = [
               '/usr/local/lib/iCompetition',
               '/etc/iCompetition',
               '/var/www/iCompetition',
               '/var/log/iComp'
               ]

if sys.version_info[0] < 3:
    sys.stdout.write("Run Script in Python3\n")
    sys.exit()
else:
    pass

confirm = input("\nReally delete all iCompetition files?  Type 'delete icomp' to continue -- ")

if confirm == "delete icomp":
  sys.stdout.write("removing icomp files\n")
  os.popen('a2dissite iComp.conf')
  try: 
      os.remove('/etc/apache2/sites-available/iComp.conf')
      call = subprocess.call('systemctl restart apache2',shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
  except FileNotFoundError:
      pass  
  try: 
      os.popen('systemctl stop iCompApi')
      os.remove('/etc/systemd/system/iCompApt.service')
      call = subprocess.call('systemctl daemon-reload',shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
  except FileNotFoundError:
      pass
  try: os.remove('/etc/profile.d/iComp.sh')
  except FileNotFoundError:
      pass
  
  for i in range(len(trees)):
      shutil.rmtree(trees[i])
  
  sys.stdout.write("done\n")
else:
    sys.stdout.write("\nThanks for not removing iCompetition!\n\n")