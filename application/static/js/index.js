

//Login Button Click
$("#login").click(function (e) {
    e.preventDefault();
    closeMenu();
    openLogin();
});

//$("#verify-submit").click(function(e){
//     closeVerifyPage(e);
// })



$("#login-desktop").click(function (e) {
    e.preventDefault();
    openLogin();
});

// Mobile close
$("#x-mobile").click(function (e) {
    e.preventDefault();
    closeMobile();
});

// Verify Close
$("#x-verify").click(function (e) {
    e.preventDefault();
    closeVerifyPage();
});

//Login close
$("#x").click(function (e) {
    e.preventDefault();
    closeLogin();
});

//signup close
$("#x-signup").click(function (e) {
    e.preventDefault();
    closeSignup();
});

//Signup Button Click
$("#signup").click(function (e) {
    e.preventDefault();
    closeMenu();
    openSignup();
});

$("#signup-desktop").click(function (e) {
    e.preventDefault();
    openSignup();
});

$("#signup-main").click(function (e) {
    e.preventDefault();
    openSignup();
});


// Toggle Menu
$("#ham").click(function (e) {
    e.preventDefault();
    openMenu();
});

$("#x-menu").click(function (e) {
    e.preventDefault();
    closeMenu();
});


$("#mobile-cover").click(function (e) {
    e.preventDefault();
    closeMenu();
});

//Open signup
$("#signup-link").click(function (e) {
    e.preventDefault();
    closeLogin();
    openSignup();
})

$("#login-link").click(function (e) {
    e.preventDefault();
    closeSignup();
    openLogin();
})

$("#go-to-login").click(function (e) {
    e.preventDefault();
    openLogin()
})

// Functions
function openMobileForm(e) {
    $(".pid").html(e.target.id);
    $("#mobile-page").addClass("show");
    $("#confirm-form").css("display", "none");
    $("#verify-form").css("display", "none");
    $("#mobile-form").css("display", "block");
    $("#x-mobile").css("display", "block");
}

function closeMobile() {
    $("#mobile-form").css("display", "none");
    $("#x-mobile").css("display", "none");
    $("#mobile-page").removeClass("show");
}

function openVerifyPage() {
    $("#mobile-form").css("display", "none");
    $("#verify-form").css("display", "block");
}

function openConfirmPage() {
    $("#verify-form").css("display", "none");
    $("#confirm-form").css("display", "block");
}

function openSignup() {
    $("#signup-page").addClass("show");
    $("#x-signup").css("display", "block");
}

function openLogin() {
    $("#login-page").addClass("show");
    $("#x").css("display", "block");
}

function openMenu() {
    $("#mobile-cover").addClass("show");
    $("#mobile-menu").addClass("show");
    $("#x-menu").css("display", "block");
}

function closeSignup() {
    $("#signup-page").removeClass("show");
    $("#x-signup").css("display", "none");
}

function closeLogin() {
    $("#login-page").removeClass("show");
    $("#x").css("display", "none");
}
function closeMenu() {
    $("#mobile-cover").removeClass("show");
    $("#mobile-menu").removeClass("show");
    $("#x-menu").css("display", "none");
}



/**
 * Global loader function
 */
$(document).bind("ajaxSend", function () {
    $('#loading').show();
}).bind("ajaxComplete", function () {
    $("#loading").hide();
});




/**
 * Signup submit
 */
$("#signup-form").submit(function (e) {
    e.preventDefault();
    register();
})
function register() {
    var username = $("#name-signup").val();
    var email = $("#email-signup").val();
    var password = $("#password-signup").val();
    var repassword = $("#repassword-signup").val();
    if (isValidDetails(username, email, password, repassword)) {
        return;
    }
    $.ajax({
        url: "/register",
        type: "POST",
        contentType: "application/json",
        crossDomain: true,
        global: true,
        data: JSON.stringify({ username: username, email: email, password: password, repassword: repassword }),
        success: function (data) {
            displayAlert('success', 90000);
            $("#return-message").html(data);
        },
        error: function (error) {
            displayAlert('error');
            $("#return-message").html(error.responseText);
        },
        beforeSend: function () {
            $("#signup-submit").prop({ "disabled": true, "value": "Loading" });
        },
        complete: function () {
            $("#signup-submit").prop({ "disabled": false, "value": "Signup" });
        }
    });
}



/**
 * 
 * @param {*} state 
 * Alert display
 */
function displayAlert(state, timeout = 3000) {
    $("#return-message").css({ "opacity": 1, "width": "93%", "visibility": "visible", "display": "block" })
        .delay(timeout).fadeOut('slow');
    if (state == "error") {
        $("#return-message").css("border-left", "6px solid red");
    }
    if (state == "success") {
        $("#return-message").css("border-left", "6px solid green");
    }
    if (state == "info") {
        $("#return-message").css("border-left", "6px solid #039BE5");
    }
}


/**
 * 
 * @param {*} username 
 * @param {*} email 
 * @param {*} password 
 * @param {*} repassword 
 * Frontend validations to increase speed for the UI
 * 
 */
