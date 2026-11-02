// How to Play carousel. go(n) is the only thing that changes the step, so a
// mouse click now and a pinch gesture later both just call it.
(function () {
  const slides = [...document.querySelectorAll(".slide")];
  const caps   = [...document.querySelectorAll("[data-cap]")];
  const pips   = [...document.querySelectorAll(".pager i")];
  const first  = document.querySelector('[data-ctrl="first"]');
  const last   = document.querySelector('[data-ctrl="last"]');
  const lastIndex = slides.length - 1;
  let current = 0;

  function go(n) {
    current = Math.max(0, Math.min(lastIndex, n));
    slides.forEach((s, i) => {
      s.classList.toggle("is-active", i === current);
      s.classList.toggle("is-before", i < current);
      s.classList.toggle("is-after", i > current);
      s.inert = i !== current;
    });
    caps.forEach((c, i) => c.classList.toggle("on", i === current));
    pips.forEach((p, i) => p.classList.toggle("on", i === current));

    const atEnd = current === lastIndex;
    first.classList.toggle("is-on", !atEnd); first.inert = atEnd;
    last.classList.toggle("is-on", atEnd);   last.inert = !atEnd;
  }

  document.getElementById("btn-next").addEventListener("click", () => go(current + 1));
  document.getElementById("btn-back").addEventListener("click", () => go(current - 1));
  // handy while testing with a keyboard
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") go(current + 1);
    if (e.key === "ArrowLeft")  go(current - 1);
  });

  window.howTo = { go };   // hook for gestures later
  go(0);
})();
