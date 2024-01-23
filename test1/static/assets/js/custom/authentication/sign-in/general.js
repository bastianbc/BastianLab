"use strict";

function wait(ms){
   var start = new Date().getTime();
   var end = start;
   while(end < start + ms) {
     end = new Date().getTime();
  }
}

var KTSigninGeneral = (function () {
    var e, t, i;

    return {
        init: function () {
            e = document.querySelector("#kt_sign_in_form");
            t = document.querySelector("#kt_sign_in_submit");
            i = FormValidation.formValidation(e, {
                fields: {
                    email: {
                        validators: {
                            regexp: {
                                regexp: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                                message: "The value is not a valid email address"
                            },
                            notEmpty: {
                                message: "Email address is required"
                            }
                        }
                    },
                    password: {
                        validators: {
                            notEmpty: {
                                message: "The password is required"
                            }
                        }
                    }
                },
                plugins: {
                    trigger: new FormValidation.plugins.Trigger,
                    bootstrap: new FormValidation.plugins.Bootstrap5({
                        rowSelector: ".fv-row",
                        eleInvalidClass: "",
                        eleValidClass: ""
                    })
                }
            });

            t.addEventListener("click", function (n) {
                n.preventDefault();
                i.validate().then(function (i) {
                    if ("Valid" == i) {
                        t.setAttribute("data-kt-indicator", "on");
                        t.disabled = !0;
                        setTimeout(function () {
                            t.removeAttribute("data-kt-indicator");
                            t.disabled = !1;
                            Swal.fire({
                                text: "You have successfully logged in!",
                                icon: "success",
                                buttonsStyling: !1,
                                confirmButtonText: "Ok, got it!",
                                customClass: {
                                    confirmButton: "btn btn-primary"
                                }
                            }).then(function (t) {
                                wait(3000);
                                if (t.isConfirmed) {
                                    e.querySelector('[name="username"]').value = "";
                                    e.querySelector('[name="password"]').value = "";
                                    wait(3000);
                                    var i = e.getAttribute("data-kt-redirect-url");

                                    wait(3000);
                                    if (i) {
                                        wait(3000);
                                        location.href = i;
                                        wait(3000);
                                    }
                                }
                            })
                        }, 2e3);
                    } else {
                        Swal.fire({
                            text: "Sorry, looks like there are some errors detected, please try again.",
                            icon: "error",
                            buttonsStyling: !1,
                            confirmButtonText: "Ok, got it!",
                            customClass: {
                                confirmButton: "btn btn-primary"
                            }
                        });
                    }
                });
            });
        }
    };
})();

KTUtil.onDOMContentLoaded(function () {
    KTSigninGeneral.init();
});
