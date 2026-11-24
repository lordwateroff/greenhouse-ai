"""The whole chain: Bayes -> MDP -> hill climbing -> one recommendation.

Bayes turns a noisy reading into a belief P(Dry).
The MDP turns that belief into an action (Water or Wait).
Hill climbing picks the dose, used only if the action is Water.
"""

from greenhouse import config
from greenhouse.bayes import posterior
from greenhouse.hill_climbing import hill_climb, random_restart
from greenhouse.mdp import decide_under_belief, value_iteration


def run_pipeline(observation: str = "alert",
                 prior_dry: float = config.PRIOR_DRY,
                 p_alert_given_dry: float = config.P_ALERT_GIVEN_DRY,
                 p_alert_given_normal: float = config.P_ALERT_GIVEN_NORMAL,
                 gamma: float = config.GAMMA,
                 rewards: dict = config.REWARDS,
                 transitions: dict = config.TRANSITIONS,
                 doses: list = config.DOSES,
                 scores: list | None = None,
                 start_dose: int = config.START_DOSE,
                 tricky: bool = False,
                 restarts: bool = False) -> dict:
    """Run all three algorithms in order and return every result plus the final advice."""
    if scores is None:
        scores = config.TRICKY_SCORES if tricky else config.SCORES

    # 1. Bayes: how sure are we that the soil is dry?
    bayes = posterior(prior_dry, p_alert_given_dry, p_alert_given_normal, observation)

    # 2. MDP: learn the value of each action, then decide using our belief.
    mdp = value_iteration(config.STATES, config.ACTIONS, rewards, transitions, gamma,
                          config.TOLERANCE, config.MAX_ITERATIONS)
    decision = decide_under_belief(bayes["p_dry"], mdp["Q"])

    # 3. Hill climbing: how much water? (with optional restarts to escape a local maximum)
    climb = hill_climb(doses, scores, start_dose)
    restart = random_restart(doses, scores) if restarts else None
    dose = restart["best_dose"] if restart else climb["best_dose"]

    if decision["action"] == "Water":
        headline = f"Water {dose} ml now."
        detail = f"We are {bayes['p_dry']:.0%} sure the soil is dry, so watering pays off."
    else:
        headline = "Wait. Check again later."
        detail = f"No watering now. When it's needed, the best dose is {dose} ml."

    return {
        "inputs": {"observation": observation, "prior_dry": prior_dry,
                   "p_alert_given_dry": p_alert_given_dry, "p_alert_given_normal": p_alert_given_normal,
                   "gamma": gamma, "rewards": rewards, "transitions": transitions,
                   "doses": doses, "scores": scores, "start_dose": start_dose,
                   "tricky": tricky, "restarts": restarts},
        "bayes": bayes,
        "mdp": mdp,
        "decision": decision,
        "hill_climbing": climb,
        "random_restart": restart,
        "recommendation": {"action": decision["action"], "dose": dose,
                           "headline": headline, "detail": detail},
    }
