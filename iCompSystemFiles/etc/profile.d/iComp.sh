#API Commands
alias iComp-apiUp='systemctl start iCompApi.service && systemctl start iCompToken.timer'
alias iComp-apiDown='systemctl stop iCompApi.service && systemctl stop iCompToken.service && systemctl stop iCompToken.timer'
alias iComp-apiStatus='systemctl status iCompApi.service && systemctl status iCompToken.timer'
#App Commands
alias iComp-version='python3 /usr/local/lib/iCompetition/python/scripts/displayICompVersion.py'
alias iComp-modifyUserAdmin='python3 /usr/local/lib/iCompetition/python/scripts/adminFlag.py'
alias iComp-chgDbPwd='python3 /usr/local/lib/iCompetition/python/scripts/databasePasswordUtil.py'
alias iComp-deleteInstall='python3 /usr/local/lib/iCompetition/iComp_delete.py'
alias iComp-checkForUpdate='python3 /usr/local/lib/iCompetition/python/scripts/updater.py listVersions'
alias iComp-updateToVersion='python3 /usr/local/lib/iCompetition/python/scripts/updater.py update --version'
#Navigation Comands
alias iComp-goToInstall='cd /usr/local/lib/iCompetition'
alias iComp-gotoConfig='cd /etc/iCompetition'
alias iComp-gotoWeb='cd /var/www/iCompetition/'
alias iComp-gotoLog='cd /var/log/iComp/'
#Web Commands
alias iComp-changeLoginImage="python3 /usr/local/lib/iCompetition/python/scripts/changeLoginPageImage.py"
#Util Commands
alias iComp-showLogs='ls -la /var/log/iComp/'
alias iComp-purgeExpiredTokens='python3 /usr/local/lib/iCompetition/python/scripts/tokenCleanup.py'
##Funciton Commands
alias iComp-function-enable='python3 /usr/local/lib/iCompetition/python/scripts/functionEnablement.py enable'
alias iComp-function-disable='python3 /usr/local/lib/iCompetition/python/scripts/functionEnablement.py disable'
alias iComp-function-status='python3 /usr/local/lib/iCompetition/python/scripts/functionEnablement.py status'
