"""2. MDP with value iteration: water now or wait?

In plain words: for each action we ask "what do I get now, plus what can
I expect later?" and pick the bigger number.
"""

from greenhouse import step


def check_mdp(states: list, actions: list, rewards: dict, transitions: dict, gamma: float) -> None:
    """Stop early with a clear message if the MDP numbers do not make sense."""
    if not 0.0 <= gamma < 1.0:
        raise ValueError(f"gamma must be in [0, 1), got {gamma}")
    for s in states:
        for a in actions:
            row = transitions[s][a]
            if any(p < 0 or p > 1 for p in row.values()):
                raise ValueError(f"transition probabilities for ({s}, {a}) must be in [0, 1]")
            if abs(sum(row.values()) - 1.0) > 1e-9:
                raise ValueError(f"transitions for ({s}, {a}) must sum to 1, got {sum(row.values())}")
            float(rewards[s][a])


def q_value(s: str, a: str, V: dict, rewards: dict, transitions: dict, gamma: float) -> float:
    """Bellman: Q(s,a) = R(s,a) + gamma * sum over s' of P(s'|s,a) * V(s')."""
    later = sum(p * V[s2] for s2, p in transitions[s][a].items())
    return rewards[s][a] + gamma * later


def value_iteration(states: list, actions: list, rewards: dict, transitions: dict, gamma: float,
                    tolerance: float = 1e-6, max_iterations: int = 1000) -> dict:
    """Repeat the Bellman update until values stop changing. Return V*, Q*, policy, history."""
    check_mdp(states, actions, rewards, transitions, gamma)

    V = {s: 0.0 for s in states}  # start knowing nothing: V0 = 0
    history = [{"k": 0, "V": dict(V), "Q": None, "delta": None}]

    for k in range(1, max_iterations + 1):
        Q = {s: {a: q_value(s, a, V, rewards, transitions, gamma) for a in actions} for s in states}
        new_V = {s: max(Q[s].values()) for s in states}  # take the best action in each state
        delta = max(abs(new_V[s] - V[s]) for s in states)
        V = new_V
        history.append({"k": k, "V": dict(V), "Q": Q, "delta": delta})
        if delta < tolerance:
            break

    # Final Q* uses the converged V*.
    Q = {s: {a: q_value(s, a, V, rewards, transitions, gamma) for a in actions} for s in states}
    policy = {s: max(actions, key=lambda a: Q[s][a]) for s in states}

    steps = [step("mdp", f"start: V0 = 0 for every state, gamma = {gamma}")]
    for h in history[1:3]:
        vs = ", ".join(f"V{h['k']}({s}) = {h['V'][s]:.2f}" for s in states)
        steps.append(step("mdp", f"iteration {h['k']}: {vs}", ".."))
    steps.append(step("mdp", f"converged after {len(history) - 1} iterations (change < {tolerance:g})"))
    for s in states:
        qs = ", ".join(f"Q*({s},{a}) = {Q[s][a]:.4f}" for a in actions)
        steps.append(step("mdp", qs))
    pol = ", ".join(f"{s} → {a}" for s, a in policy.items())
    steps.append(step("mdp", f"policy: {pol}", "OK"))

    return {"V": V, "Q": Q, "policy": policy, "iterations": history, "steps": steps}


def decide_under_belief(p_dry: float, Q: dict) -> dict:
    """We only know P(Dry), so weigh each action's value by that belief (QMDP).

    Score(a) = P(Dry) * Q*(Dry, a) + (1 - P(Dry)) * Q*(Normal, a)
    """
    b = p_dry
    scores = {a: b * Q["Dry"][a] + (1 - b) * Q["Normal"][a] for a in ("Water", "Wait")}
    action = "Water" if scores["Water"] > scores["Wait"] else "Wait"

    # Where both lines cross: the P(Dry) above which watering wins.
    gain_if_dry = Q["Dry"]["Water"] - Q["Dry"]["Wait"]
    loss_if_normal = Q["Normal"]["Wait"] - Q["Normal"]["Water"]
    total = gain_if_dry + loss_if_normal
    threshold = loss_if_normal / total if total != 0 else None  # None: the two lines never cross

    steps = [
        step("decide", f"belief P(Dry) = {b:.4f}"),
        step("decide", f"Score(Water) = {b:.4f}·{Q['Dry']['Water']:.2f} + {1 - b:.4f}·{Q['Normal']['Water']:.2f} = {scores['Water']:.2f}"),
        step("decide", f"Score(Wait)  = {b:.4f}·{Q['Dry']['Wait']:.2f} + {1 - b:.4f}·{Q['Normal']['Wait']:.2f} = {scores['Wait']:.2f}"),
        step("decide", f"threshold: water when P(Dry) > {threshold:.3f}" if threshold is not None
             else "threshold: none, both actions score the same way"),
        step("decide", f"decision: {action}", "OK"),
    ]
    return {"belief": b, "scores": scores, "action": action, "threshold": threshold, "steps": steps}
