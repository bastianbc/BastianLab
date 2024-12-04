document.addEventListener("DOMContentLoaded", function () {

    // init event to start typing to password inputs
    document.querySelectorAll('input[type="password"]').forEach((item, i) => {
        item.addEventListener("keydown", function () {
            toggleEyeIconVisibility(this);
        });
    });

    document.querySelectorAll('.password-input-container .toggle-password i').forEach((item, i) => {
        item.addEventListener("click", function () {
            togglepasswordVisibility(this);
        });
    });

});


function toggleEyeIconVisibility( item ) {
    var eyeIcon = item.nextElementSibling.firstElementChild;

    if ( item.value ) {
        if (eyeIcon) {
            eyeIcon.classList.remove("d-none");
        }
    }
    else {
        eyeIcon.classList.add("d-none")
    }
}

function togglepasswordVisibility( item ) {
    const passwordInput = item.parentElement.previousElementSibling;
    const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
    passwordInput.setAttribute("type", type);
    item.classList.toggle("bi-eye");
    item.classList.toggle("bi-eye-slash");
}
