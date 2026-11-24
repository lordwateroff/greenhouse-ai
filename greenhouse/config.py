"""All default numbers in one place.

Every value here is an assumption (hypothetical) chosen for the demo.
In a real greenhouse we would learn them from sensor logs.
"""

# --- 1. Bayes: how much do we trust the sensor? ---
PRIOR_DRY = 0.30  # assumption (hypothetical): soil is dry 30% of the time
P_ALERT_GIVEN_DRY = 0.90  # assumption (hypothetical): sensor catches dry soil 90% of the time
P_ALERT_GIVEN_NORMAL = 0.20  # assumption (hypothetical): false alarm 20% of the time

# --- 2. MDP: water now or wait? ---
STATES = ["Dry", "Normal"]
ACTIONS = ["Water", "Wait"]
GAMMA = 0.9  # assumption (hypothetical): future matters, but a bit less than now

# R(s, a): what we get right now for doing action a in state s
REWARDS = {  # assumption (hypothetical)
    "Dry": {"Water": 6.0, "Wait": -10.0},  # plant saved minus water cost / plant suffers
    "Normal": {"Water": -4.0, "Wait": 5.0},  # overwatering / all good, water saved
}

# P(s' | s, a): where we end up tomorrow
TRANSITIONS = {  # assumption (hypothetical)
    "Dry": {
        "Water": {"Dry": 0.1, "Normal": 0.9},
        "Wait": {"Dry": 1.0, "Normal": 0.0},
    },
    "Normal": {
        "Water": {"Dry": 0.0, "Normal": 1.0},
        "Wait": {"Dry": 0.3, "Normal": 0.7},
    },
}

TOLERANCE = 1e-6
MAX_ITERATIONS = 1000

# --- 3. Hill climbing: how much water is best? ---
DOSES = [10, 20, 30, 40, 50]  # ml
SCORES = [55, 72, 88, 80, 60]  # assumption (hypothetical): plant health score per dose
TRICKY_SCORES = [60, 70, 65, 85, 75]  # assumption (hypothetical): has a local maximum at 20 ml
START_DOSE = 10


def defaults() -> dict:
    """Return every default input as one plain dict (used by the API and the UI reset)."""
    return {
        "observation": "alert",
        "prior_dry": PRIOR_DRY,
        "p_alert_given_dry": P_ALERT_GIVEN_DRY,
        "p_alert_given_normal": P_ALERT_GIVEN_NORMAL,
        "gamma": GAMMA,
        "rewards": REWARDS,
        "transitions": TRANSITIONS,
        "doses": DOSES,
        "scores": SCORES,
        "tricky_scores": TRICKY_SCORES,
        "start_dose": START_DOSE,
        "tricky": False,
        "restarts": False,
    }
