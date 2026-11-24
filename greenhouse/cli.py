"""Console demo: python -m greenhouse.cli [alert|no_alert] [--tricky] [--restarts]

Prints input -> steps -> output for all three algorithms. Works offline.
"""

import sys

from greenhouse.pipeline import run_pipeline


def print_steps(title: str, steps: list) -> None:
    print(f"\n{title}")
    for s in steps:
        print(f"  {s['status']:<2}  {s['source']:<7} {s['text']}")


def main(argv: list[str]) -> None:
    observation = "no_alert" if "no_alert" in argv else "alert"
    result = run_pipeline(observation=observation, tricky="--tricky" in argv,
                          restarts="--restarts" in argv)

    print("Mini Greenhouse Assistant  (all numbers are hypothetical assumptions)")
    print_steps("① Bayes: is the soil really dry?", result["bayes"]["steps"])
    print_steps("② MDP: water now or wait?", result["mdp"]["steps"] + result["decision"]["steps"])
    print_steps("③ Hill climbing: how much water?", result["hill_climbing"]["steps"])
    if result["random_restart"]:
        print_steps("③b Random restart", result["random_restart"]["steps"])

    rec = result["recommendation"]
    print(f"\n=> {rec['headline']}  {rec['detail']}")


if __name__ == "__main__":
    main(sys.argv[1:])
