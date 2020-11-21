//user menu functions

function loadUserPage(){
  const authCheck = new XMLHttpRequest();
  authCheckurl = apiAddress + "iComp/auth/checkToken";
  authCheck.open("POST",authCheckurl,false);
  authCheck.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  authCheck.send("token=" + getCookie("auth"));
  authCheckresponse = JSON.parse(authCheck.responseText);
  if (authCheckresponse.result != true){
    logOut();
    window.location.replace(htmlAddress + "login.html");
    }
  else if ((getCookie("userName") == null) || (getCookie("userName") == "") || (getCookie("userName") == "none")){
    window.location.replace(htmlAddress + "login.html");
    }
  else{
    const getBaseUserInfo = new XMLHttpRequest(),
      getBaseUserInfourl = apiAddress + "iComp/users/getUserInfo?userName=" + getCookie("userName") + "&token=" + getCookie("auth");
      getBaseUserInfo.open("GET",getBaseUserInfourl,false);
      getBaseUserInfo.send(null);
      responseUI = JSON.parse(getBaseUserInfo.responseText);   
    document.getElementById("um_usertd").innerHTML  = getCookie("userName");
    document.getElementById("um_fnametd").innerHTML = responseUI.firstName;
    document.getElementById("um_lnametd").innerHTML = responseUI.lastName;
    document.getElementById("um_numtd").innerHTML   = responseUI.userNum;
    setCookie("userNum",responseUI.userNum,7);
    if (responseUI.admin == "Y"){
      var adminButton = document.createElement("div");
      adminButton.innerHTML = '<button class="mt-2 btn btn-outline-primary btn-sm w-100" onClick="showModal(\'passPromptModal\');">Admin</button>';
      document.getElementById("userBaseInfoDiv").appendChild(adminButton);
      setCookie("adm","Y",7);
    }
    const getLiveEventInfo = new XMLHttpRequest(),
      getLiveEventInfourl = apiAddress + "iComp/events/getLiveEvents?userName=" + getCookie("userName") + "&token=" + getCookie("auth");
      getBaseUserInfo.open("GET",getLiveEventInfourl,false);
      getBaseUserInfo.send(null);
      responseEI = JSON.parse(getBaseUserInfo.responseText);         
      if (responseEI.result == true){
          list = document.getElementById("eventReg_eventSel");
          list.innerHTML = "<option>Select Event...</option>" + responseEI.html;
      } 
      
    const checkForEventCount = new XMLHttpRequest(),
      method2 = "GET",
      url2 = apiAddress + "iComp/events/eventCountCheck?userName=" + getCookie("userName") + "&token=" + getCookie("auth");
      checkForEventCount.open(method2,url2,false);
      checkForEventCount.send(null);
      response = JSON.parse(checkForEventCount.responseText);
      if (response.result == false){
        var noEventMes = document.createElement("div");
        noEventMes.innerHTML = '<h4>\'' + getCookie("userName") + '\' Is Not Registered For Any Events</h4>';
        document.getElementById("eventTableDiv").appendChild(noEventMes);
      }else{
        document.getElementById("logScoreBut").classList.remove('disabled');
        const eventListApi = new XMLHttpRequest(),
          eventListApiurl = apiAddress + "iComp/events/pullRegisteredEvents?userName=" + getCookie("userName") + "&token=" + getCookie("auth");
          eventListApi.open("GET",eventListApiurl,false);
          eventListApi.send(null);
          responseEL = JSON.parse(eventListApi.responseText);
          eTableDiv = document.getElementById("eventTableDiv")
          eTableDiv.innerHTML = eTableDiv.innerHTML + responseEL.html;
          eScoreSelect = document.getElementById("score_eventSel");
          eScoreSelect.innerHTML = eScoreSelect.innerHTML + responseEL.html2;
      }
  }
}

