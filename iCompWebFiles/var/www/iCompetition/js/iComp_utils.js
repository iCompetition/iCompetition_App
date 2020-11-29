
//util functions

function hideModal(mName){
  $('#' + mName).modal('hide');
}

function showModal(mName){
  $('#' + mName).modal('show');
}

function displayAlertBox(message){
  var alertBox     = document.getElementById('alertbox');
  alertBox.innerHTML = message;
  alertBox.classList.remove("d-none");
}

function hideAlertBox(){
  var alertBox     = document.getElementById('alertbox');
  alertBox.classList.add("d-none");
}

function displayAlertBox2(message){
  var alertBox     = document.getElementById('alertbox2');
  alertBox.innerHTML = message;
  alertBox.classList.remove("d-none");
}

function hideAlertBox2(){
  var alertBox     = document.getElementById('alertbox2');
  alertBox.classList.add("d-none");
}

function displayAlertDimissableInfo(message){
  var alertBox     = document.getElementById('dismissibleAlertInfo');
  var alertBoxMes  = document.getElementById('disAlertInfoMes');
  alertBoxMes.innerHTML = message;
  alertBox.classList.remove("d-none");
}

function displayAlertDimissableWarn(message){
  var alertBox     = document.getElementById('dismissibleAlertWarn');
  var alertBoxMes  = document.getElementById('disAlertWarnMes');
  alertBox.innerHTML = message;
  alertBoxMes.classList.remove("d-none");
}

function getQueryVariable(variable)
{
       var query = window.location.search.substring(1);
       var vars = query.split("&");
       for (var i=0;i<vars.length;i++) {
               var pair = vars[i].split("=");
               if(pair[0] == variable){return pair[1];}
       }
       return(false);
}

function getVersionInfo(){
  const call = new XMLHttpRequest(),
    url = apiAddress + "iComp/version";
    call.open("GET",url,true);
    
    call.onload = function(){
                         response = JSON.parse(call.responseText);
                         toolTipText = "iCompetition " + response.version 
                         document.getElementById("versionTooltip").title = toolTipText; 
    }
    call.send(null);
}

function iCompServerCheck(){
  const call = new XMLHttpRequest(),
    url = apiAddress + "iComp/reachable";
    call.open("GET",url,true);
    call.onerror = function(){displayAlertDimissableInfo("iCompetition Servers Are Not Reachable At This Time");};
    call.send(null);
     
}