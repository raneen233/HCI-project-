// Shared confirmation popup.
//   1) Any <form data-confirm="Title?"> asks before it submits (used by Log out).
//      Optional: data-confirm-text, data-confirm-ok, data-confirm-cancel, data-confirm-eyebrow
//   2) From JS: Modal.confirm({ title, text, ok, cancel }).then(yes => ...)
//      (handy later for "Clear canvas?" and "Finish turn?")
(function () {
  const dlg = document.createElement("dialog");
  dlg.className = "modal";
  dlg.setAttribute("aria-labelledby", "modal-title");
  dlg.innerHTML = `
    <div class="modal-body">
      <p class="modal-eyebrow"></p>
      <h2 class="modal-title" id="modal-title"></h2>
      <p class="modal-text"></p>
      <div class="modal-actions">
        <button class="btn btn-primary gesture-target" type="button" data-answer="yes"></button>
        <button class="btn btn-outline gesture-target" type="button" data-answer="no"></button>
      </div>
    </div>`;
  document.body.appendChild(dlg);

  const eyebrow = dlg.querySelector(".modal-eyebrow");
  const title = dlg.querySelector(".modal-title");
  const text = dlg.querySelector(".modal-text");
  const okBtn = dlg.querySelector('[data-answer="yes"]');
  const cancelBtn = dlg.querySelector('[data-answer="no"]');
  let answer = null;

  function close(result) {
    dlg.close();
    if (answer) { answer(result); answer = null; }
  }
  okBtn.addEventListener("click", () => close(true));
  cancelBtn.addEventListener("click", () => close(false));
  dlg.addEventListener("cancel", (e) => { e.preventDefault(); close(false); });   // Esc key
  dlg.addEventListener("click", (e) => { if (e.target === dlg) close(false); });  // click outside

  function confirm(opts) {
    eyebrow.textContent = opts.eyebrow || "";
    eyebrow.hidden = !opts.eyebrow;
    title.textContent = opts.title || "Are you sure?";
    text.textContent = opts.text || "";
    text.hidden = !opts.text;
    okBtn.textContent = opts.ok || "Yes";
    cancelBtn.textContent = opts.cancel || "Cancel";
    dlg.showModal();
    cancelBtn.focus();   // the safe choice is focused first
    return new Promise((resolve) => { answer = resolve; });
  }

  document.addEventListener("submit", async (e) => {
    const form = e.target;
    if (!form.matches("[data-confirm]")) return;
    e.preventDefault();
    form.closest("details")?.removeAttribute("open");   // close the dropdown behind it

    const d = form.dataset;
    const yes = await confirm({
      eyebrow: d.confirmEyebrow, title: d.confirm, text: d.confirmText,
      ok: d.confirmOk, cancel: d.confirmCancel,
    });
    if (yes) form.submit();   // form.submit() skips this check, so no loop
  });

  window.Modal = { confirm };
})();
