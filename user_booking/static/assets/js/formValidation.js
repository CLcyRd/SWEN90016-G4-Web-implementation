$(document).ready(function() {
    // Display error message
    function showError(message) {
        document.getElementById("messBox").style.display = "block";  // Show error message box
        $("#errorMess").html(message);  // Update error message content
        setTimeout(hidden, 2000);   // Hide message after 2 seconds
    }

    // Hide error message
    function hidden() {
        document.getElementById("messBox").style.display = "none";  // Hide error message box
    }

    // Check if email format is correct
    function testEmail(str) {
         var re = /^\w+@[0-9a-zA-Z]+\.[a-zA-Z]+$/;  // Regular expression for email
         return re.test(str);  // Check if the email matches the regular expression
    }
    
    // When clicking the "Send Email" button
    $("#sendEmail").click(
        function () {
        var email = $("input[name='email']").val();  // Get the email entered by the user

        if (email === "") {
            showError("Please enter correct email: " + email);  // Show error if email is empty
        } else {
            $.ajax({
                url: "/sign_up/reg/",  // Send request to server
                type: 'POST',  // Send data using POST method
                data: {
                    type: 'sendOTP',  // Request type for sending OTP
                    csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val(),  // Django CSRF token for security
                    email: email  // Email address
                },
                dataType: "json",  // Expect JSON response from server

                success:  // If server returns successfully
                function (reg) {
                    if (reg.state == false) {  // If there is an error on the server
                        showError(reg.errmsg);  // Display the error message
                    } else {
                        console.log(reg.state);  // Log success message
                        settime();  // Start countdown timer
                    }
                }
            });

            var btn_sendEmail = $("#sendEmail");
            var countdown = 5;
        
            // Countdown functionality
            function settime() {
                if (countdown === 0) {
                    btn_sendEmail.attr("disabled", false);  // Re-enable the button after countdown ends
                    btn_sendEmail.val("Get code");  // Reset the button text
                    countdown = 5;  // Reset the countdown
                    return;
                } else {
                    btn_sendEmail.attr("disabled", true);  // Disable button to prevent further clicks
                    btn_sendEmail.val("Send again (" + countdown + ")");  // Update button text with countdown
                    countdown--;  // Decrease countdown value
                }
                setTimeout(function () {
                    settime();  // Call the function every second to continue the countdown
                }, 1000);
            }
        }
    });

});