function getCarsForEvent(){
  eventSel = document.getElementById("eventReg_eventSel");
  eventNum = eventSel.options[eventSel.selectedIndex].value
  const call = new XMLHttpRequest(),
    url = apiAddress + "iComp/events/getEventCars?eventNum=" + eventNum;
    call.open("GET",url,false);
    call.send(null);
    response = JSON.parse(call.responseText);
  carList = document.getElementById("eventReg_carSel");
  carList.innerHTML = response.html;
  carList.disabled = false;
}

function registerForEvent(){
  eventSel = document.getElementById("eventReg_eventSel");
  carSel   = document.getElementById("eventReg_carSel");
  
  evNum = eventSel.options[eventSel.selectedIndex].value
  uName = getCookie("userName");
  uNum = getCookie("userNum");
  car   = carSel.options[carSel.selectedIndex].value
  
  const call = new XMLHttpRequest(),
    url = apiAddress + "iComp/events/registerForEvent?eventNum=" + evNum + "&userName=" + uName + "&userNum=" + uNum + "&car=" + car + "&token=" + getCookie("auth");
    call.open("GET",url,false);
    call.send(null);
    response = JSON.parse(call.responseText);
  
  if (response.result == true){
    hideModal("eventRegModal");
    document.getElementById("logScoreBut").classList.remove('disabled');
    alert("You are registered for " + eventSel.options[eventSel.selectedIndex].innerHTML);
    window.location.reload();
  }else{alert("Failed to register for event");}
}


function getWkSchduleForEvent(){
  uName  = getCookie("userName")
  eNumEl = document.getElementById("score_eventSel");
  evNum  = eNumEl.options[eNumEl.selectedIndex].value;
  wkSel = document.getElementById("score_weekSel");
  
  const call = new XMLHttpRequest(),
  url = apiAddress + "iComp/events/schedule/getUserUnscoredWks?eventNum=" + evNum + "&userName=" + uName;
  call.open("GET",url,false);
  call.send(null);
  response = JSON.parse(call.responseText);
  
  
  if (evNum  = eNumEl.options[eNumEl.selectedIndex].innerHTML != "Select Event..."){
    wkSel.innerHTML = "<option value=''>Select Week...</option>" + response.html;
    wkSel.disabled = false;
  }else{
    wkSel.disabled = true;    
  }
}
  
function enableScoreInputs(){
  wkSel = document.getElementById("score_weekSel");
  wkSelChoice = wkSel.options[wkSel.selectedIndex].innerHTML;
  
  if (wkSelChoice != "Select Week..."){
    document.getElementById("score_position").disabled = false;
    document.getElementById("score_points").disabled = false;
    document.getElementById("score_inc").disabled = false;
  }else{
    document.getElementById("score_position").disabled = true;
    document.getElementById("score_points").disabled = true;
    document.getElementById("score_inc").disabled = true;
  }
}
  
function logScore(){
  eSel = document.getElementById("score_eventSel");
  wSel = document.getElementById("score_weekSel");
  
  en  = eSel.options[eSel.selectedIndex].value;
  wn  = wSel.options[wSel.selectedIndex].value;
  pos = document.getElementById("score_position").value;
  pnt = document.getElementById("score_points").value;
  inc = document.getElementById("score_inc").value;
  un  = getCookie("userNum");
  
  const call = new XMLHttpRequest(),
  url = apiAddress + "iComp/events/logScore?userNum=" + un + "&eventNum=" + en + "&wkNum=" + wn + "&pos=" + pos + "&pnt=" + pnt + "&inc=" + inc + "&token=" + getCookie("auth");
  call.open("GET",url,false);
  call.send(null);
  response = JSON.parse(call.responseText);
  
  if (response.result == true){
    hideModal('scoreLoggingModal');
    displayAlertDimissableInfo("Your Score Has Been Logged!");
    eSel.selectedIndex = 0
    wSel.selectedIndex = 0
  }else{
    hideModal('scoreLoggingModal');
    displayAlertDimissableInfo("Error Logging Score: " + response.message );
  } 
  
  document.getElementById("score_position").value = "";
  document.getElementById("score_points").value = "";
  document.getElementById("score_inc").value = "";  
  wSel.innerHTML.value = "";
  wkSel.disabled = true; 
  
}

