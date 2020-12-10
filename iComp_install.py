#!/usr/lib/python3

#####installer for iCompetition
#####Requires root

##Imports
import os
import sys
import subprocess
import getpass
import errno

##Variables
installVersion = '1.01.00'
dirsToCreate   = [
                 '/usr/local/lib/iCompetition/api',
                 '/usr/local/lib/iCompetition/python',
                 '/usr/local/lib/iCompetition/python/crypt',
                 '/usr/local/lib/iCompetition/python/scripts',
                 '/usr/local/lib/iCompetition/.tokens',
                 '/usr/local/lib/iCompetition/.tokens/.adm',
                 '/usr/local/lib/iCompetition/.tokens/.pwd',
                 '/etc/iCompetition/.creds',
                 '/var/www/iCompetition/css',
                 '/var/www/iCompetition/js',
                 '/var/www/iCompetition/images',
                 '/var/log/iComp'
                 ]
domain    = ""
httpsPort = ""


def CheckPrereq():
    ##check user
    if getpass.getuser() == 'root':
        pass
    else:
        sys.stdout.write("root user is required\n")
        sys.exit()

    #Check python version
    sys.stdout.write("\nChecking iComp prereqs...\n\n")
    sys.stdout.write("Python version meets requirements...")
    if sys.version_info[0] < 3:
        sys.stdout.write("FALSE\n\n")
        sys.stdout.write("iComp Requires Version 3 or higher\n\n")
        sys.exit()
    else:
        sys.stdout.write("TRUE\n")
        pass

    ##Check packages
    #apache2
    sys.stdout.write("Apache2 is installed...")
    checkApache = subprocess.call('apt list | grep apache',shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    if checkApache == 0:
        sys.stdout.write("TRUE\n")
        pass        
    else:
        sys.stdout.write("FALSE\n\n")
        sys.stdout.write("iComp Requires apache2 to be installed\n\n")
        sys.exit()        
    #gunicorn
    sys.stdout.write("Gunicorn is installed...")
    checkGunicorn = subprocess.call('apt list | grep gunicorn',shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    if checkGunicorn == 0:
        sys.stdout.write("TRUE\n")
        pass        
    else:
        sys.stdout.write("FALSE\n\n")
        sys.stdout.write("iComp Requires gunicorn to be installed\n\n")
        sys.exit()        

    ##Check python modules
    try:
        sys.stdout.write('Python3 module - flask installed...')
        import flask
        sys.stdout.write('TRUE\n')
    except ModuleNotFoundError:
        sys.stdout.write('FALSE\n\n')
        sys.stdout.write("iComp Requires flask to be installed\n\n")
        sys.exit
    try:
        sys.stdout.write('Python3 module - flask_cors installed...')
        import flask_cors
        sys.stdout.write('TRUE\n')
    except ModuleNotFoundError:
        sys.stdout.write('FALSE\n\n')
        sys.stdout.write("iComp Requires flask_cors to be installed\n\n")
        sys.exit        
    try:
        sys.stdout.write('Python3 module - smtplib installed...')
        import smtplib
        sys.stdout.write('TRUE\n')
    except ModuleNotFoundError:
        sys.stdout.write('FALSE\n\n')
        sys.stdout.write("iComp Requires smtplib to be installed\n\n")
        sys.exit        
    try:
        sys.stdout.write('Python3 module - hashlib installed...')
        import hashlib
        sys.stdout.write('TRUE\n')
    except ModuleNotFoundError:
        sys.stdout.write('FALSE\n\n')
        sys.stdout.write("iComp Requires hashlib to be installed\n\n")
        sys.exit            
    try:
        sys.stdout.write('Python3 module - email.mime.multipart installed...')
        import email.mime.multipart
        sys.stdout.write('TRUE\n')
    except ModuleNotFoundError:
        sys.stdout.write('FALSE\n\n')
        sys.stdout.write("iComp Requires email.mime.multipart to be installed\n\n")
        sys.exit      
    try:
        sys.stdout.write('Python3 module - email.mime.text installed...')
        import email.mime.text
        sys.stdout.write('TRUE\n')
    except ModuleNotFoundError:
        sys.stdout.write('FALSE\n\n')
        sys.stdout.write("iComp Requires eemail.mime.text to be installed\n\n")
        sys.exit      
    try:
        sys.stdout.write('Python3 module - simplecrypt installed...')
        import simplecrypt
        sys.stdout.write('TRUE\n')
    except ModuleNotFoundError:
        sys.stdout.write('FALSE\n\n')
        sys.stdout.write("iComp Requires simplecrypt to be installed\n\n")
        sys.exit   


def makeiCompDirs():
    sys.stdout.write('\n\nMaking local dirs\n\n')
    for i in range(len(dirsToCreate)):
      try:
          sys.stdout.write("creating " + dirsToCreate[i] + "\n")
          os.makedirs(dirsToCreate[i], mode=0o755)
      except FileExistsError:
          pass
      except:
          raise


def buildApacheConf():
    sys.stdout.write("\n\nHTTPS Info\n\n")
    httpsOn = ""
    certLoc = ""
    keyLoc  = ""
    while httpsOn != "y" and httpsOn != "n":
        httpsOn = input("Using HTTPS (Recommended) [y/n]: ")
        if httpsOn.lower() != "y" and httpsOn.lower() != "n":
            sys.stdout.write("Invalid response.  [y/n]")
        else:
            pass
    
    if httpsOn == "y":
        certLoc = input("Cert Location:  ")
        keyLoc  = input("Key Location:  ")
    
    fh = open('./iCompWebFiles/etc/apache2/sites-available/iComp.conf','w')
    fh.write("<VirtualHost *:8001>\n")
    fh.write("\tServerAdmin webmaster@localhost\n")
    fh.write("\tDocumentRoot /var/www/iCompetition\n")
    if httpsOn == "y":
        fh.write("\tSSLEngine on\n")
        fh.write("\tSSLCertificateFile    " + certLoc + "\n")
        fh.write("\tSSLCertificateKeyFile " + keyLoc + "\n")
    fh.write("\tErrorLog ${APACHE_LOG_DIR}/error.log\n")
    fh.write("\tCustomLog ${APACHE_LOG_DIR}/access.log combined\n")
    fh.write("</VirtualHost>")
    fh.close()


def buildJSSharedVars():
    global domain
    global httpsPort
        
    domain    = input("What is your public facing url for this server?:  ")
    httpsPort = input("What is your public facing https port for this server?:  ")
    apiPort   = input("What is your public facing api port for this server?:  ")
    fh = open("./iCompWebFiles/var/www/iCompetition/js/iComp_sharedVars.js",'w')
    fh.write("htmlAddress  = \"" + domain + ":" + httpsPort + "/\"\n")
    fh.write("apiAddress = \"" + domain + ":" + apiPort + "/\"\n")
    fh.close()

def copyFiles():
    sys.stdout.write('\n\nCopying files to system\n\n')
    os.popen('cp ./iCompPythonFiles/usr/local/lib/iCompetition/api/* /usr/local/lib/iCompetition/api/')
    os.popen('cp -r ./iCompPythonFiles/usr/local/lib/iCompetition/python/* /usr/local/lib/iCompetition/python/')
    os.popen('cp -r ./iCompWebFiles/var/www/iCompetition/* /var/www/iCompetition/')
    os.popen('cp ./iCompWebFiles/etc/apache2/sites-available/iComp.conf /etc/apache2/sites-available/iComp.conf')
    os.popen('cp ./iCompSystemFiles/etc/profile.d/iComp.sh /etc/profile.d/iComp.sh')
    os.popen('cp ./iCompSystemFiles/etc/systemd/system/iCompApi.service /etc/systemd/system/iCompApi.service')
    os.popen('cp ./iComp_delete.py /usr/local/lib/iCompetition/')
    os.popen('a2ensite iComp.conf')
    os.popen('systemctl restart apache2')
    os.popen('systemctl daemon-reload')
    os.popen('systemctl enable iCompApi')


def getDbInfo():
    sys.path.append("/usr/local/lib/iCompetition/python")
    from iComp_util import iencrypt
    
    sys.stdout.write("\n\nDatabase Info\n\n")
    dblocation = input("DB Url or IP Addres:      ")
    dbport     = input("DB Port:                  ")
    dbname     = input("DB Name:                  ")
    roUser     = getpass.getpass("iCompRead User Password:  ")
    altUser    = getpass.getpass("iCompAlt  User Password:  ")
    
    fh = open('/etc/iCompetition/iComp.conf','w')
    fh.write('#Database Config\n')
    fh.write('database_location:' + dblocation + '\n')
    fh.write('database_port:' + dbport + '\n')
    fh.write('database_name:' + dbname + '\n')
    fh.close()

    pwdRO = iencrypt(roUser)
    fh = open('/etc/iCompetition/.creds/.iCompRead','wb')
    fh.write(pwdRO)
    fh.close()    

    pwdALT = iencrypt(altUser)
    fh = open('/etc/iCompetition/.creds/.iCompAlt','wb')
    fh.write(pwdALT)
    fh.close()        

def getEmailConf():
    emailAddr   = input("Enter password reset email address:   ")
    emailPwd    = input("Enter password reset email password:  ")
    emailDomain = input("Enter password reset email domain:    ")
    emailPort   = input("Enter password reset email port:      ")
    fh = open('/etc/iCompetition/iComp.conf','a')
    fh.write("#Send Email Config\n")
    fh.write('emailLink:' + domain + ':' + httpsPort + "\n")
    fh.write("sendEmailAddr:"   + emailAddr + "\n")
    fh.write("sendEmailPass:"   + emailPwd + "\n")
    fh.write("sendEmailDomain:" + emailDomain + "\n")
    fh.write("sendEmailPort:"   + emailPort + "\n")
    fh.close()
    

def addAdditionalConfig():
    global domain
    global httpsPort
    fh = open('/etc/iCompetition/iComp.conf','a')
    fh.write('#iCompetition Version\n')
    fh.write('version:' + installVersion + "\n")
    fh.write('#Bonus Points For Fast Lap Bonus\n')
    fh.write('fastLapBonusAmount:10\n')
    fh.close()


def main():
    CheckPrereq()
    makeiCompDirs()
    buildApacheConf()
    buildJSSharedVars()
    copyFiles()
    getDbInfo()
    getEmailConf()
    addAdditionalConfig()
    sys.stdout.write('\n\n')
    sys.stdout.write('iCompetition ' + installVersion + ' web application is now installed!\n')
    sys.stdout.write('A few notes: - \n')
    sys.stdout.write('\t - If this is a brand new installation of iComp, ensure you have completed the DB build.\n')
    sys.stdout.write('\t\t - See iComp_DB repository\n')
    sys.stdout.write('\t - The iCompApi can be started and stopped with iCompApi-up and iCompApi-down commands (You may need to log out and in first) or by using systemctl\n')
    sys.stdout.write('\t - ensure ports 8001 and 5000 are open on this server.  Ensure database ports are open if database exists on this server.\n')

if __name__ == '__main__':
    main()