function isValidDetails(username, email, password, repassword) {
    if (!username) {
        displayAlert('error');
        $("#return-message").html("Enter a username");
        return true;
    }
    if (!email) {
        displayAlert('error');
        $("#return-message").html("Enter an email");
        return true;
    }
    if (!password) {
        displayAlert('error');
        $("#return-message").html("Enter a password");
        return true;
    }
    if (!repassword) {
        displayAlert('error');
        $("#return-message").html("Confirm your password");
        return true;
    }
    if (password != repassword) {
        displayAlert('error');
        $("#return-message").html("Passwords do not match");
        return true;
    }
}



/**
 * Login form submit functionality
 */
$("#login-form").submit(function (e) {
    e.preventDefault();
    login();
})
function login() {
    var email = $("#email").val();
    var password = $("#password").val();
    if (!email) {
        displayAlert('error');
        $("#return-message").html("Enter your email");
        return;
    }
    if (!password) {
        displayAlert('error');
        $("#return-message").html("Enter your password");
        return;
    }
    $.ajax({
        url: "/login",
        type: "POST",
        contentType: "application/json",
        crossDomain: true,
        global: true,
        data: JSON.stringify({ email: email, password: password }),
        success: function (data) {
            displayAlert('success');
            $("#return-message").html(data);
            setTimeout(function () {
                window.location.replace("/home");
            }, 500);
        },
        error: function (error) {
            displayAlert('error');
            $("#return-message").html(error.responseText);
        },
        beforeSend: function () {
            $("#login-submit").prop({ "disabled": true, "value": "Loading" });
        },
        complete: function () {
            $("#login-submit").prop({ "disabled": false, "value": "Login" });
        }
    });
}



/**
 * Logout functionality
 */
$("#logout").click(function (e) {
    e.preventDefault();
    logout();
})
$("#logout-mobile").click(function (e) {
    e.preventDefault();
    logout();
})

function logout() {
    $.ajax({
        url: "/logout",
        type: "POST",
        crossDomain: true,
        global: true
        ,success: function (data) {
            displayAlert('success');
            $("#return-message").html(data);
        },
        error: function (error) {
            displayAlert('error');
            $("#return-message").html(error.responseText);
        }

    });
    window.location.replace("/")
}




/**
 * Save message functionality
 */
$("#add-form").submit(function (e) {
    e.preventDefault();
    saveMessage();
})
function saveMessage() {
    var message = $("#message").val();
    var duration = $("#duration").val();
    var name = $("#group-name").val();
    $.ajax({
        url: "/save_message",
        type: "POST",
        contentType: "application/json",
        crossDomain: true,
        global: true,
        data: JSON.stringify({ message: message, duration: duration, name: name }),
        success: function (data) {
            displayAlert('success');
            $("#return-message").html(data);
            setTimeout(function () {
                window.location.replace("/home");
            }, 500);
        },
        error: function (error) {
            displayAlert('error');
            $("#return-message").html(error.responseText);
        },
        beforeSend: function () {
            $("#add-submit").prop({ "disabled": true, "value": "Loading" });
        },
        complete: function () {
            $("#add-submit").prop({ "disabled": false, "value": "Add Message" });
        }
    });
}



/**
 * Edit message form
 */
$(".editselect").click(function (e) {
    e.preventDefault();
    var messageId = e.target.id;
    window.location.replace(`/edit/${messageId}`);
});

/**
 * Edit form submission
 */
$("#edit-form").submit(function (e) {
    e.preventDefault();
    editMessage(e);
})

function editMessage(e) {
    var id = $("#idStore").attr("value");
    var message = $("#message-edit").val();
    var duration = $("#duration-edit").val();
    var name = $("#group-name-edit").val();
    $.ajax({
        url: "/edit_message",
        type: "POST",
        contentType: "application/json",
        crossDomain: true,
        global: true,
        data: JSON.stringify({ message: message, duration: duration, name: name, id: id }),
        success: function (data) {
            displayAlert('success');
            $("#return-message").html(data);
            setTimeout(function () {
                window.location.replace("/home");
            }, 500);
        },
        error: function (error) {
            displayAlert('error');
            $("#return-message").html(error.responseText);
        },
        beforeSend: function () {
            $("#edit-submit").prop({ "disabled": true, "value": "Loading" });
        },
        complete: function () {
            $("#edit-submit").prop({ "disabled": false, "value": "Update Message" });
        }
    });
}

/**
 * Send code to Mobile
 */
// Start and stop message
$(".start-message").click(function (e) {
    e.preventDefault();
    openMobileForm(e);
});

$(".stop-message").click(function (e) {
    e.preventDefault();
    stopMessaging(e);
});

$("#mobile-form").submit(function (e) {
    e.preventDefault();
    sendVerificationCode();
})

