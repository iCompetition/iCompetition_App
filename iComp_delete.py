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

sys.stdout.write("removing icomp files\n")
os.popen('a2dissite iComp.conf')
try: 
    os.remove('/etc/apache2/sites-available/iComp.conf')
    call = subprocess.call('systemctl restart apache2',shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
except FileNotFoundError:
    pass

try: 
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