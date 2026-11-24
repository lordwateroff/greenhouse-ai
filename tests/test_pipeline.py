from greenhouse.experiments import run_all
from greenhouse.pipeline import run_pipeline


def test_alert_means_water_30_ml():
    rec = run_pipeline(observation="alert")["recommendation"]
    assert rec["action"] == "Water"
    assert rec["headline"] == "Water 30 ml now."


def test_no_alert_means_wait():
    rec = run_pipeline(observation="no_alert")["recommendation"]
    assert rec["action"] == "Wait"
    assert rec["headline"].startswith("Wait")
    assert "30 ml" in rec["detail"]


def test_bayes_output_feeds_the_mdp():
    r = run_pipeline(observation="alert")
    assert r["decision"]["belief"] == r["bayes"]["p_dry"]


def test_tricky_mode_with_and_without_restarts():
    assert run_pipeline(tricky=True)["recommendation"]["dose"] == 20
    assert run_pipeline(tricky=True, restarts=True)["recommendation"]["dose"] == 40


def test_experiments_run():
    data = run_all()
    assert len(data["decision_grid"]) == 9
    # noisy sensor + rare drought can mean "Wait" even on an alert
    assert any(row["action"] == "Wait" for row in data["decision_grid"])
    assert data["score_curve"]["threshold"] == 0.376
