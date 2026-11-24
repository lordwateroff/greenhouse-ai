import pytest

from greenhouse.bayes import posterior


def run(obs, prior=0.30):
    return posterior(prior, 0.90, 0.20, obs)


def test_alert_gives_66_percent():
    r = run("alert")
    assert r["evidence"] == pytest.approx(0.41)
    assert r["p_dry"] == pytest.approx(0.658537, abs=1e-6)


def test_no_alert_gives_5_percent():
    r = run("no_alert")
    assert r["evidence"] == pytest.approx(0.59)
    assert r["p_dry"] == pytest.approx(0.050847, abs=1e-6)


def test_certain_prior_stays_certain():
    assert run("alert", prior=0.0)["p_dry"] == 0.0
    assert run("alert", prior=1.0)["p_dry"] == 1.0


@pytest.mark.parametrize("bad", [-0.1, 1.5])
def test_invalid_probability_raises(bad):
    with pytest.raises(ValueError):
        posterior(bad, 0.9, 0.2, "alert")
    with pytest.raises(ValueError):
        posterior(0.3, bad, 0.2, "alert")


def test_unknown_observation_raises():
    with pytest.raises(ValueError):
        posterior(0.3, 0.9, 0.2, "maybe")


def test_steps_end_with_the_answer():
    assert "0.6585" in run("alert")["steps"][-1]["text"]
