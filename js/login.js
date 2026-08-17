document.addEventListener("DOMContentLoaded", () => {

    const loginForm = document.getElementById("loginForm");

    if (!loginForm) {
        console.error("[LOGIN] loginForm not found.");
        return;
    }

    console.log("[LOGIN] JavaScript loaded.");

    const rolePatientBtn = document.getElementById("rolePatientBtn");
    const roleAdminBtn = document.getElementById("roleAdminBtn");
    const selectedRoleInput = document.getElementById("selectedRole");

    if (rolePatientBtn && roleAdminBtn && selectedRoleInput) {
        rolePatientBtn.addEventListener("click", () => {
            selectedRoleInput.value = "user";
            rolePatientBtn.style.background = "rgba(59, 130, 246, 0.3)";
            rolePatientBtn.style.color = "#fff";
            roleAdminBtn.style.background = "rgba(255, 255, 255, 0.05)";
            roleAdminBtn.style.color = "#94a3b8";
        });
        roleAdminBtn.addEventListener("click", () => {
            selectedRoleInput.value = "admin";
            roleAdminBtn.style.background = "rgba(59, 130, 246, 0.3)";
            roleAdminBtn.style.color = "#fff";
            rolePatientBtn.style.background = "rgba(255, 255, 255, 0.05)";
            rolePatientBtn.style.color = "#94a3b8";
        });
    }

    loginForm.addEventListener("submit", async (event) => {

        event.preventDefault();
        event.stopPropagation();

        const emailInput = document.getElementById("email");
        const passwordInput = document.getElementById("password");
        const role = selectedRoleInput ? selectedRoleInput.value : "user";

        const rememberInput = loginForm.querySelector(
            'input[type="checkbox"]'
        );

        if (!emailInput || !passwordInput) {
            console.error("[LOGIN] Required input missing.");
            alert("Login form is incomplete.");
            return;
        }

        const email = emailInput.value.trim().toLowerCase();
        const password = passwordInput.value;

        const remember = rememberInput
            ? rememberInput.checked
            : false;

        if (!email || !password) {
            alert(
                "Please enter your email and password."
            );
            return;
        }

        const submitButton = loginForm.querySelector(
            'button[type="submit"]'
        );

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = "Logging in...";
        }

        try {

            console.log(
                "[LOGIN] Sending POST /api/login"
            );

            const response = await fetch(
                "http://127.0.0.1:5000/api/auth/login",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },

                    credentials: "include",

                    body: JSON.stringify({
                        email: email,
                        password: password,
                        remember: remember
                    })
                }
            );

            const result = await response.json();

            if (response.ok && result.success) {

                if (result.user) {
                    localStorage.setItem(
                        "currentUser",
                        JSON.stringify(result.user)
                    );
                    const accounts = JSON.parse(localStorage.getItem("logged_in_accounts") || "[]");
                    if (!accounts.some(a => a.email.toLowerCase() === result.user.email.toLowerCase())) {
                        accounts.push(result.user);
                        localStorage.setItem("logged_in_accounts", JSON.stringify(accounts));
                    }
                }

                if (role === "admin" && result.user?.role !== "admin") {
                    alert("This account is not authorized to access the Administrator Portal.");
                    return;
                }

                alert("Login successful.");

                window.location.replace(
                    result.user?.role === "admin" ? "dashboard.html" : "index.html"
                );

                return;
            }

            alert(
                result.error ||
                "Invalid email or password."
            );

        } catch (error) {

            console.error(
                "[LOGIN] Connection error:",
                error
            );

            alert("Unable to contact the server. Please make sure the backend is running and try again.");

        } finally {

            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = "Login";
            }
        }
    });


    // ------------------------------------------------------------------------
    // PASSWORD VISIBILITY
    // ------------------------------------------------------------------------

    const togglePassword = document.getElementById(
        "togglePassword"
    );

    const passwordInput = document.getElementById(
        "password"
    );

    if (togglePassword && passwordInput) {

        togglePassword.addEventListener(
            "click",
            () => {

                if (passwordInput.type === "password") {

                    passwordInput.type = "text";

                    togglePassword.classList.remove(
                        "fa-eye"
                    );

                    togglePassword.classList.add(
                        "fa-eye-slash"
                    );

                } else {

                    passwordInput.type = "password";

                    togglePassword.classList.remove(
                        "fa-eye-slash"
                    );

                    togglePassword.classList.add(
                        "fa-eye"
                    );
                }
            }
        );
    }
});
