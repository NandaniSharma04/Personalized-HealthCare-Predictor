document
.getElementById("loginForm")
.addEventListener("submit", async function(e){

e.preventDefault();


let loginData = {

    email: document.getElementById("email").value,

    password: document.getElementById("password").value

};



try {


let response = await fetch("/login", {

    method:"POST",

    headers:{

        "Content-Type":"application/json"

    },

    body:JSON.stringify(loginData)

});




if(response.ok)

{


let user = await response.json();


// save current login session

localStorage.setItem(

    "currentUser",

    JSON.stringify(user)

);



window.location.href="index.html";


}

else

{


alert("Invalid Email or Password");


}



}

catch(error)

{


alert("Server is not running. Start server.py first");


}



});