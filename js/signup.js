document
.getElementById("signupForm")
.addEventListener("submit", async function(e){

e.preventDefault();


let user = {

name: document.getElementById("name").value,

email: document.getElementById("email").value,

password: document.getElementById("password").value

};



try{


let response = await fetch("/signup",{

method:"POST",

headers:{

"Content-Type":"application/json"

},

body:JSON.stringify(user)

});



let result = await response.text();



if(response.ok)

{

alert("Account Created Successfully");


window.location.href="login.html";


}

else

{

alert(result);

}



}

catch(error)

{

alert("Server is not running");

}



});