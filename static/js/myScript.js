
/* form actions */
function nameValidation(){
    console.log("test")
   var check1 = /^[-a-zA-Z-()]+(\s+[-a-zA-Z-()]+)*$/;
   var name1 = $("#login-username").val();
   
   if(name1==""){
       
       $("#nameError").html("This field is required!");
       return false;
   }else if(check1.test(name1)){
       $("#nameError").html("");
       return true;}
  }


    function checkStrength(password){ 
         var strength = 0 
         //if the password length is less than 6, return message. 
         if (password.length < 6) { 
             $('#result').removeClass() 
             $('#result').addClass('short') 
             return 'Too short' 
            } 
     //if length is 8 characters or more, increase strength value 
     if (password.length > 7) 
        strength += 1 
     //if password contains both lower and uppercase characters, increase strength value 
     if (password.match(/([a-z].*[A-Z])|([A-Z].*[a-z])/)) 
        strength += 1 
     //if it has numbers and characters, increase strength value 
     if (password.match(/([a-zA-Z])/) && password.match(/([0-9])/)) 
        strength += 1 
     //if it has one special character, increase strength value 
     if (password.match(/([!,%,&,@,#,$,^,*,?,_,~])/))
        strength += 1 
     //if it has two special characters, increase strength value 
     if (password.match(/(.*[!,%,&,@,#,$,^,*,?,_,~].*[!,",%,&,@,#,$,^,*,?,_,~])/)) 
        strength += 1 
     //now we have calculated strength value, we can return messages //if value is less than 2 
     
     if (strength < 2 ) 
     { 
        $('#result').removeClass() 
        $('#result').addClass('weak') 
        return 'Weak' } 
     else if (strength == 2 ) 
     { 
        $('#result').removeClass() 
        $('#result').addClass('good') 
        return 'Good'
     } 
     else { 
            $('#result').removeClass()
            $('#result').addClass('strong') 
            return 'Strong' 
        } 
    } 

$(document).ready(function(){
    $("#name").keyup(function(){
      nameValidation()
    });
    $('#password').keyup(function(){
        $('#result').html(checkStrength($('#password').val()))
    });

    $("#submit-form").submit((e)=>{
        e.preventDefault()
        if(nameValidation() &&emailValidation()&&phoneValidation()){
        $("#submitError").fadeOut();
    $.ajax({
        url:"https://script.google.com/macros/s/AKfycbxRvmz-TOzNZggP1Zq3NzP0ulJbvquNsUtVopH9cGvZSXf_tOtJHAwLhBFkFpz4bQOE/exec",
        data:$("#submit-form").serialize(),
        method:"post",
        success:function (response){
            swal("Form submitted successfully.").then(function(){
                window.location.reload()

            });
            // alert("submitted successfully.")
            //window.location.href="https://google.com"
        },
        error:function (err){
            alert("Something Error")
        }
    })}else{
        nameValidation() 
        emailValidation() 
        phoneValidation()
    }
})
  })