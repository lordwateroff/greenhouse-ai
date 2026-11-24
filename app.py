"""Thin FastAPI layer over the greenhouse package.

On Vercel, files in public/ are served by the CDN. Locally (offline demo),
FastAPI serves public/ itself.
"""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator, model_validator

from greenhouse import config
from greenhouse.experiments import run_all
from greenhouse.pipeline import run_pipeline

PUBLIC = Path(__file__).parent / "public"

app = FastAPI(title="Mini Greenhouse Assistant")



class RunInput(BaseModel):
    """Every field is optional; missing ones take the defaults from config.py."""

    observation: str = "alert"
    prior_dry: float = Field(config.PRIOR_DRY, ge=0.0, le=1.0)
    p_alert_given_dry: float = Field(config.P_ALERT_GIVEN_DRY, ge=0.0, le=1.0)
    p_alert_given_normal: float = Field(config.P_ALERT_GIVEN_NORMAL, ge=0.0, le=1.0)
    gamma: float = Field(config.GAMMA, ge=0.0, lt=1.0)
    rewards: dict[str, dict[str, float]] = config.REWARDS
    transitions: dict[str, dict[str, dict[str, float]]] = config.TRANSITIONS
    doses: list[int] = config.DOSES
    scores: list[float] | None = None
    start_dose: int = config.START_DOSE
    tricky: bool = False
    restarts: bool = False

    @field_validator("observation")
    @classmethod
    def known_observation(cls, v: str) -> str:
        if v not in ("alert", "no_alert"):
            raise ValueError("observation must be 'alert' or 'no_alert'")
        return v

    @model_validator(mode="after")
    def tables_make_sense(self):
        for s in config.STATES:
            for a in config.ACTIONS:
                if s not in self.rewards or a not in self.rewards[s]:
                    raise ValueError(f"missing reward for ({s}, {a})")
                row = self.transitions.get(s, {}).get(a)
                if row is None:
                    raise ValueError(f"missing transitions for ({s}, {a})")
                if any(p < 0 or p > 1 for p in row.values()):
                    raise ValueError(f"transition probabilities for ({s}, {a}) must be between 0 and 1")
                if abs(sum(row.values()) - 1.0) > 1e-6:
                    raise ValueError(f"transitions for ({s}, {a}) must add up to 1")
        if self.scores is not None and len(self.scores) != len(self.doses):
            raise ValueError("doses and scores must have the same length")
        if self.start_dose not in self.doses:
            raise ValueError("start_dose must be one of the doses")
        return self


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/defaults")
def defaults() -> dict:
    return config.defaults()


@app.post("/api/run")
def run(body: RunInput | None = None) -> dict:
    body = body or RunInput()
    try:
        return run_pipeline(**body.model_dump())
    except ValueError as e:  # impossible combos the validator cannot see (e.g. zero evidence)
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/api/experiments")
def experiments() -> dict:
    return run_all()


@app.get("/")
def index():
    return FileResponse(PUBLIC / "index.html")


# Local/offline only: Vercel serves public/ from its CDN and says not to mount it.
if not os.environ.get("VERCEL") and PUBLIC.exists():
    app.mount("/", StaticFiles(directory=PUBLIC), name="public")
