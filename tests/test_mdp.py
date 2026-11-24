import copy

import pytest

from greenhouse import config
from greenhouse.mdp import decide_under_belief, value_iteration


def solve(**overrides):
    args = {"states": config.STATES, "actions": config.ACTIONS, "rewards": config.REWARDS,
                "transitions": config.TRANSITIONS, "gamma": config.GAMMA}
    args.update(overrides)
    return value_iteration(**args)


def test_iteration_1_values():
    v1 = solve()["iterations"][1]["V"]
    assert v1 == {"Dry": pytest.approx(6), "Normal": pytest.approx(5)}


def test_iteration_2_q_values():
    q2 = solve()["iterations"][2]["Q"]
    assert q2["Dry"]["Water"] == pytest.approx(10.59)
    assert q2["Dry"]["Wait"] == pytest.approx(-4.6)
    assert q2["Normal"]["Water"] == pytest.approx(0.5)
    assert q2["Normal"]["Wait"] == pytest.approx(9.77)


def test_converges_to_v_star_and_q_star():
    r = solve()
    assert r["V"]["Dry"] == pytest.approx(53.1356, abs=1e-3)
    assert r["V"]["Normal"] == pytest.approx(52.2881, abs=1e-3)
    assert r["Q"]["Dry"]["Water"] == pytest.approx(53.1356, abs=1e-3)
    assert r["Q"]["Dry"]["Wait"] == pytest.approx(37.8220, abs=1e-3)
    assert r["Q"]["Normal"]["Water"] == pytest.approx(43.0593, abs=1e-3)
    assert r["Q"]["Normal"]["Wait"] == pytest.approx(52.2881, abs=1e-3)
    assert r["iterations"][-1]["delta"] < 1e-6


def test_policy():
    assert solve()["policy"] == {"Dry": "Water", "Normal": "Wait"}


def test_decision_under_belief():
    Q = solve()["Q"]
    alert = decide_under_belief(0.658537, Q)
    assert alert["action"] == "Water"
    assert alert["scores"]["Water"] == pytest.approx(49.70, abs=0.01)
    assert alert["scores"]["Wait"] == pytest.approx(42.76, abs=0.01)
    no_alert = decide_under_belief(0.050847, Q)
    assert no_alert["action"] == "Wait"
    assert no_alert["scores"]["Water"] == pytest.approx(43.57, abs=0.01)
    assert no_alert["scores"]["Wait"] == pytest.approx(51.55, abs=0.01)


def test_threshold_is_about_38_percent():
    Q = solve()["Q"]
    assert decide_under_belief(0.5, Q)["threshold"] == pytest.approx(0.376, abs=1e-3)
    assert decide_under_belief(0.38, Q)["action"] == "Water"
    assert decide_under_belief(0.37, Q)["action"] == "Wait"


def test_transitions_must_sum_to_one():
    bad = copy.deepcopy(config.TRANSITIONS)
    bad["Dry"]["Water"] = {"Dry": 0.5, "Normal": 0.6}
    with pytest.raises(ValueError):
        solve(transitions=bad)


def test_gamma_must_be_below_one():
    with pytest.raises(ValueError):
        solve(gamma=1.0)


def test_equal_rewards_have_no_threshold():
    flat = {s: {a: 1.0 for a in config.ACTIONS} for s in config.STATES}
    Q = solve(rewards=flat)["Q"]
    r = decide_under_belief(0.5, Q)
    assert r["threshold"] is None
    assert r["action"] == "Wait"
