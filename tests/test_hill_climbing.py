import pytest

from greenhouse.config import DOSES, SCORES, TRICKY_SCORES
from greenhouse.hill_climbing import hill_climb, random_restart


def test_climbs_from_10_to_30():
    r = hill_climb(DOSES, SCORES, 10)
    assert r["path"] == [10, 20, 30]
    assert r["best_dose"] == 30
    assert r["best_score"] == 88
    assert r["num_steps"] == 2


@pytest.mark.parametrize("start", DOSES)
def test_any_start_reaches_30(start):
    assert hill_climb(DOSES, SCORES, start)["best_dose"] == 30


def test_tricky_gets_stuck_at_local_maximum():
    r = hill_climb(DOSES, TRICKY_SCORES, 10)
    assert r["path"] == [10, 20]
    assert r["best_dose"] == 20


def test_random_restart_escapes_local_maximum():
    r = random_restart(DOSES, TRICKY_SCORES)
    assert r["best_dose"] == 40
    assert r["best_score"] == 85


def test_plateau_stops():
    r = hill_climb([10, 20, 30], [50, 50, 50], 20)
    assert r["path"] == [20]
    assert r["num_steps"] == 0


def test_length_mismatch_raises():
    with pytest.raises(ValueError):
        hill_climb([10, 20], [1, 2, 3], 10)


def test_unknown_start_raises():
    with pytest.raises(ValueError):
        hill_climb(DOSES, SCORES, 35)
