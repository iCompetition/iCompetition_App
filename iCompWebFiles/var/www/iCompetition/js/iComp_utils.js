
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

function randomFactoid(){
  phrase     = [
                "Kidney stones are tough to pass",
                "Powwwaaaa",
                "\"Speed has never killed anyone...suddenly becoming stationary,  that's what gets you\" -- Jeremy Clarkson",
                "\"The oval community is better than the road racing community\" -- Everybody ",
                "Just keep turning left",
                "BRAKES!",
                "To finish first, you must first finish",
                "DANGER TO MANIFOLD!",
                "NOOSSSSS",
                "Straight roads are for fast cars, turns are for fast drivers",
                "\"Racing makes heroin addiction look like a vague wish for something salty.\" -- Peter Egan",
                "Leiws Hamiltion is overrated....What?...Wanna fight about it!?",
                "\"The winner ain't the one with the fastest car, it's the one who refuses to lose.\" -- Dale Earnhardt",
                "\"Aerodynamics are for people who can't build engines\" -- Enzo Ferrari",
                "Enzo Ferrari was kind of a cry baby.  Donut did a podcast on it...check it out",
                "R.I.P Paul",
                "Saw a really old lady in a modded GTI the other day.  That was cool",
                "LOL - Miata",
                "\"I drive a cool civic\" is never a true statement",
                "Mitsubishi should bring back the eclipse....properly",
                "\"It's not a throttle-it's a detonator.\" -- Jeremy Clarkson",
                "Better luck next week",
                "iRace, iCrash, iCry",
                "Thank you for using iCompetition.  We know you don't have other choices and we welcome you to mediocrity",
                "Michael > LeBron",
                "\"Hard Charger\"....sounds kind of dirty when you think about it"
                ]
  pullIndex  = Math.floor(Math.random() * phrase.length);
  document.getElementById("randomText").innerHTML = phrase[pullIndex];
}