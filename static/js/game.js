// Shared by every in-game screen: pause menu + hand-tracking status pill.
(function () {
  const pauseDialog = document.getElementById("pause-dialog");
  const listeners = { pause: [], resume: [] };

  function pause() {
    if (pauseDialog.open) return;
    pauseDialog.showModal();
    listeners.pause.forEach((fn) => fn());
  }
  function resume() {
    if (!pauseDialog.open) return;
    pauseDialog.close();
    listeners.resume.forEach((fn) => fn());
  }

  document.getElementById("pause-btn").addEventListener("click", pause);
  document.getElementById("resume-btn").addEventListener("click", resume);
  pauseDialog.addEventListener("cancel", (e) => { e.preventDefault(); resume(); });   // Esc = resume

  // Pages (e.g. the drawing timer) can react:  game.on("pause", stopTimer)
  window.game = {
    pause,
    resume,
    on(event, fn) { listeners[event].push(fn); },
  };

  // Hand-tracking status in the bottom-left corner.
  // The socket code can call: handStatus.set("hand") / ("lost") / ("mouse")
  const pill = document.getElementById("hand-status");
  const labels = { hand: "Hand detected", lost: "No hand detected", mouse: "Mouse mode" };
  window.handStatus = {
    set(state) {
      pill.classList.toggle("is-hand", state === "hand");
      pill.classList.toggle("is-lost", state === "lost");
      pill.querySelector("span").textContent = labels[state] || labels.mouse;
    },
  };
})();
