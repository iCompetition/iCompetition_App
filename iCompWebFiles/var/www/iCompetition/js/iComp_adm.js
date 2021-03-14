//adm menu related functions

function openAdmin(){
  passCheck = document.getElementById("passPromptPass").value;  
  const xhttp = new XMLHttpRequest();
  url = apiAddress + "iComp/users/login";
  xhttp.open("POST",url,false);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("userName=" + getCookie("userName") + "&password=" + passCheck);
  response = JSON.parse(xhttp.responseText);
  if (response.result == false){
    hideModal("passPromptModal");
    displayAlertDimissableInfo("Invalid Password");
  }else{
    setCookie("auth",response.token,1);
    window.location.replace("admin.html");
  }
}

function checkAdminStatus(){
  const xhttp = new XMLHttpRequest();
  url = apiAddress + "iComp/auth/adminStatus";
  try{
    xhttp.open("POST",url,false);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send("token=" + getCookie("auth") + "&un=" + getCookie("userName"));
    response = JSON.parse(xhttp.responseText);
  }catch{
    checkUser();
  } 
  if (response.result != true || getCookie("adm") != "Y"){
    checkUser();
  }
  else if (response.result == true || getCookie("adm") == "Y"){
    setCookie('atok',response.adminToken,1)
  }
    
}

function adm_listUsers(){
  header = document.getElementById("simpleListHeader");
  tbl    = document.getElementById("simpleListTable");
  const xhttp = new XMLHttpRequest();
  url = apiAddress + "iComp/admin/listUsers";
  xhttp.open("POST",url,false);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("auth=" + getCookie("atok"));
  response = JSON.parse(xhttp.responseText);
  if (response.result != true){
    displayAlertDimissableInfo("Token Invalid");
  }else{
    header.innerHTML = "Total Users: " + response.cnt;
    tbl.innerHTML = response.html;
    showModal("simpleListModal");
  }
}

function adm_listEvents(){
  header = document.getElementById("simpleListHeader");
  tbl    = document.getElementById("simpleListTable");
  const xhttp = new XMLHttpRequest();
  url = apiAddress + "iComp/admin/listEvents";
  xhttp.open("POST",url,false);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("auth=" + getCookie("atok"));
  response = JSON.parse(xhttp.responseText);
  if (response.result != true){
    displayAlertDimissableInfo("Token Invalid");
  }else{
    header.innerHTML = "Total Events: " + response.cnt;
    tbl.innerHTML = response.html;
    showModal("simpleListModal");
  }
}

function adm_listEvents_active(){
  header = document.getElementById("simpleListHeader");
  tbl    = document.getElementById("simpleListTable");
  const xhttp = new XMLHttpRequest();
  url = apiAddress + "iComp/admin/getActiveEvents";
  xhttp.open("POST",url,false);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("auth=" + getCookie("atok"));
  response = JSON.parse(xhttp.responseText);
  if (response.result != true){
    displayAlertDimissableInfo("Token Invalid");
  }else{
    header.innerHTML = "Total Events: " + response.cnt;
    tbl.innerHTML = response.html;
    showModal("simpleListModal");
  }
}

