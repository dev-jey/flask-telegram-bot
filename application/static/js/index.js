

//Login Button Click
$("#login").click(function (e) {
    closeMenu(e);
    openLogin(e);
});

// Start message
$("#start-message").click(function (e) {
    openMobileForm(e);
})

$("#mobile-submit").click(function (e) {
    closeMobile(e);
    openVerifyPage(e);
})

//$("#verify-submit").click(function(e){
//     closeVerifyPage(e);
// })



$("#login-desktop").click(function (e) {
    openLogin(e);
});

// Mobile close
$("#x-mobile").click(function (e) {
    closeMobile(e);
});

// Verify Close
$("#x-verify").click(function (e) {
    closeVerifyPage(e);
});

//Login close
$("#x").click(function (e) {
    closeLogin(e);
});

//signup close
$("#x-signup").click(function (e) {
    closeSignup(e);
});

//Signup Button Click
$("#signup").click(function (e) {
    closeMenu(e);
    openSignup(e);
});

$("#signup-desktop").click(function (e) {
    openSignup(e);
});

$("#signup-main").click(function (e) {
    openSignup(e);
});


// Toggle Menu
$("#ham").click(function (e) {
    openMenu(e);
});

$("#x-menu").click(function (e) {
    closeMenu(e);
});


$("#mobile-cover").click(function (e) {
    closeMenu(e);
});

//Open signup
$("#signup-link").click(function (e) {
    closeLogin(e);
    openSignup(e);
})

$("#login-link").click(function (e) {
    closeSignup(e);
    openLogin(e);
})

$("#go-to-login").click(function (e) {
    openLogin(e)
})

// Functions
function openMobileForm(e) {
    e.preventDefault();
    $("#mobile-page").addClass("show");
    $("#x-mobile").css("display", "block");
}

function openVerifyPage(e) {
    e.preventDefault();
    $("#verify-page").addClass("show");
    $("#x-verify").css("display", "block");
}

function openSignup(e) {
    e.preventDefault();
    $("#signup-page").addClass("show");
    $("#x-signup").css("display", "block");
}

function openLogin(e) {
    e.preventDefault();
    $("#login-page").addClass("show");
    $("#x").css("display", "block");
}

function openMenu(e) {
    e.preventDefault();
    $("#mobile-cover").addClass("show");
    $("#mobile-menu").addClass("show");
    $("#x-menu").css("display", "block");
}

function closeSignup(e) {
    e.preventDefault();
    $("#signup-page").removeClass("show");
    $("#x-signup").css("display", "none");
}

function closeLogin(e) {
    e.preventDefault();
    $("#login-page").removeClass("show");
    $("#x").css("display", "none");
}
function closeMenu(e) {
    e.preventDefault();
    $("#mobile-cover").removeClass("show");
    $("#mobile-menu").removeClass("show");
    $("#x-menu").css("display", "none");
}

function closeMobile(e) {
    e.preventDefault();
    $("#mobile-page").removeClass("show");
    $("#x-mobile").css("display", "none");
}

function closeVerifyPage(e) {
    e.preventDefault();
    $("#verify-page").removeClass("show");
    $("#x-verify").css("display", "none");
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
            displayAlert('success');
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
function displayAlert(state) {
    $("#return-message").css({ "opacity": 1, "width": "400px", "visibility": "visible", "display": "block" })
        .delay(3000).fadeOut('slow');
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
        return True;
    }
    if (!email) {
        displayAlert('error');
        $("#return-message").html("Enter an email");
        return True;
    }
    if (!password) {
        displayAlert('error');
        $("#return-message").html("Enter a password");
        return True;
    }
    if (!repassword) {
        displayAlert('error');
        $("#return-message").html("Confirm your password");
        return True;
    }
    if (password != repassword) {
        displayAlert('error');
        $("#return-message").html("Passwords do not match");
        return True;
    }
}




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
            window.location.replace("/home");
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

$("#login-form").submit(function (e) {
    e.preventDefault();
    login();
})



$("#logout").click(function (e) {
    logout(e);
})
$("#logout-mobile").click(function (e) {
    logout(e);
})

function logout(e){
    e.preventDefault();
    $.ajax({
        url: "/logout",
        type: "GET",
        crossDomain: true,
        global: true
    });
    window.location.replace("/")
}
















function getBotResponse() {
    $("#respo").html(`<b></b>`);
    var msg = $("#msg").val();
    var duration = $("#duration").val();
    var link = $("#link").val();
    $.get("/save_process", { msg: msg, duration: duration, link: link })
        .then((res) => {
            $("#respo").html(`<b>${res}</b>`);
            if (res == "Process has been added successfully") {
                window.location.replace("/processes");
            }
        })
}

$("#buttonInput").click(function (e) {
    e.preventDefault();
    getBotResponse();
})