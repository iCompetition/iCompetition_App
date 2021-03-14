//User / usermanagement related functions

function userRegister(){
  var userName     = document.getElementById('reg_uName');
  var firstName    = document.getElementById('reg_fName');
  var lastName     = document.getElementById('reg_lName');
  var password     = document.getElementById('reg_pwd');
  var passwordc    = document.getElementById('reg_pwdconf');
  var email        = document.getElementById('reg_email');
  var v_un    = userName.value;
  var v_fn    = firstName.value;
  var v_ln    = lastName.value;
  var v_pwd   = password.value;
  var v_pwdc  = passwordc.value;
  var v_email = email.value;
  if (v_pwd != v_pwdc){
    displayAlertBox("Password Values Do Not Match");
  }else{
      const xhttp = new XMLHttpRequest();
      url = apiAddress + "iComp/users/createUser";
      xhttp.open("POST",url,false);
      xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
      xhttp.send("userName=" + v_un + "&firstName=" + v_fn + "&lastName=" + v_ln + "&password=" + v_pwd + "&email=" + v_email);
      response = JSON.parse(xhttp.responseText);
      if(response.result == true){
        setCookie("userName",v_un,7)
        alert("User Created");
        checkUser();
      }
      else{displayAlertBox(response.message);}
  }
}

function userLogin(){
  var userName    = document.getElementById('login_uName');
  var password    = document.getElementById('login_pwd');
  var v_un  = userName.value;
  var v_pwd = password.value;
  
  const xhttp = new XMLHttpRequest();
  url = apiAddress + "iComp/users/login";
  xhttp.open("POST",url,false);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("userName=" + v_un + "&password=" + v_pwd);
  response = JSON.parse(xhttp.responseText);
  if(response.result == true){
    setCookie("userName",v_un,7);
    setCookie("auth",response.token,7);
    checkUser();
  }
  else{displayAlertBox(response.message); }
}

function checkUser(){
  if ((getCookie("userName") == null) || (getCookie("userName") == "") || (getCookie("userName") == "none")){
    window.location.replace(htmlAddress + "login.html")
  }else{
    window.location.replace(htmlAddress + "userMenu.html")
  }   
}

function logOut(){
   deleteCookie("userName");
   deleteCookie("userNum");
   deleteCookie("auth");
   deleteCookie("adm");
   deleteCookie("atok");
   deleteCookie("lastViewedEvent");
   window.location.replace(htmlAddress + "login.html");
}

function requestPasswordReset(){
  var userName    = document.getElementById('login_uName');
  var subButton    = document.getElementById('subButton');
  var v_un  = userName.value;   
  const xhttp = new XMLHttpRequest();
  url = apiAddress + "iComp/users/requestPassReset?userName=" + v_un;
  xhttp.open("GET",url,false);
  xhttp.send(null);
  userName.classList.add("d-none");
  subButton.classList.add("d-none");
  displayAlertBox("A reset link will be emailed to the address used during registration");
}

function validatePassResetLink(){
  token = getQueryVariable("validation");
  un = getQueryVariable("userName");
  const xhttp = new XMLHttpRequest();
  url = apiAddress + "iComp/auth/checkResetToken";
  xhttp.open("POST",url,false);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("token=" + token);
  response = JSON.parse(xhttp.responseText);
  if (response.result == true){
    pwdForm = document.getElementById("pwdResetForm")
    pwdForm.classList.remove("d-none");
    document.getElementById("pwdResetUserName").innerHTML = un
  }else{displayAlertBox("Reset Link Has Expired");}
}

function resetPasswordForUser(){
  token = getQueryVariable("validation");
  un = getQueryVariable("userName");
  pwdBox1 = document.getElementById("pwdReset_one");
  pwdBox2 = document.getElementById("pwdReset_two");
  unh = document.getElementById("unholder");
  rpb = document.getElementById("rpassbut");
  rtnLogin = document.getElementById("returnToLogin");
  if (pwdBox1.value != pwdBox2.value){
    displayAlertBox("Password and Confirm Password Do Not Match");
  }else{
    pwd = pwdBox1.value;
    const rPwdCall = new XMLHttpRequest();
    rPwdCallurl = apiAddress + "iComp/users/resetPassword";
    rPwdCall.open("POST",rPwdCallurl,false);
    rPwdCall.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    rPwdCall.send("userName=" + un + "&token=" + token + "&pw=" + pwd);
    rPwdCallresponse = JSON.parse(rPwdCall.responseText);    
    if (rPwdCallresponse.result == true){
      displayAlertBox2("Password Has Been Reset");
      pwdBox1.classList.add("d-none");
      pwdBox2.classList.add("d-none");
      unh.classList.add("d-none");
      rpb.classList.add("d-none");
      rtnLogin.classList.remove("d-none");
    }else{displayAlertBox("Could Not Change Password")};
  }
}

function submitPassChg(){
  curPass     = document.getElementById("passChange_Current").value;
  newPass     = document.getElementById("passChange_new").value;
  newPassConf = document.getElementById("passChange_new_conf").value;
  userName    = getCookie("userName");
  token = getCookie("auth");
  if (newPass != newPassConf){
    alert("Password and Confirm Password Do Not Match");
  }else{
    const xhttp = new XMLHttpRequest();
      url = apiAddress + "iComp/users/changePassword";
      xhttp.open("POST",url,false);
      xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
      xhttp.send("auth=" + token + "&userName=" + userName + "&curPass=" + curPass + "&newPass=" + newPass);
      response = JSON.parse(xhttp.responseText);    
    if (response.success == true){
      displayAlertDimissableInfo("Password Changed");
    }else{
      displayAlertDimissableInfo(response.message);
    }
  }
  closeAcctConfigModal();
}

function submitEmailChg(){
  curPass      = document.getElementById("emailChange_pass").value;
  newEmail     = document.getElementById("emailChange_new").value;
  newEmailConf = document.getElementById("emailChange_new_conf").value;
  userName     = getCookie("userName");
  token = getCookie("auth");
  if (newEmail != newEmailConf){
    alert("Email and Confirm Email Do Not Match");
  }else{
    const xhttp = new XMLHttpRequest();
      url = apiAddress + "iComp/users/changeEmail";
      xhttp.open("POST",url,false);
      xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
      xhttp.send("auth=" + token + "&userName=" + userName + "&pass=" + curPass + "&newEmail=" + newEmail);
      response = JSON.parse(xhttp.responseText);    
    if (response.success == true){
      displayAlertDimissableInfo("Email Changed");
    }else{
      displayAlertDimissableInfo(response.message);
    }
  }
  closeAcctConfigModal();
}