function stopMessaging(e) {
    var pid = e.target.id;
    $.ajax({
        url: "/stop_process",
        type: "POST",
        contentType: "application/json",
        crossDomain: true,
        global: true,
        data: JSON.stringify({ pid: pid }),
        success: function (data) {
            displayAlert('success');
            $("#return-message").html(data);
            setTimeout(function () {
                window.location.replace("/home");
            }, 5000);
        },
        error: function (error) {
            displayAlert('error');
            $("#return-message").html(error.responseText);
            setTimeout(function () {
                window.location.replace("/home");
            }, 5000);
        },
        beforeSend: function () {
            $(".stop-message").prop({ "disabled": true, "value": "Loading" });
        },
        complete: function () {
            $(".stop-message").prop({ "disabled": false, "value": "Stop Messaging" });
        }
    });
}


function sendVerificationCode() {
    var pid = $(".pid").text();
    var mobileNo = $("#mobile").val();
    var code = $("#code").val();
    if (!code) {
        displayAlert('error');
        $("#return-message").html("Enter a valid country number");
        return;
    }
    if (!mobileNo) {
        displayAlert('error');
        $("#return-message").html("Enter a mobile number");
        return;
    }

    $.ajax({
        url: "/send_code",
        type: "POST",
        contentType: "application/json",
        crossDomain: true,
        global: true,
        data: JSON.stringify({ pid: pid, code: code, mobile: mobileNo }),
        success: function (data) {
            displayAlert('success');
            $("#return-message").html(data);
            setTimeout(function () {
                openVerifyPage();
            }, 500);
        },
        error: function (error) {
            displayAlert('error');
            $("#return-message").html(error.responseText);
        },
        beforeSend: function () {
            displayAlert('info', 1000000);
            $("#return-message").html("We are sending a code to your phone (In the telegram app/messages). This may take a few minutes");
            $("#mobile-submit").prop({ "disabled": true, "value": "Loading" });
        },
        complete: function () {
            $("#mobile-submit").prop({ "disabled": false, "value": "Send Code" });
        }
    });
}


/**
 * Verify form submit
 */
$("#verify-form").submit(function (e) {
    e.preventDefault();
    verifyCode();
});

function verifyCode() {
    var my_code = $("#verification").val();
    var pid = $(".pid").text();
    if (!my_code) {
        displayAlert('error');
        $("#return-message").html("Enter the code received on your mobile phone");
        return;
    }

    $.ajax({
        url: "/verify_code",
        type: "POST",
        contentType: "application/json",
        crossDomain: true,
        global: true,
        data: JSON.stringify({ my_code: my_code, pid: pid }),
        success: function (data) {
            const { channel_name, channel_members, can_send, message } = data;
            displayAlert('success');
            $("#return-message").html(message);
            setTimeout(function () {
                $("#channel_name").html(channel_name);
                $("#channel_members").html(channel_members);
                if(can_send){
                    $("#confirm-start").css("display", "block")
                }else{
                    $("#cant_text").css("display", "block")
                    $("#cant_text").html("*You cant send messages <br> to this channel*");
                    $(".view-all-messages").css("display", "block");
                }
                openConfirmPage();
            }, 500);
        },
        error: function (error) {
            if (error.status == 404) {
                $("#confirm-title").html("Channel or group name not found");
                $("#confirm-desc").html("Ensure that you give a channel or group <br> that you are a member of.");
                $(".view-all-messages").css("display", "block");
                openConfirmPage();
                return;
            }
            if (error.status == 401) {
                $("#confirm-title").html("Code was not verified");
                $("#confirm-desc").html("We experienced an error while verifying your code.");
                $(".view-all-messages").css("display", "block");
                openConfirmPage();
                return;
            }
            displayAlert('error');
            $("#return-message").html(error.responseText);
        },
        beforeSend: function () {
            $("#verify-submit").prop({ "disabled": true, "value": "Loading" });
        },
        complete: function () {
            $("#verify-submit").prop({ "disabled": false, "value": "Verify" });
        }
    });
}



/**
 * Confirm the start of the process
 */
$("#confirm-start").click(function (e) {
    e.preventDefault();
    confirmStart();
})
function confirmStart() {
    pid = $(".pid").text();
    $.ajax({
        url: "/start_process",
        type: "POST",
        contentType: "application/json",
        crossDomain: true,
        global: true,
        data: JSON.stringify({ pid: pid }),
        success: function (data) {
            displayAlert('success', 10000);
            $("#return-message").html("We will start the process in a short while");
            // setTimeout(function () {
            //     window.location.replace("/home");
            // }, 10000);
        },
        error: function (error) {
            displayAlert('error');
            $("#return-message").html(error.responseText);
            // setTimeout(function () {
            //     window.location.replace("/home");
            // }, 10000);
        },
        beforeSend: function () {
            displayAlert('success', 10000);
            $("#return-message").html("We will start the process in a short while");
            $("#confirm-start").prop({ "disabled": true, "value": "Loading" });
        },
        complete: function () {
            $("#confirm-start").prop({ "disabled": true, "value": "Confirm" });
        }
    });
}