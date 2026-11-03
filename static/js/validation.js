// Shared form helpers for Log In and Create Account.
window.Validate = {
  isEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value.trim());
  },

  // Show (or clear, if msg is empty) the error under an input.
  setError(input, msg) {
    const field = input.closest(".field");
    field.classList.toggle("has-error", Boolean(msg));
    field.querySelector(".field-error span").textContent = msg || "";
    input.setAttribute("aria-invalid", msg ? "true" : "false");
  },

  // Eye buttons: <button data-toggle-password="inputId">
  initPasswordToggles(root = document) {
    root.querySelectorAll("[data-toggle-password]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const input = document.getElementById(btn.dataset.togglePassword);
        const show = input.type === "password";
        input.type = show ? "text" : "password";
        btn.setAttribute("aria-pressed", String(show));
        btn.setAttribute("aria-label", show ? "Hide password" : "Show password");
      });
    });
  },
};
