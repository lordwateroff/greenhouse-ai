// Greenhouse helper: ask the Python API, then paint the answer.
const $ = (id) => document.getElementById(id);
const state = { observation: "alert", tricky: false, restarts: false };
let busy = false;

const pct = (x) => `${Math.round(x * 100)}%`;

async function run() {
  if (busy) return;
  busy = true;
  document.querySelectorAll(".choice").forEach((b) => (b.disabled = true));
  try {
    const res = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    paint(await res.json());
    $("notice").hidden = true;
  } catch {
    $("notice").hidden = false;
  } finally {
    busy = false;
    document.querySelectorAll(".choice").forEach((b) => (b.disabled = false));
  }
}

function paint(r) {
  const rec = r.recommendation;
  const pDry = r.bayes.p_dry;
  const water = rec.action === "Water";
  const hc = state.restarts ? r.random_restart : r.hill_climbing;

  // the answer card
  $("answer").dataset.action = rec.action;
  $("a-head").textContent = rec.headline;
  $("a-why").textContent = water
    ? `I am ${pct(pDry)} sure the soil is dry, so watering helps.`
    : `I am only ${pct(pDry)} sure the soil is dry. When it is time, use ${hc.best_dose} ml.`;
  $("cup-water").style.transform = `translateY(${144 - 2.1 * rec.dose}px)`;

  // step 1: how dry
  setBar("b-dry", pDry, pct(pDry));
  setBar("b-ok", 1 - pDry, pct(1 - pDry));

  // step 2: water or wait
  const s = r.decision.scores;
  const top = Math.max(s.Water, s.Wait);
  setBar("d-water", s.Water / top, s.Water.toFixed(1));
  setBar("d-wait", s.Wait / top, s.Wait.toFixed(1));
  $("d-water").parentElement.classList.toggle("soft", s.Water < s.Wait);
  $("d-wait").parentElement.classList.toggle("soft", s.Wait <= s.Water);

  // step 3: how much
  const doses = r.inputs.doses;
  const scores = r.inputs.scores;
  const best = Math.max(...scores);
  $("doses").replaceChildren(...doses.map((d, i) => {
    const col = document.createElement("div");
    col.className = "dose" + (d === hc.best_dose ? " best" : hc.path.includes(d) ? " seen" : "");
    const bar = document.createElement("i");
    bar.style.setProperty("--h", (scores[i] / (best * 1.12)).toFixed(3));
    const label = document.createElement("span");
    label.textContent = d;
    col.append(bar, label);
    return col;
  }));
  $("doses").setAttribute("aria-label", `Plant happiness for each dose. Best is ${hc.best_dose} ml.`);
  const [first, ...rest] = hc.path;
  const walk = rest.length ? `Start at ${first} ml, then ${rest.join(", then ")}.` : `Start at ${first} ml.`;
  const topDose = doses[scores.indexOf(best)];
  $("dose-path").textContent = state.restarts
    ? `I tried every start. Best: ${hc.best_dose} ml.`
    : hc.best_score < best
      ? `${walk} Stuck at ${hc.best_dose} ml, but ${topDose} ml is better. A small hill fooled it.`
      : `${walk} Best: ${hc.best_dose} ml.`;

  // details
  const t = r.decision.threshold;
  $("k-thresh").textContent = t === null ? "never" : `${(t * 100).toFixed(1)}%`;
  const lines = [...r.bayes.steps, ...r.mdp.steps, ...r.decision.steps, ...(state.restarts ? r.random_restart.steps : r.hill_climbing.steps)];
  $("log").replaceChildren(...lines.map((l) => {
    const li = document.createElement("li");
    li.textContent = `${l.source}: ${l.text}`;
    if (l.status === "OK") li.className = "ok";
    return li;
  }));
}

function setBar(id, value, label) {
  $(id).style.setProperty("--w", Math.max(0, Math.min(1, value)).toFixed(3));
  $(`${id}-n`).textContent = label;
}

document.querySelectorAll(".choice").forEach((btn) => {
  btn.addEventListener("click", () => {
    state.observation = btn.dataset.obs;
    document.querySelectorAll(".choice").forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
    run();
  });
});
$("t-tricky").addEventListener("change", (e) => { state.tricky = e.target.checked; run(); });
$("t-restarts").addEventListener("change", (e) => { state.restarts = e.target.checked; run(); });
$("retry").addEventListener("click", run);

run();