function eventDetail(eventNum){
  rankingTable  = document.getElementById("eventDetailRankTable");
  scheduleTable = document.getElementById("eventDetailScheduleTable");
  eventNameLbl  = document.getElementById("evDetailTitle");
  seriesNameLbl = document.getElementById("evDetailSeries");
  drSelDropDown = document.getElementById("eventDetailNameSel");
  
  const call = new XMLHttpRequest(),
  url = apiAddress + "iComp/events/pullDetails?eventNum=" + eventNum + "&userNum=" + getCookie("userNum") + "&currentUserNum=" + getCookie("userNum");
  call.open("GET",url,false);
  call.send(null);
  response = JSON.parse(call.responseText);  
  
  rankingTable.innerHTML  = response.rankings;
  scheduleTable.innerHTML = response.schedule;
  eventNameLbl.innerHTML = response.eventName;
  seriesNameLbl.innerHTML = response.eventSeries;
  drSelDropDown.innerHTML = response.driverSelect;
  showModal("eventDetailModal");
  setCookie('lastViewedEvent',eventNum,100);
  }
  
function checkForAvaEvents(){
  const call = new XMLHttpRequest(),
  url = apiAddress + "iComp/events/getLiveEvents?userName=" + getCookie("userName") + "&token=" + getCookie("auth");
  call.open("GET",url,false);
  call.send(null);
  responseEI = JSON.parse(call.responseText);         
  if (responseEI.result == true){
    showModal("eventRegModal");
  }else{
    displayAlertDimissableInfo("No Events To Register For");
  }
}

function updateWeeksForDriverSelect(){
  drSelDropDown = document.getElementById("eventDetailNameSel");
  scheduleTable = document.getElementById("eventDetailScheduleTable");
  userNum = drSelDropDown.options[drSelDropDown.selectedIndex].value;
  
  const call = new XMLHttpRequest(),
  url = apiAddress + "iComp/events/pullDetails?eventNum=" + getCookie("lastViewedEvent") + "&userNum=" + userNum + "&currentUserNum=" + getCookie("userNum");
  call.open("GET",url,false);
  call.send(null);
  response = JSON.parse(call.responseText);  
  scheduleTable.innerHTML = response.schedule;
}


function startScoreModify(eventNum,userNum,week){
  ms_userName   = document.getElementById("ms_userName");
  ms_eventTitle = document.getElementById("ms_eventTitle");
  ms_weekTitle  = document.getElementById("ms_weekTitle");
  ms_curPos     = document.getElementById("ms_curPos");
  ms_curPnt     = document.getElementById("ms_curPnt");
  ms_curinc     = document.getElementById("ms_curinc");
  ms_newPos     = document.getElementById("ms_position");
  ms_newPnt     = document.getElementById("ms_points");
  ms_newinc     = document.getElementById("ms_inc");
  
  const call = new XMLHttpRequest(),
  url = apiAddress + "iComp/event/modify/getResultsPreModify?token=" + getCookie("auth") + "&eventNum=" + eventNum + "&userNum=" + userNum + "&week=" + week;
  call.open("GET",url,false);
  call.send(null);
  response = JSON.parse(call.responseText);  
  if (response.success == true) {
    ms_userName.innerHTML   = response.userName
    ms_eventTitle.innerHTML = response.eventName
    ms_weekTitle.innerHTML  = response.track
    ms_curPos.innerHTML     = response.position
    ms_curPnt.innerHTML     = response.points
    ms_curinc.innerHTML     = response.inc
    ms_newPos.disabled      = false;
    ms_newPnt.disabled      = false;
    ms_newinc.disabled      = false;
    setCookie('tmp_reqChg_eventNum',eventNum,100);
    setCookie('tmp_reqChg_userNum',userNum,100);
    setCookie('tmp_reqChg_wkNum',week,100);
    showModal("scoreModifyModal");
    hideModal("eventDetailModal");
  }else{
    displayAlertDimissableInfo("Failed to pull data from server");
  }
}


