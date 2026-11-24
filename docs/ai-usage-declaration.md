# AI usage declaration

Project: Mini Greenhouse Assistant
Course: AI Fundamentals, final project
Student: Miras Yessenaly (individual project)

## Summary

I used Claude Code, an AI coding assistant by Anthropic, as my helper on this project. I knew what I wanted: a simple greenhouse helper that uses Bayes, an MDP and hill climbing to decide when and how much to water a plant. Claude helped me with the design and turned my ideas into a working project: the code, the website and the documents. I chose the topic and the algorithms, set the requirements, asked for changes when something did not look right, and checked the results myself.

## Tool used

- Claude Code (Anthropic), used on my Mac.

## What the AI generated

- Python code for the three algorithms: Bayes (`greenhouse/bayes.py`), MDP value iteration and the decision under belief (`greenhouse/mdp.py`), hill climbing and restarts (`greenhouse/hill_climbing.py`), the pipeline that connects them (`greenhouse/pipeline.py`), the CLI and the experiments script.
- The FastAPI layer (`app.py`).
- The automated tests (`tests/`), written from the numbers I calculated by hand.
- The website (`public/`): one simple light page in leaf green, with a sprout logo and plain words for a plant owner.
- The documents: README, technical report, slides, defense script, demo video script, defense cheatsheet, this declaration template and the team contribution statement.

## What I did myself

- Chose topic 04, Mini Greenhouse Assistant, and the problem: noisy soil sensors.
- Chose the three algorithms and how they connect: Bayes → MDP → hill climbing.
- Wrote the full requirements (spec) for the project, including the first design. Later I asked to change the design.
- Calculated the small expected numbers by hand before the code existed: P(Dry|alert) = 0.6585, P(Dry|no alert) = 0.0508, V1 = (6, 5), the iteration-2 Q values, the 0.376 threshold, and the hill climbing paths.
- Put the expected converged values (V*(Dry) ≈ 53.1356, V*(Normal) ≈ 52.2881) in the spec. They take 148 iterations, so I did not calculate them with pen and paper. The program computes them, and the tests check them.
- Reviewed the code, the website and the documents, and asked for changes.
- Checked that the program output matches my hand calculations.
- Learned and can explain each algorithm, and will defend the project myself.

The first version of the website was dark, purple and too complicated. I asked to make it light and green, like a greenhouse, and simple enough to show to a five-year-old. I also asked that every commit on GitHub comes from my own account.

## How the work was verified

- 41 automated tests (pytest), all passing. They pin the hand-calculated values, for example P(Dry|alert) = 0.658537, V*(Dry) ≈ 53.1356, the policy Dry → Water, Normal → Wait, the 0.376 threshold and the hill climbing path 10 → 20 → 30.
- Manual recalculation of the Bayes posterior, the first two value iteration steps and the hill climbing path, compared with the CLI output.
- Browser checks of the website. The buttons "Yes, it beeped" and "No, it was quiet" flip the answer between Water and Wait, "Tricky plant" gets stuck at 20 ml, and "Try every start" finds 40 ml.
- One number by hand: 0.9 · 0.3 = 0.27 and 0.2 · 0.7 = 0.14, so P(alert) = 0.41 and P(Dry | alert) = 0.27 / 0.41 = 0.6585. The program gives the same number.

## What I learned

Bayes showed me that a sensor that is right 90% of the time can still leave us only 66% sure, because dry soil is rare and false alarms are common. The MDP taught me to compare actions by what they bring now and later, not only now. Hill climbing is simple, but it can stop on a small hill, and trying every start fixes that. The hardest part was the MDP: understanding why value iteration needs many rounds before the numbers stop changing.

## Statement

I understand every part of this project and can explain how each algorithm works, why it was chosen and how it contributes to the result. The AI was a tool. The decisions, the checking and the defense are mine.

Signed: Miras Yessenaly
Date: 25 November 2026

