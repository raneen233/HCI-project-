// Guessing page: one guess, then lock everything and show the result.
(function () {
  const cfg = JSON.parse(document.getElementById("guess-config").textContent);
  const answers = document.getElementById("answers");
  const buttons = [...answers.querySelectorAll(".answer")];
  const box = document.getElementById("guess-box");
  const nextBtn = document.getElementById("next-btn");

  function showResult(chosen, correct, word, points) {
    answers.classList.add("is-locked");
    document.querySelector(".answers-panel").classList.add("is-locked");
    document.getElementById("answers-meta-text").textContent = "Answers locked · No more guesses this turn";
    document.getElementById("guess-eyebrow").textContent = "Guess complete";

    buttons.forEach((b) => {
      b.disabled = true;
      const isChosen = b.dataset.answer === chosen;
      b.classList.toggle("is-chosen", isChosen);
      b.classList.toggle("is-correct", isChosen && correct);
      b.classList.toggle("is-wrong", isChosen && !correct);
      b.querySelector(".answer-tag").textContent = isChosen ? (correct ? "Correct · Locked" : "Incorrect · Locked") : "";
    });

    box.classList.add(correct ? "is-correct" : "is-wrong");
    document.getElementById("points-won").textContent = points;
    document.getElementById("real-word").textContent = word;
    nextBtn.disabled = false;
  }

  async function guess(answer) {
    if (answers.classList.contains("is-locked") || answers.classList.contains("is-sending")) return;
    answers.classList.add("is-sending");
    try {
      const res = await fetch("/game/guess", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer }),
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      showResult(data.guess, data.correct, data.word, data.points);
      document.getElementById("you-score").textContent = data.score;
    } catch {
      answers.classList.remove("is-sending");
      document.getElementById("answers-meta-text").textContent = "Couldn't send your guess. Try again.";
    }
  }

  buttons.forEach((b) => b.addEventListener("click", () => guess(b.dataset.answer)));

  // Came back to the page after guessing (e.g. refresh): show the locked result again.
  if (cfg.guessed) showResult(cfg.guessed, cfg.correct, cfg.word, cfg.correct ? cfg.points : 0);

  // Hook for hand tracking / DollarPy: guessing.choose("Flower")
  window.guessing = { choose: guess };
})();
