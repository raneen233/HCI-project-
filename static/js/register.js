// Create Account page: checks every field, then shows "Creating account..." while the form is sent.
(function () {
  const form = document.getElementById("register-form");
  const card = document.getElementById("register-card");
  const label = form.querySelector(".submit-label");
  const f = form.elements;   // f.username, f.email, f.password, f.confirm, f.terms

  Validate.initPasswordToggles(form);

  const checks = {
    username() {
      const v = f.username.value.trim();
      if (!v) return "Please choose a username.";
      if (v.length < 3) return "Usernames need at least 3 characters.";
      if (!/^[A-Za-z0-9_]+$/.test(v)) return "Use only letters, numbers and _.";
      return "";
    },
    email() {
      const v = f.email.value.trim();
      if (!v) return "Please enter your email address.";
      if (!Validate.isEmail(v)) return "Enter a valid email, like doodle@example.com.";
      return "";
    },
    password() {
      const v = f.password.value;
      if (!v) return "Please create a password.";
      if (v.length < 6) return "Use at least 6 characters.";
      return "";
    },
    confirm() {
      if (!f.confirm.value) return "Please re-enter your password.";
      if (f.confirm.value !== f.password.value) return "Passwords don't match.";
      return "";
    },
    terms() {
      return f.terms.checked ? "" : "Please agree to the terms to join the fun.";
    },
  };
  const order = ["username", "email", "password", "confirm", "terms"];

  // Check a text field when the user leaves it; clear its error while they fix it.
  ["username", "email", "password", "confirm"].forEach((name) => {
    f[name].addEventListener("blur", () => { if (f[name].value) Validate.setError(f[name], checks[name]()); });
    f[name].addEventListener("input", () => Validate.setError(f[name], ""));
  });
  // If they change the password after confirming it, re-check the match.
  f.password.addEventListener("input", () => {
    if (f.confirm.value) Validate.setError(f.confirm, checks.confirm());
  });
  f.terms.addEventListener("change", () => Validate.setError(f.terms, checks.terms()));

  form.addEventListener("submit", (e) => {
    let firstBad = null;
    order.forEach((name) => {
      const msg = checks[name]();
      Validate.setError(f[name], msg);
      if (msg && !firstBad) firstBad = f[name];
    });

    if (firstBad) {
      e.preventDefault();
      firstBad.focus();
      return;
    }
    card.classList.add("is-loading");
    label.textContent = "Creating account...";
  });

  window.addEventListener("pageshow", () => {
    card.classList.remove("is-loading");
    label.textContent = "Create Account";
  });
})();
