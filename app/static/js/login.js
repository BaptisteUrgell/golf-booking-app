//*****************************************************//
//              Switch signIn/signUp section           //
//*****************************************************//

var login_section = document.getElementById("login-section");
var create_section = document.getElementById("create-section");
var go_signup = document.getElementById("go-signup");
var go_signin = document.getElementById("go-signin");

function switch_section(){
    login_section.hidden = !login_section.hidden;
    create_section.hidden = !create_section.hidden;
}

go_signup.onclick = switch_section;
go_signin.onclick = switch_section;

//*****************************************************//
//              Check confirm-password                 //
//*****************************************************//

var create_password = document.getElementById("create-password");
var confirm_password = document.getElementById("confirm-password");

function validatePassword(){
  if(create_password.value != confirm_password.value) {
    confirm_password.setCustomValidity("Passwords Don't Match");
  } else {
    confirm_password.setCustomValidity('');
  }
}

create_password.onchange = validatePassword;
confirm_password.onkeyup = validatePassword;

//*****************************************************//
//   Send create account form and actualize the page   //
//*****************************************************//

function sendForm(thisForm) {
    let formData = new FormData( thisForm );
    let action = thisForm.getAttribute('action');

    displayRun(thisForm);
    console.log("sending form");

    fetch(action, {
      method: 'POST',
      body: formData,
      headers: {'X-Requested-With': 'XMLHttpRequest'}
    })
    .then(response => {
      return response.text();
    })
    .then(data => {
    //   thisForm.querySelector('.loading').classList.remove('d-block');
    console.log(data);
      if (data.trim() == 'OK') {
        thisForm.reset();
        window.location.replace("/");
    } else {
        throw new Error(data ? data : 'Form submission failed and no error message returned from: ' + action); 
      }
    })
    .catch((error) => {
      displayError(thisForm, error);
    });
}

function displayRun(thisForm) {
    // thisForm.querySelector("#succes-response").hidden = true;
    thisForm.querySelector("#error-response").hidden = true;
    thisForm.querySelector('#loading').hidden = false;
}

function displayError(thisForm, error) {
    // supprimer l'élément tournant
    thisForm.querySelector('#loading').hidden = true;
    thisForm.querySelector('#error-response').innerHTML = error;
    thisForm.querySelector('#error-response').hidden = false;
}

var create_form = document.getElementById("create-form");

create_form.addEventListener("submit", function(event) {
    let thisForm = this;

    event.preventDefault();
    sendForm(thisForm);
});

var login_form = document.getElementById("login-form");

login_form.addEventListener("submit", function(event) {
    let thisForm = this;
    event.preventDefault();
    sendForm(thisForm);
});

//*****************//
//   Onload page   //
//*****************//

window.addEventListener("load", function(event) {
    login_form.querySelector('#loading');
});