from fastapi.testclient import TestClient

from app import app
from greenhouse.pipeline import run_pipeline

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_defaults():
    d = client.get("/api/defaults").json()
    assert d["prior_dry"] == 0.30
    assert d["scores"] == [55, 72, 88, 80, 60]


def test_run_with_defaults_matches_pipeline():
    r = client.post("/api/run", json={})
    assert r.status_code == 200
    expected = run_pipeline()
    assert r.json()["recommendation"] == expected["recommendation"]
    assert r.json()["bayes"]["p_dry"] == expected["bayes"]["p_dry"]


def test_run_without_body():
    assert client.post("/api/run").status_code == 200


def test_no_alert_flips_to_wait():
    r = client.post("/api/run", json={"observation": "no_alert"})
    assert r.json()["recommendation"]["action"] == "Wait"


def test_bad_probability_is_422():
    r = client.post("/api/run", json={"prior_dry": 1.4})
    assert r.status_code == 422
    assert "prior_dry" in r.text


def test_transitions_not_summing_to_one_is_422():
    t = run_pipeline()["inputs"]["transitions"]
    t = {s: {a: dict(row) for a, row in acts.items()} for s, acts in t.items()}
    t["Dry"]["Water"] = {"Dry": 0.5, "Normal": 0.6}
    r = client.post("/api/run", json={"transitions": t})
    assert r.status_code == 422
    assert "add up to 1" in r.text


def test_length_mismatch_is_422():
    r = client.post("/api/run", json={"scores": [1, 2]})
    assert r.status_code == 422
    assert "same length" in r.text


def test_impossible_observation_is_422():
    r = client.post("/api/run", json={"p_alert_given_dry": 0, "p_alert_given_normal": 0})
    assert r.status_code == 422
    assert "impossible" in r.text
