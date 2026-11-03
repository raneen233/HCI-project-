// Bluetooth sign-in: ask the server who's nearby every 2 seconds.
// One known phone nearby -> short countdown, then sign in (can be cancelled).
// Several nearby -> the player taps their name.
(function () {
  const POLL_MS = 2000;
  const COUNTDOWN_MS = 2500;

  const radar = document.getElementById("bt-radar");
  const status = document.getElementById("bt-status");
  const statusText = document.getElementById("bt-status-text");
  const found = document.getElementById("bt-found");
  const progress = document.getElementById("bt-progress");
  const form = document.getElementById("bt-form");
  const chips = [...document.querySelectorAll(".bt-player")];

  const dismissed = new Set();   // phones the user cancelled; we won't auto sign them in again
  let pending = null;            // id of the player we're counting down for
  let countdown = null;
  let signingIn = false;

  function setStatus(text, kind) {
    statusText.textContent = text;
    status.classList.toggle("is-ok", kind === "ok");
    status.classList.toggle("is-warn", kind === "warn");
  }

  function signIn(id) {
    if (signingIn) return;
    signingIn = true;
    clearTimeout(countdown);
    document.getElementById("bt-player-id").value = id;
    setStatus("Signing in...", "ok");
    form.submit();
  }

  function stopCountdown() {
    clearTimeout(countdown);
    pending = null;
    found.hidden = true;
    progress.style.transition = "none";
    progress.style.width = "0";
  }

  function startCountdown(player) {
    if (pending === player.id) return;
    stopCountdown();
    pending = player.id;
    document.getElementById("bt-found-name").textContent = `Found ${player.name}'s phone!`;
    const avatar = document.getElementById("bt-found-avatar");
    avatar.textContent = player.name[0];
    avatar.className = `bt-avatar tone-${player.tone}`;
    found.hidden = false;
    requestAnimationFrame(() => requestAnimationFrame(() => {   // animate the bar from 0 to 100%
      progress.style.transition = `width ${COUNTDOWN_MS}ms linear`;
      progress.style.width = "100%";
    }));
    countdown = setTimeout(() => signIn(player.id), COUNTDOWN_MS);
  }

  document.getElementById("bt-cancel").addEventListener("click", () => {
    if (pending) dismissed.add(pending);
    stopCountdown();
    setStatus("Sign-in cancelled. Tap your name if you change your mind.");
  });

  chips.forEach((chip) => chip.addEventListener("click", () => {
    if (chip.classList.contains("is-nearby")) signIn(chip.dataset.id);
  }));

  function render(data) {
    if (signingIn) return;
    document.querySelectorAll("[data-sim]").forEach((b) =>
      b.setAttribute("aria-pressed", String((data.simulated || []).includes(b.dataset.sim))));
    const nearby = data.players.filter((p) => p.nearby);

    chips.forEach((chip) => {
      const p = data.players.find((x) => x.id === chip.dataset.id);
      const near = Boolean(p && p.nearby);
      chip.classList.toggle("is-nearby", near);
      chip.disabled = !near;
      chip.setAttribute("aria-label", `Sign in as ${chip.textContent.trim()}${near ? "" : " (phone not nearby)"}`);
    });

    radar.classList.toggle("is-found", nearby.length > 0);
    radar.classList.toggle("is-off", nearby.length === 0 && data.status !== "scanning" && data.status !== "starting");

    // Phone we were counting down for walked away
    if (pending && !nearby.some((p) => p.id === pending)) {
      stopCountdown();
      setStatus("Lost the signal. Bring your phone a little closer.", "warn");
      return;
    }

    const candidates = nearby.filter((p) => !dismissed.has(p.id));
    if (candidates.length === 1 && nearby.length === 1) {
      startCountdown(candidates[0]);
      setStatus("Phone found!", "ok");
    } else if (nearby.length > 1) {
      stopCountdown();
      setStatus(`${nearby.length} phones nearby · Tap your name to sign in`, "ok");
    } else if (nearby.length === 1) {
      // only phone nearby was cancelled
      setStatus("Tap your name to sign in.", "ok");
    } else if (data.status === "unavailable" || data.status === "error") {
      stopCountdown();
      setStatus("Bluetooth scanning isn't working on this laptop yet.", "warn");
      document.getElementById("bt-hint").textContent = data.error || "";
    } else {
      stopCountdown();
      setStatus("Looking for nearby phones...");
    }
  }

  async function poll() {
    try {
      const res = await fetch("/api/bluetooth/nearby", { cache: "no-store" });
      render(await res.json());
    } catch {
      setStatus("Can't reach the game server. Is app.py running?", "warn");
    }
  }

  // Developer testing panel (only rendered in debug mode)
  document.querySelectorAll("[data-sim]").forEach((btn) => btn.addEventListener("click", async () => {
    await fetch("/dev/bluetooth/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player_id: btn.dataset.sim }),
    });
    dismissed.delete(btn.dataset.sim);
    poll();
  }));

  window.addEventListener("pageshow", () => { signingIn = false; });
  poll();
  setInterval(poll, POLL_MS);
})();
