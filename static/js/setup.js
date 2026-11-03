// Game Setup: keeps the summary card in sync with the choices, handles the
// Player 2 picker, and shows "Starting..." before going to the first round.
(function () {
  const form = document.getElementById("setup-form");
  const summary = document.getElementById("summary");
  const picker = document.getElementById("p2-picker");
  const p2Card = document.getElementById("p2-card");
  const p2Input = document.getElementById("player2");
  const player1 = picker.dataset.player1;
  const $ = (id) => document.getElementById(id);

  function current() {
    const diff = form.querySelector('input[name="difficulty"]:checked');
    const rounds = form.querySelector('input[name="rounds"]:checked');
    return {
      difficulty: diff.dataset.name,
      seconds: Number(diff.dataset.seconds),
      rounds: Number(rounds.value),
      player2: p2Input.value,
    };
  }

  // Redraw everything that depends on the choices.
  function update() {
    const s = current();
    const ready = Boolean(s.player2);

    $("sum-players").textContent = `Player 1 = ${player1}\nPlayer 2 = ${s.player2 || "?"}`;
    $("sum-difficulty").textContent = s.difficulty;
    $("sum-time").textContent = `${s.seconds} seconds`;
    $("sum-rounds").textContent = `${s.rounds} rounds`;

    p2Card.classList.toggle("is-empty", !ready);
    $("p2-name").textContent = s.player2 || "Add Player 2";
    $("players-meta").textContent = ready ? "2 players signed in" : "1 of 2 players signed in";

    summary.classList.toggle("is-waiting", !ready);
    $("sum-status").textContent = ready ? "Ready when you are" : "Waiting for Player 2";
    $("sum-first-title").textContent = ready ? "First up: Round 1" : "Add Player 2 to start";
    $("sum-first-roles").textContent = ready ? `${player1} draws · ${s.player2} guesses` : "Two players take turns drawing and guessing.";
    $("sum-first-time").textContent = `${s.seconds} seconds to draw!`;
    $("sum-foot").textContent = ready ? "All set. Let the happy little guesses begin!" : "Tap the Player 2 card to add your friend.";
  }

  // ---- Player 2 ----
  function setPlayer2(name) {
    if (!name || name === player1) return;
    p2Input.value = name;
    p2Card.classList.remove("attention");
    update();
  }

  function openPicker() {
    picker.querySelectorAll(".picker-item").forEach((b) =>
      b.classList.toggle("is-current", b.dataset.name === p2Input.value));
    picker.showModal();
  }

  p2Card.addEventListener("click", openPicker);
  picker.querySelectorAll(".picker-item").forEach((btn) =>
    btn.addEventListener("click", () => { setPlayer2(btn.dataset.name); picker.close(); }));
  picker.querySelector(".picker-cancel").addEventListener("click", () => picker.close());
  picker.addEventListener("click", (e) => { if (e.target === picker) picker.close(); });

  form.addEventListener("change", update);

  // ---- Start ----
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const s = current();
    if (!s.player2) {               // can't start alone: point at the Player 2 card
      p2Card.classList.remove("attention");
      void p2Card.offsetWidth;      // restart the shake animation
      p2Card.classList.add("attention");
      openPicker();
      return;
    }
    summary.classList.add("is-starting");
    form.classList.add("is-starting");
    $("start-btn").disabled = true;
    $("sum-status").textContent = "Here we go";
    $("sum-first-title").textContent = "Starting your game...";
    $("sum-first-time").textContent = `${s.seconds} seconds to bring the word to life!`;
    $("start-btn").querySelector(".start-label").textContent = "Starting...";
    $("sum-foot").textContent = "Preparing Round 1. Please wait.";
    setTimeout(() => form.submit(), 1200);   // short pause so players see what's coming
  });

  window.addEventListener("pageshow", () => {
    summary.classList.remove("is-starting");
    form.classList.remove("is-starting");
    $("start-btn").disabled = false;
    $("start-btn").querySelector(".start-label").textContent = "Start Game";
    update();
  });

  // Hook for later: the Bluetooth code can call setup.setPlayer2("Jamie")
  // when it recognises Player 2's phone.
  window.setup = { setPlayer2 };
  update();
})();
