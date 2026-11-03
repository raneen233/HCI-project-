// Drawing page: canvas, tools, undo/clear, countdown timer, submit.
// Mouse/touch work now. Hand tracking plugs in through window.drawing (bottom of file).
(function () {
  const cfg = JSON.parse(document.getElementById("draw-config").textContent);
  const wrap = document.getElementById("canvas-wrap");
  const canvas = document.getElementById("canvas");
  const ctx = canvas.getContext("2d");
  const undoBtn = document.getElementById("undo-btn");
  const clearBtn = document.getElementById("clear-btn");

  // ---------------- drawing state ----------------
  const pick = (sel, attr) => document.querySelector(`${sel}[aria-pressed="true"]`)?.dataset[attr];
  let color = pick(".swatch", "color");
  let size = Number(pick(".size-btn", "size"));
  let tool = pick(".tool-chip", "tool") || "pencil";
  let strokes = [];        // every finished line, so Undo can redraw without the last one
  let current = null;      // the line being drawn right now
  let locked = false;      // true after submitting / time's up

  // Points are stored as 0-1 fractions of the canvas, so resizing the window keeps the drawing.
  function toPoint(clientX, clientY) {
    const r = canvas.getBoundingClientRect();
    return [(clientX - r.left) / r.width, (clientY - r.top) / r.height];
  }

  function strokeStyle(s) {
    const base = { color: s.color, width: s.size, alpha: 1 };
    if (s.tool === "brush") return { ...base, width: s.size * 1.9, alpha: 0.85 };
    if (s.tool === "fineliner") return { ...base, width: Math.max(1.5, s.size * 0.5) };
    if (s.tool === "eraser") return { ...base, color: "#ffffff", width: s.size * 2.6 };
    return base;
  }

  function drawStroke(s) {
    const st = strokeStyle(s);
    const w = canvas.clientWidth, h = canvas.clientHeight;
    const pts = s.points.map(([x, y]) => [x * w, y * h]);
    ctx.save();
    ctx.globalAlpha = st.alpha;
    ctx.strokeStyle = st.color;
    ctx.fillStyle = st.color;
    ctx.lineWidth = st.width;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    if (pts.length === 1) {                       // a single tap = a dot
      ctx.beginPath();
      ctx.arc(pts[0][0], pts[0][1], st.width / 2, 0, Math.PI * 2);
      ctx.fill();
    } else {                                      // smooth curve through the points
      ctx.beginPath();
      ctx.moveTo(pts[0][0], pts[0][1]);
      for (let i = 1; i < pts.length - 1; i++) {
        const mx = (pts[i][0] + pts[i + 1][0]) / 2, my = (pts[i][1] + pts[i + 1][1]) / 2;
        ctx.quadraticCurveTo(pts[i][0], pts[i][1], mx, my);
      }
      const last = pts[pts.length - 1];
      ctx.lineTo(last[0], last[1]);
      ctx.stroke();
    }
    ctx.restore();
  }

  function redraw() {
    ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);
    strokes.forEach(drawStroke);
    if (current) drawStroke(current);
  }

  function refreshButtons() {
    const hasInk = strokes.length > 0;
    undoBtn.disabled = !hasInk || locked;
    clearBtn.disabled = !hasInk || locked;
    wrap.classList.toggle("has-ink", hasInk || Boolean(current));
  }

  // Keep the canvas sharp at any size / screen density.
  function resize() {
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(canvas.clientWidth * dpr);
    canvas.height = Math.round(canvas.clientHeight * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    redraw();
  }
  new ResizeObserver(resize).observe(canvas);

  // ---------------- stroke lifecycle (shared by mouse and hand) ----------------
  function canDraw() { return !locked && !timer.isPaused(); }
  function startStroke(pt) {
    if (!canDraw()) return;
    current = { color, size, tool, points: [pt] };
    wrap.classList.add("is-drawing");
    redraw(); refreshButtons();
  }
  function extendStroke(pt) {
    if (!current) return;
    const prev = current.points[current.points.length - 1];
    if (Math.hypot(pt[0] - prev[0], pt[1] - prev[1]) < 0.002) return;   // skip tiny jitters
    current.points.push(pt);
    redraw();
  }
  function endStroke() {
    wrap.classList.remove("is-drawing");
    if (!current) return;
    strokes.push(current);
    current = null;
    refreshButtons();
  }

  // Mouse / touch / pen
  canvas.addEventListener("pointerdown", (e) => {
    canvas.setPointerCapture(e.pointerId);
    startStroke(toPoint(e.clientX, e.clientY));
  });
  canvas.addEventListener("pointermove", (e) => { if (current) extendStroke(toPoint(e.clientX, e.clientY)); });
  ["pointerup", "pointercancel"].forEach((t) => canvas.addEventListener(t, endStroke));

  // ---------------- toolbar ----------------
  function choose(group, btn) {
    document.querySelectorAll(group).forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
  }
  document.querySelectorAll(".swatch").forEach((b) => {
    if (["#e8dcc4", "#cfcfd4", "#ffffff"].includes(b.dataset.color)) b.classList.add("is-light");
    b.addEventListener("click", () => {
      choose(".swatch", b); color = b.dataset.color;
      if (tool === "eraser") {                    // picking a colour means "draw again"
        const pencil = document.querySelector('.tool-chip[data-tool="pencil"]');
        if (pencil) { choose(".tool-chip", pencil); tool = "pencil"; }
      }
    });
  });
  document.querySelectorAll(".size-btn").forEach((b) =>
    b.addEventListener("click", () => { choose(".size-btn", b); size = Number(b.dataset.size); }));
  document.querySelectorAll(".tool-chip").forEach((b) =>
    b.addEventListener("click", () => { choose(".tool-chip", b); tool = b.dataset.tool; }));

  function undo() {
    if (locked || !strokes.length) return;
    strokes.pop(); redraw(); refreshButtons();
  }
  undoBtn.addEventListener("click", undo);
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z") { e.preventDefault(); undo(); }
  });

  // ---------------- popups (timer pauses while they're open) ----------------
  function ask(dialog) {
    return new Promise((resolve) => {
      timer.hold("dialog");
      dialog.showModal();
      dialog.querySelector('[data-answer="no"]').focus();
      const done = (answer) => {
        dialog.close(); timer.release("dialog"); resolve(answer);
        dialog.removeEventListener("cancel", onCancel);
      };
      const onCancel = (e) => { e.preventDefault(); done(false); };
      dialog.addEventListener("cancel", onCancel);
      dialog.querySelectorAll("[data-answer]").forEach((b) => {
        b.onclick = () => done(b.dataset.answer === "yes");
      });
    });
  }

  const clearDialog = document.getElementById("clear-dialog");
  const finishDialog = document.getElementById("finish-dialog");
  const finishText = document.getElementById("finish-text");
  const normalFinishText = finishText.textContent;

  clearBtn.addEventListener("click", async () => {
    if (await ask(clearDialog)) { strokes = []; redraw(); refreshButtons(); }
  });

  document.getElementById("finish-btn").addEventListener("click", async () => {
    if (locked) return;
    endStroke();
    finishText.textContent = strokes.length
      ? normalFinishText
      : `Your canvas is still empty! ${cfg.guesser} won't have anything to guess from.`;
    if (await ask(finishDialog)) submit("finished");
  });

  // ---------------- submit ----------------
  function submit(reason) {
    if (locked && reason !== "timeout") return;
    locked = true;
    endStroke();
    wrap.classList.add("is-locked");
    refreshButtons();
    // Export on a white background (the canvas itself is transparent).
    const out = document.createElement("canvas");
    out.width = canvas.width; out.height = canvas.height;
    const o = out.getContext("2d");
    o.fillStyle = "#ffffff"; o.fillRect(0, 0, out.width, out.height);
    o.drawImage(canvas, 0, 0);
    document.getElementById("drawing-data").value = out.toDataURL("image/png");
    document.getElementById("submit-reason").value = reason;
    document.getElementById("submit-form").submit();
  }

  // ---------------- countdown timer ----------------
  const timer = (function () {
    const box = document.getElementById("timer");
    const text = document.getElementById("timer-text");
    const holds = new Set();          // reasons the clock is paused ("dialog", "menu")
    let msLeft = cfg.remaining * 1000;
    let last = performance.now();
    let finished = false;

    function render() {
      const s = Math.max(0, Math.ceil(msLeft / 1000));
      text.textContent = `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
      box.classList.toggle("is-low", s <= 10 && s > 0);
      box.classList.toggle("is-paused", holds.size > 0);
    }
    function tick() {
      const now = performance.now();
      if (!holds.size && !finished) msLeft -= now - last;
      last = now;
      render();
      if (msLeft <= 0 && !finished) { finished = true; timeUp(); }
    }
    setInterval(tick, 200);
    render();
    return {
      hold(reason) { holds.add(reason); render(); },
      release(reason) { holds.delete(reason); last = performance.now(); render(); },
      isPaused() { return holds.size > 0; },
    };
  })();

  function timeUp() {
    endStroke();
    [clearDialog, finishDialog].forEach((d) => d.open && d.close());
    if (window.game) game.resume();
    locked = true;
    refreshButtons();
    document.getElementById("times-up").hidden = false;
    setTimeout(() => submit("timeout"), 1500);
  }

  // The shared pause menu (pause button / fist gesture) also stops the clock.
  if (window.game) {
    game.on("pause", () => { endStroke(); timer.hold("menu"); });
    game.on("resume", () => timer.release("menu"));
  }

  // ---------------- hand-tracking hooks for the socket code ----------------
  const cursor = document.getElementById("hand-cursor");
  const camStatus = document.querySelectorAll("#cam-status");
  function setCamStatus(state, label) {
    camStatus.forEach((el) => {
      el.hidden = false;
      el.classList.toggle("is-hand", state === "hand");
      el.classList.toggle("is-lost", state === "lost");
      el.querySelector("span").textContent = label;
    });
  }

  window.drawing = {
    // x, y: 0-1 position over the canvas. pinching: true while thumb + index touch.
    handMove(x, y, pinching) {
      cursor.hidden = false;
      cursor.style.left = `${x * 100}%`;
      cursor.style.top = `${y * 100}%`;
      cursor.classList.toggle("is-pinching", pinching);
      setCamStatus("hand", pinching ? "Hand detected · Pinching" : "Hand detected · Open palm");
      if (window.handStatus) handStatus.set("hand");
      if (pinching && !current) startStroke([x, y]);
      else if (pinching) extendStroke([x, y]);
      else endStroke();
    },
    handLost() {
      endStroke();
      cursor.hidden = true;
      setCamStatus("lost", "No hand detected · Raise your hand");
      if (window.handStatus) handStatus.set("lost");
    },
    // Show the webcam stream from the Python side, e.g. setCamFeed("/video_feed")
    setCamFeed(url) {
      document.querySelectorAll("#cam-feed").forEach((img) => { img.src = url; img.hidden = false; });
    },
    undo,
    clear: () => clearBtn.click(),
    finish: () => document.getElementById("finish-btn").click(),
  };

  refreshButtons();
})();
