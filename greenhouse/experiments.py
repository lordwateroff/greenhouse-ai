"""Experiments for the Results section: python -m greenhouse.experiments [--json]

Same code as the app, just run over a grid of inputs.
"""

import json
import sys

from greenhouse import config
from greenhouse.hill_climbing import hill_climb, random_restart
from greenhouse.pipeline import run_pipeline


def decision_grid() -> list:
    """Experiment 1: decision on 'alert' for different priors and false-alarm rates."""
    rows = []
    for prior in (0.1, 0.3, 0.5):
        for false_alarm in (0.05, 0.2, 0.4):
            r = run_pipeline(observation="alert", prior_dry=prior, p_alert_given_normal=false_alarm)
            rows.append({"prior_dry": prior, "p_alert_given_normal": false_alarm,
                         "p_dry": round(r["bayes"]["p_dry"], 4), "action": r["decision"]["action"]})
    return rows


def hill_starts() -> list:
    """Experiment 2: hill climbing from every start, normal vs tricky, with and without restarts."""
    rows = []
    for mode, scores in (("normal", config.SCORES), ("tricky", config.TRICKY_SCORES)):
        restart_best = random_restart(config.DOSES, scores)["best_dose"]
        for d in config.DOSES:
            r = hill_climb(config.DOSES, scores, d)
            rows.append({"mode": mode, "start_dose": d, "path": r["path"], "stops_at": r["best_dose"],
                         "score": r["best_score"], "with_restarts": restart_best})
    return rows


def score_curve(points: int = 11) -> dict:
    """Experiment 3: Score(Water) and Score(Wait) as P(Dry) goes from 0 to 1."""
    r = run_pipeline()
    Q = r["mdp"]["Q"]
    curve = []
    for i in range(points):
        b = i / (points - 1)
        curve.append({"p_dry": b,
                      "water": round(b * Q["Dry"]["Water"] + (1 - b) * Q["Normal"]["Water"], 2),
                      "wait": round(b * Q["Dry"]["Wait"] + (1 - b) * Q["Normal"]["Wait"], 2)})
    return {"threshold": round(r["decision"]["threshold"], 4), "curve": curve}


def run_all() -> dict:
    return {"decision_grid": decision_grid(), "hill_starts": hill_starts(), "score_curve": score_curve()}


def main(argv: list[str]) -> None:
    data = run_all()
    if "--json" in argv:
        print(json.dumps(data, indent=2))
        return
    print("Experiment 1: decision on 'alert'")
    print("  prior  false-alarm  P(Dry|alert)  action")
    for row in data["decision_grid"]:
        print(f"  {row['prior_dry']:<5}  {row['p_alert_given_normal']:<11}  {row['p_dry']:<12.4f}  {row['action']}")
    print("\nExperiment 2: hill climbing from every start")
    print("  mode    start  path                  stops at  with restarts")
    for row in data["hill_starts"]:
        path = " → ".join(map(str, row["path"]))
        print(f"  {row['mode']:<6}  {row['start_dose']:<5}  {path:<20}  {row['stops_at']:<8}  {row['with_restarts']}")
    sc = data["score_curve"]
    print(f"\nExperiment 3: water when P(Dry) > {sc['threshold']}")
    for p in sc["curve"]:
        print(f"  P(Dry)={p['p_dry']:.1f}  Water={p['water']:7.2f}  Wait={p['wait']:7.2f}")


if __name__ == "__main__":
    main(sys.argv[1:])
