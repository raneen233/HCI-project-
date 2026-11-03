// Word Choosing: hand-off screen -> pick a word -> lock it and open the canvas.
(function () {
  const handoff = document.getElementById("handoff");
  const step = document.getElementById("word-step");
  const form = document.getElementById("word-form");
  const status = document.getElementById("word-status");
  const statusText = document.getElementById("word-status-text");
  const drawBtn = document.getElementById("draw-btn");
  const foot = document.getElementById("word-foot");

  const picked = () => form.querySelector('input[name="word"]:checked');

  // Step 1 -> 2: the drawer reveals the words
  document.getElementById("reveal-btn").addEventListener("click", () => {
    handoff.hidden = true;
    step.hidden = false;
    form.querySelector('input[name="word"]').focus({ preventScroll: true });
  });

  // Back hides the words again (useful if the guesser walks in)
  document.getElementById("word-back").addEventListener("click", () => {
    step.hidden = true;
    handoff.hidden = false;
  });

  function update() {
    const p = picked();
    status.classList.remove("shake");
    status.classList.toggle("is-picked", Boolean(p));
    drawBtn.setAttribute("aria-disabled", p ? "false" : "true");
    statusText.textContent = p
      ? `Your secret word: ${p.value} · You can still change your choice`
      : "No word selected yet · Move to a card and pinch to choose";
  }
  form.addEventListener("change", update);

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const p = picked();
    if (!p) {                                   // nothing picked: nudge the hint
      status.classList.remove("shake");
      void status.offsetWidth;
      status.classList.add("shake");
      statusText.textContent = "Pick a word first · Move to a card and pinch to choose";
      return;
    }
    form.classList.add("is-locked");
    statusText.textContent = `${p.value} selected · Choice locked while your canvas opens`;
    drawBtn.querySelector(".draw-label").textContent = "Opening your canvas...";
    foot.textContent = "Getting ready · Your drawing time hasn't started yet";
    setTimeout(() => form.submit(), 1000);
  });

  window.addEventListener("pageshow", () => {
    form.classList.remove("is-locked");
    drawBtn.querySelector(".draw-label").textContent = "Let's Draw!";
    foot.textContent = "Your drawing time begins only after you confirm with Let's Draw!";
    update();
  });
})();
