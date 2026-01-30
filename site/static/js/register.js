document.addEventListener("DOMContentLoaded", function() {
    const passwordInput = document.getElementById("register-input-password");
    const confirmInput = document.getElementById("register-input-confirm");
    const passwordStatus = document.getElementById("register-password-status");
    const confirmStatus = document.getElementById("register-confirm-status");

    function checkPasswordPolicy(password) {
        if (password.length > 24) return true;
        if (password.length < 12) return false;

        const hasUpper = /[A-Z]/.test(password);
        const hasLower = /[a-z]/.test(password);
        const hasDigit = /\d/.test(password);
        const hasSymbol = /[!@#$%^&*()\[\]_\-+=,.?<>~|/\\{}]/.test(password);

        return hasUpper && hasLower && hasDigit && hasSymbol;
    }

    function checkPassword() {
        if (checkPasswordPolicy(passwordInput.value)) {
            passwordStatus.textContent = "✓ ok";
        } else {
            passwordStatus.textContent = "";
        }
        checkMatch();
    }

    function checkMatch() {
        if (confirmInput.value.length === 0) {
            confirmStatus.textContent = "";
            return;
        }

        if (confirmInput.value === passwordInput.value) {
            confirmStatus.textContent = "✓ ok";
        } else {
            confirmStatus.textContent = ""
        }
    }

    passwordInput.addEventListener("input", checkPassword);
    confirmInput.addEventListener("input", checkMatch);
});
