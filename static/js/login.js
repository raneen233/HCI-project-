// Log In page: checks the fields, then shows "Logging in..." while the form is sent.
(function () {
  const form = document.getElementById("login-form");
  const card = document.getElementById("login-card");
  const email = form.elements.email;
  const password = form.elements.password;
  const label = form.querySelector(".submit-label");

  Validate.initPasswordToggles(form);

  function checkEmail() {
    const v = email.value.trim();
    if (!v) return "Please enter your email address.";
    if (!Validate.isEmail(v)) return "Enter a valid email, like player@example.com.";
    return "";
  }
  function checkPassword() {
    return password.value ? "" : "Please enter your password.";
  }

  // Check a field when the user leaves it; clear its error as soon as they fix it.
  email.addEventListener("blur", () => { if (email.value) Validate.setError(email, checkEmail()); });
  email.addEventListener("input", () => Validate.setError(email, ""));
  password.addEventListener("input", () => Validate.setError(password, ""));

  form.addEventListener("submit", (e) => {
    const emailMsg = checkEmail();
    const passMsg = checkPassword();
    Validate.setError(email, emailMsg);
    Validate.setError(password, passMsg);

    if (emailMsg || passMsg) {
      e.preventDefault();
      (emailMsg ? email : password).focus();
      return;
    }
    // Valid: show the loading state; the browser sends the form to Flask.
    card.classList.add("is-loading");
    label.textContent = "Logging in...";
    email.readOnly = password.readOnly = true;
  });

  // If the user comes back with the browser's Back button, undo the loading state.
  window.addEventListener("pageshow", () => {
    card.classList.remove("is-loading");
    label.textContent = "Log In";
    email.readOnly = password.readOnly = false;
  });
})();
