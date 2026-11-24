"""Mini Greenhouse Assistant: Bayes -> MDP -> hill climbing."""


def step(source: str, text: str, status: str = ">>") -> dict:
    """One line of the 'how we got here' log. status: 'OK', '>>' or '..'."""
    return {"status": status, "source": source, "text": text}
