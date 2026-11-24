# GitHub About settings

Values for the About box of `lordwateroff/greenhouse-ai`. Nothing here is applied yet. Run the commands yourself after the repo is pushed.

## Description

```text
A little helper that tells you when to water your plant, and how much. Bayes, MDP and hill climbing inside.
```

105 characters. GitHub allows 350, and this fits on one line in search results.

## Website

```text
https://greenhouse-ai-blue.vercel.app
```

The live site on Vercel.

## Topics

```text
artificial-intelligence
bayesian-inference
mdp
value-iteration
hill-climbing
fastapi
python
student-project
```

## Apply with the GitHub CLI

Check that you are signed in as the repo owner first.

```bash
gh auth status
gh repo edit lordwateroff/greenhouse-ai \
  --description "Decides whether to water a plant and how much, using Bayes, MDP value iteration and hill climbing." \
  --homepage "https://greenhouse-ai-blue.vercel.app" \
  --add-topic artificial-intelligence \
  --add-topic bayesian-inference \
  --add-topic mdp \
  --add-topic value-iteration \
  --add-topic hill-climbing \
  --add-topic fastapi \
  --add-topic python \
  --add-topic student-project
```

Check the result:

```bash
gh repo view lordwateroff/greenhouse-ai --json description,homepageUrl,repositoryTopics
```

## Social preview

GitHub has no API or `gh` command for the social preview image, so upload it by hand.

1. Open the repo on github.com and go to Settings.
2. In General, find Social preview and click Edit, then Upload an image.
3. Pick `assets/social-preview.png` (1280 x 640 px, under the 1 MB limit).
4. Paste the repo link into a chat or a post to check the card. Some sites cache the old card for a while.
