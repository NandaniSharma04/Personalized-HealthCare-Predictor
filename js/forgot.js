document
.getElementById("forgotForm")
.addEventListener("submit", async function(e){


e.preventDefault();



let data = {


email:

document.getElementById("email").value,


password:

document.getElementById("newPassword").value


};




try{


let response = await fetch("/forgot",{


method:"POST",


headers:{


"Content-Type":"application/json"


},


body:JSON.stringify(data)



});





let result = await response.text();




if(response.ok)

{


alert("Password Updated Successfully");


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