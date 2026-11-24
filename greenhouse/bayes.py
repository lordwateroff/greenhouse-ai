"""1. Bayesian inference: is the soil really dry?

In plain words: the sensor says "dry", but it sometimes lies.
Bayes tells us how much to trust it.
"""

from greenhouse import step


def check_probability(name: str, value: float) -> None:
    """Stop early with a clear message if a probability is outside [0, 1]."""
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1, got {value}")


def posterior(prior_dry: float, p_alert_given_dry: float, p_alert_given_normal: float,
              observation: str) -> dict:
    """Return P(Dry | observation) plus the steps used to get there.

    observation is "alert" (sensor says dry) or "no_alert".
    """
    check_probability("prior_dry", prior_dry)
    check_probability("p_alert_given_dry", p_alert_given_dry)
    check_probability("p_alert_given_normal", p_alert_given_normal)
    if observation not in ("alert", "no_alert"):
        raise ValueError("observation must be 'alert' or 'no_alert'")

    prior_normal = 1.0 - prior_dry

    # Likelihood: how likely is what we saw, in each world?
    if observation == "alert":
        like_dry, like_normal = p_alert_given_dry, p_alert_given_normal
    else:
        like_dry, like_normal = 1.0 - p_alert_given_dry, 1.0 - p_alert_given_normal

    joint_dry = like_dry * prior_dry  # "dry AND we saw this"
    joint_normal = like_normal * prior_normal  # "normal AND we saw this"
    evidence = joint_dry + joint_normal  # P(observation), all the ways to see it
    if evidence == 0:
        raise ValueError("this observation is impossible with these numbers")

    p_dry = joint_dry / evidence  # Bayes rule

    o = observation
    steps = [
        step("bayes", f"prior P(Dry) = {prior_dry:.2f}, P(Normal) = {prior_normal:.2f}"),
        step("bayes", f"sensor reading = {o}"),
        step("bayes", f"P({o}|Dry)·P(Dry) = {like_dry:.2f}·{prior_dry:.2f} = {joint_dry:.4f}"),
        step("bayes", f"P({o}|Normal)·P(Normal) = {like_normal:.2f}·{prior_normal:.2f} = {joint_normal:.4f}"),
        step("bayes", f"P({o}) = {joint_dry:.4f} + {joint_normal:.4f} = {evidence:.4f}"),
        step("bayes", f"P(Dry|{o}) = {joint_dry:.4f} / {evidence:.4f} = {p_dry:.4f}  ({p_dry:.1%})", "OK"),
    ]
    return {
        "prior_dry": prior_dry,
        "observation": observation,
        "likelihood_dry": like_dry,
        "likelihood_normal": like_normal,
        "evidence": evidence,
        "p_dry": p_dry,
        "steps": steps,
    }
