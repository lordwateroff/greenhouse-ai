"""3. Hill climbing: how much water is best?

In plain words: try a bit more or a bit less water. If the plant gets
better, keep going that way. If it gets worse, stop.
Like finding the right music volume.
"""

from greenhouse import step


def check_doses(doses: list, scores: list) -> None:
    """Stop early with a clear message if the dose table is broken."""
    if len(doses) != len(scores):
        raise ValueError(f"doses ({len(doses)}) and scores ({len(scores)}) must have the same length")
    if not doses:
        raise ValueError("need at least one dose")


def hill_climb(doses: list, scores: list, start_dose: int) -> dict:
    """Steepest-ascent hill climbing over neighbouring doses (index ± 1).

    Look at both neighbours, move to the better one only if it is strictly
    better than where we stand. Otherwise stop: we are on a hill top.
    """
    check_doses(doses, scores)
    if start_dose not in doses:
        raise ValueError(f"start_dose {start_dose} is not one of the doses {doses}")

    i = doses.index(start_dose)
    path = [doses[i]]
    steps = [step("hill", f"start at {doses[i]} ml, score {scores[i]}")]

    while True:
        neighbours = [j for j in (i - 1, i + 1) if 0 <= j < len(doses)]
        best = max(neighbours, key=lambda j: scores[j])
        seen = ", ".join(f"{doses[j]} ml → {scores[j]}" for j in neighbours)
        if scores[best] > scores[i]:
            steps.append(step("hill", f"neighbours: {seen}. move to {doses[best]} ml", ".."))
            i = best
            path.append(doses[i])
        else:
            steps.append(step("hill", f"neighbours: {seen}. none is better, stop"))
            break

    n = len(path) - 1
    steps.append(step("hill", f"best dose = {doses[i]} ml, score {scores[i]}, {n} step{'' if n == 1 else 's'}", "OK"))
    return {
        "start_dose": start_dose,
        "path": path,
        "best_dose": doses[i],
        "best_score": scores[i],
        "num_steps": len(path) - 1,
        "steps": steps,
    }


def random_restart(doses: list, scores: list) -> dict:
    """Fix for getting stuck: climb from every starting dose and keep the best top.

    With only 5 doses we can afford to try every start, so no randomness is needed.
    """
    check_doses(doses, scores)
    runs = [hill_climb(doses, scores, d) for d in doses]
    best = max(runs, key=lambda r: r["best_score"])
    steps = [step("restart", f"from {r['start_dose']} ml → stops at {r['best_dose']} ml (score {r['best_score']})", "..")
             for r in runs]
    steps.append(step("restart", f"best of all runs: {best['best_dose']} ml, score {best['best_score']}", "OK"))
    return {
        "runs": [{"start_dose": r["start_dose"], "path": r["path"], "best_dose": r["best_dose"],
                  "best_score": r["best_score"]} for r in runs],
        "best_dose": best["best_dose"],
        "best_score": best["best_score"],
        "path": best["path"],
        "steps": steps,
    }
