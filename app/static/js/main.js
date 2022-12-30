//***************************//
//   Get cookie by keyword   //
//***************************//

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
};

//**********************//
//   Number of Credit   //
//**********************//

function getCredit(credit_div) {

    fetch("/getCredit", {
        method: 'GET',
        headers: {'X-Requested-With': 'XMLHttpRequest'}
    })
      .then(response => {
        return response.json();
      })
      .then(data => {
        console.log(data);
        credit_div.querySelector('#credit-number').innerHTML = 'Crédit: ' + data["credit"];
        credit_div.querySelector('#credit-required').innerHTML = 'Crédit nécessaire ' + data["book"];
        if (data["credit"] >= data["book"]) {
            credit_div.querySelector('#credit-not-enought').setAttribute("hidden", "");
            credit_div.querySelector('#credit-enought').removeAttribute("hidden");
        } else {
            credit_div.querySelector('#credit-enought').setAttribute("hidden", "");
            credit_div.querySelector('#credit-not-enought').removeAttribute("hidden");
        }
    });
};

var credit_div = document.getElementById("credit-div");

//***********************************************************//
//   Send create book form and actualize reservation table   //
//***********************************************************//

function sendForm(thisForm) {
    let formData = new FormData( thisForm );
    let action = thisForm.getAttribute('action');
    let x_csrf_token = getCookie("csrf_access_token");    
    
    displayRun(thisForm);
    
    fetch(action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'x-csrf-token': x_csrf_token
    }})
    .then(response => {
      return response.text();
    })
    .then(data => {
    console.log(data);
      if (data.trim() == 'OK') {
        thisForm.reset();
        thisForm.querySelector('#loading').hidden = true;
        thisForm.querySelector("#succes-response").hidden = false;
        getBooks(book_table);
        getCredit(credit_div);
    } else {
        throw new Error(data ? data : 'Form submission failed and no error message returned from: ' + action); 
      }
    })
    .catch((error) => {
      displayError(thisForm, error);
    });
};

function displayRun(thisForm) {
    thisForm.querySelector("#succes-response").hidden = true;
    thisForm.querySelector("#error-response").hidden = true;
    // ajouter element tournant
    thisForm.querySelector('#loading').hidden = false;
};

function displayError(thisForm, error) {
    // supprimer l'élément tournant
    thisForm.querySelector('#loading').hidden = true;
    thisForm.querySelector('#error-response').innerHTML = error;
    thisForm.querySelector('#error-response').hidden = false;
};

var book_form = document.getElementById("book-form");
var credit_form = document.getElementById("credit-form");

book_form.addEventListener("submit", function(event) {
    let thisForm = this;
    event.preventDefault();
    sendForm(thisForm);
});

credit_form.addEventListener("submit", function(event) {
    let thisForm = this;
    event.preventDefault();
    if (thisForm.querySelector("#credit-ask").value > 0) {
        sendForm(thisForm);    
    }
});

//******************//
//   Disable Book   //
//******************//

function disableBook(thisButton) {
    let x_csrf_token = getCookie("csrf_access_token");
    let id = thisButton.parentNode.parentNode.id;
    let thisTable = thisButton.parentNode.parentNode.parentNode.parentNode;
    
    let formData = new FormData();
    formData.append("id", id);

    fetch("/disablebook", {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'x-csrf-token': x_csrf_token
    }})
    .then(response => {
        return response.text();
    })
    .then(data => {
        console.log(data);
        if (data.trim() == "OK") {
            getBooks(thisTable);
            getCredit(credit_div);
        }
    })
    
}

//*********************************//
//   Get reservation of the user   //
//*********************************//

function getBooks(thisTable) {
    let tBody = thisTable.getElementsByTagName('tbody')[0];
    tBody.innerHTML = '';
    
    fetch("/getbooks", {
        method: 'GET',
        headers: {'X-Requested-With': 'XMLHttpRequest'}
    })
      .then(response => {
        return response.json();
      })
      .then(data => {
      //   thisForm.querySelector('.loading').classList.remove('d-block');
      console.log(data);
      data.forEach(element => {
        let newRow = tBody.insertRow(-1);
        newRow.classList.add("border-b", "border-gray-100", "bg-emerald-700", "dark:bg-gray-800", "dark:border-gray-700");
        newRow.id = element["id"];
        let keys = ["golf", "email", "password", "date", "start_time", "ideal_time", "end_time", "player2", "player3", "player4"];
        keys.forEach(key => {
            let newCell = newRow.insertCell(-1);
            newCell.classList.add("py-4", "px-6");
            newCell.innerHTML = element[key];
        });
        let newCell = newRow.insertCell(-1);
        newCell.classList.add("py-4", "px-6", "font-medium", "flex", "justify-center");
        // newCell.setAttribute('onclick', 'disableBook(this)');
        let supp = document.createElement("button");
        supp.setAttribute('onclick', 'disableBook(this)');
        supp.classList.add("text-white", "bg-red-700", "hover:bg-red-800", "focus:ring-4", "focus:outline-none", "focus:ring-red-300", "font-medium", "rounded-lg", "text-sm", "px-5", "py-2.5", "dark:focus:ring-red-800", "dark:hover:bg-red-700", "text-center", "mr-3", "md:mr-0", "dark:bg-red-600");
        supp.innerHTML = "Supprimer";
        // let supp = document.createTextNode("Supprimer");
        newCell.appendChild(supp);
      });
    //     if (data.trim() == ) {
          
    //   } else {
    //       throw new Error(data ? data : 'Form submission failed and no error message returned from: ' + action); 
    //     }
    //   })
    //   .catch((error) => {
    //     displayError(thisTable, error);
    });
};


var book_table = document.getElementById("book-table");

//*******************//
//   Logout Button   //
//*******************//

var logout_button = document.getElementById("logout-button");

logout_button.addEventListener("click", function(event) {
    let x_csrf_token = getCookie("csrf_access_token");

    fetch("/logout", {
        method: 'DELETE',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'x-csrf-token': x_csrf_token
        }
    })
    .then(response => {
        return response.text();
    })
    .then(data => {
        console.log(data.trim());
        if (data.trim() == 'OK') {
            window.location.replace("/");
        }
    })
});

//*****************//
//   Onload page   //
//*****************//

window.addEventListener("load", function(event) {
    getBooks(book_table);
    getCredit(credit_div);
});