function reqScoreChange(){
  ms_newPos     = document.getElementById("ms_position");
  ms_newPnt     = document.getElementById("ms_points");
  ms_newinc     = document.getElementById("ms_inc");
  
  newPnt   = ms_newPnt.value;
  newPos   = ms_newPos.value;
  newInc   = ms_newinc.value;
  eventNum = getCookie('tmp_reqChg_eventNum');
  userNum  = getCookie('tmp_reqChg_userNum');
  weekNum  = getCookie('tmp_reqChg_wkNum');
  
  const call = new XMLHttpRequest(),
  url = apiAddress + "iComp/event/modify/reqChange?token=" + getCookie("auth") + "&eventNum=" + eventNum + "&userNum=" + userNum + "&week=" + weekNum + "&pnt=" + newPnt+ "&pos=" + newPos+ "&inc=" + newInc;
  call.open("GET",url,false);
  call.send(null);
  response = JSON.parse(call.responseText);    
  if (response.success == true) {
    displayAlertDimissableInfo("Change request sent for review");
  }else{
    displayAlertDimissableInfo("Failed...");
  }
  
  hideModal("scoreModifyModal");
  deleteCookie('tmp_reqChg_eventNum');
  deleteCookie('tmp_reqChg_userNum');
  deleteCookie('tmp_reqChg_wkNum');
  ms_newPos.value = '';
  ms_newPnt.value = '';
  ms_newinc.value = '';
}


function readyPasswordChange(){
  if (document.getElementById("acctConfigEmailChgBoxes").classList.contains('d-none') == false){
    document.getElementById("acctConfigEmailChgBoxes").classList.add('d-none');
  }
  if (document.getElementById("acctConfig_submitEmailButton").classList.contains('d-none') == false){
    document.getElementById("acctConfig_submitEmailButton").classList.add('d-none');
  }
  document.getElementById("acctConfigPassChgBoxes").classList.remove('d-none');
  document.getElementById("acctConfig_submitPassButton").classList.remove('d-none');
  document.getElementById("acctConfigResetPassButton").disabled = true;
  document.getElementById("acctConfigResetEmailButton").disabled = false;
}

function readyEmailChange(){
  if (document.getElementById("acctConfigPassChgBoxes").classList.contains('d-none') == false){
    document.getElementById("acctConfigPassChgBoxes").classList.add('d-none');
  }
  if (document.getElementById("acctConfig_submitPassButton").classList.contains('d-none') == false){
    document.getElementById("acctConfig_submitPassButton").classList.add('d-none');
  }
  document.getElementById("acctConfigEmailChgBoxes").classList.remove('d-none');
  document.getElementById("acctConfig_submitEmailButton").classList.remove('d-none');
  document.getElementById("acctConfigResetEmailButton").disabled = true;
  document.getElementById("acctConfigResetPassButton").disabled = false;
}

function closeAcctConfigModal(){
  document.getElementById("acctConfigPassChgBoxes").classList.add('d-none');
  document.getElementById("acctConfigEmailChgBoxes").classList.add('d-none');
  document.getElementById("acctConfig_submitPassButton").classList.add('d-none');
  document.getElementById("acctConfig_submitEmailButton").classList.add('d-none');
  document.getElementById("acctConfigResetPassButton").disabled = false;
  document.getElementById("acctConfigResetEmailButton").disabled = false;
  document.getElementById("passChange_Current").value = "";
  document.getElementById("passChange_new").value = "";
  document.getElementById("passChange_new_conf").value = "";
  document.getElementById("emailChange_pass").value = "";
  document.getElementById("emailChange_new").value = "";
  document.getElementById("emailChange_new_conf").value = "";
  hideModal("acctConfigModal");
}