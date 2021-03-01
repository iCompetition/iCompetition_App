#API Commands
alias iCompApi-up='systemctl start iCompApi'
alias iCompApi-down='systemctl stop iCompApi'
alias iCompApi-stat='systemctl status iCompApi'
alias iCompApi-showLogs='ls -la /var/log/iComp/'
#App Commands
alias iComp-version='python3 /usr/local/lib/iCompetition/python/scripts/displayICompVersion.py'
alias iComp-modifyUserAdmin='python3 /usr/local/lib/iCompetition/python/scripts/adminFlag.py'
alias iComp-deleteInstall='python3 /usr/local/lib/iCompetition/iComp_delete.py'
#Navigation Comands
alias iCompGo-install='cd /usr/local/lib/iCompetition'
alias iCompGo-config='cd /etc/iCompetition'
alias iCompGo-web='cd /var/www/iCompetition/'
alias iCompGo-log='cd /var/log/iComp/'
#Web Commands
alias iCompWeb-changeLoginImage="python3 /usr/local/lib/iCompetition/python/scripts/changeLoginPageImage.py"