function adm_createEvent(){
  en  = document.getElementById("ce_ename").value;
  es  = document.getElementById("ce_sname").value;  
  w1  = document.getElementById("ce_wk1").value;  
  w2  = document.getElementById("ce_wk2").value;  
  w3  = document.getElementById("ce_wk3").value;  
  w4  = document.getElementById("ce_wk4").value;  
  w5  = document.getElementById("ce_wk5").value;  
  w6  = document.getElementById("ce_wk6").value;  
  w7  = document.getElementById("ce_wk7").value;  
  w8  = document.getElementById("ce_wk8").value;  
  w9  = document.getElementById("ce_wk9").value;  
  w10 = document.getElementById("ce_wk10").value;  
  w11 = document.getElementById("ce_wk11").value;  
  w12 = document.getElementById("ce_wk12").value;  
  w13 = document.getElementById("ce_wk13").value;  
  liveSel = document.getElementById("clive");
  live = liveSel.options[liveSel.selectedIndex].value;
  cars = document.getElementById("ce_car").value;  
  setFLB = document.getElementById("flb").value;
  setHCB = document.getElementById("hcb").value;
  
  if (w13 == ""){
    w13 = "norace";
  }
  
  const xhttp = new XMLHttpRequest();
  url = apiAddress + "/iComp/admin/createEvent";
  xhttp.open("POST",url,false);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("auth=" + getCookie("atok") + "&en=" + en + "&es=" + es + "&w1=" + w1 + "&w2=" + w2 + "&w3=" + w3 + "&w4=" + w4 + "&w5=" + w5 + "&w6=" + w6 + "&w7=" + w7 + "&w8=" + w8 + "&w9=" + w9 + "&w10="  + w10 + "&w11=" + w11 + "&w12=" + w12 + "&w13=" + w13 + "&live=" + live + "&cars=" + cars + "&fastLapBonus=" + setFLB + "&hardChargerBonus=" + setHCB);
  response = JSON.parse(xhttp.responseText);  
  
  if (response.result == true){
    hideModal("CE_modal");
    displayAlertDimissableInfo("Event Created");
  }else{
    hideModal("CE_modal");
    displayAlertDimissableInfo("Failed To Create Event: " + response.message);
  }
}

function adm_clearTokens(){
  const xhttp = new XMLHttpRequest();
  url = apiAddress + "/iComp/admin/clearTokens";
  xhttp.open("POST",url,false);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("auth=" + getCookie("atok"));
}


function adm_showInfoUserModal(){
  document.getElementById("SE_header").innerHTML = "GET USER INFO";
  document.getElementById("se_textbox").placeholder = "Enter username...";
  showModal("SE_modal");
}


function adm_getInfoForUser(userName){
  const xhttp = new XMLHttpRequest();
  url = apiAddress + "/iComp/admin/getUserInfo";
  xhttp.open("POST",url,false);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("auth=" + getCookie("atok") + "&un=" + userName)
  response = JSON.parse(xhttp.responseText);  
  if (response.result == true) {
    hideModal("SE_modal");
    document.getElementById("simpleListTable").innerHTML = response.html;
    showModal("simpleListModal");
  }
}


function adm_singleEntrySubmit(){
  type = document.getElementById("SE_header").innerHTML;
  if (type == "GET USER INFO"){
    un = document.getElementById("se_textbox").value;
    adm_getInfoForUser(un);
  }
}
  
  
function reviewChgReqs(){
  const xhttp = new XMLHttpRequest();
  url = apiAddress + "/iComp/event/modify/getList";
  xhttp.open("GET",url,false);
  xhttp.send(null)
  response = JSON.parse(xhttp.responseText);  
  if (response.cnt == 0){
    displayAlertDimissableInfo("No Requests");
  }else{
    document.getElementById("requestApprovalTabel").innerHTML = response.html;
    showModal("requestApprovalModal");
  }
}


function actOnChangeChg(reqNum,appDeny){
  appv = 2
  if (appDeny == true){appv = 0}
  else if (appDeny == false){appv = 1}
  
  const xhttp = new XMLHttpRequest();
  url = apiAddress + "/iComp/event/modify/respond";
  xhttp.open("POST",url,false);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("auth=" + getCookie("atok") + "&reqNum=" + reqNum + "&appv=" + appv)
  response = JSON.parse(xhttp.responseText);  
  if (response.success == true){
    displayAlertDimissableInfo("Action Completed");
    reviewChgReqs();
  }else{
    displayAlertDimissableInfo("Action Failed");
   }
   hideModal("requestApprovalModal")
}


function adm_finishEvent(evNum){
  const xhttp = new XMLHttpRequest();
  url = apiAddress + "iComp/admin/finishEvent";
  xhttp.open("POST",url,false);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("auth=" + getCookie("atok") + "&event=" + evNum);
  response = JSON.parse(xhttp.responseText);
  if (response.result == true){
    displayAlertDimissableInfo("Action Completed");
  }else{
    displayAlertDimissableInfo("Action Failed");
  }

  hideModal("simpleListModal")



}

















