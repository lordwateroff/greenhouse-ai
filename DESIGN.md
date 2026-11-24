# Sprout — design system

A light, friendly page that a child could use. One question, one answer, three small steps. Leaf green is the only strong colour. Brown means dry soil, blue means water.

**Do:** one idea per block; big buttons; plain words ("Is the soil really dry?"); numbers next to bars; hide the math in "Details for the teacher".
**Don't:** purple, gradients, glow, shadows, dark theme, sidebars, sliders on the main page, jargon on the main page, emoji, uppercase labels.

## Tokens

```css
:root {
  --bg: #f5f8f0;        /* page */
  --card: #fcfdf9;      /* cards */
  --ink: #1b2a1e;       /* text */
  --ink-2: #3f5243;     /* secondary text */
  --ink-3: #66776a;     /* captions */
  --line: #dfe7d8;      /* borders, empty bars */
  --leaf: #2e7d45;      /* primary: buttons, "water" card, winning bar */
  --leaf-dark: #1f5e32; /* links, focus ring */
  --leaf-soft: #e2f0e1; /* step numbers, hovers */
  --leaf-mid: #9fcca5;  /* losing bar, visited doses */
  --on-leaf: #f8fcf5;   /* text on green */
  --soil: #a8743f;      /* "dry" */
  --water: #3d86c6;     /* water in the cup */
}
```

## Type

- Headings: **Geologica** 500. Hero 36–60px, section 28–38px, card 22px.
- Body: **Onest**, 17px, line-height 1.5.
- Code and the log: **JetBrains Mono**.
- Sentence case. No letter-spacing.

## Shape

Radii: page cards 28, buttons 20, small blocks 14, pills 999. Spacing on a 4px scale. Borders 1px (2px on the big choice buttons). No shadows.

## Components

- **Choice buttons:** two big buttons, 60px tall. Selected = leaf green with light text; other = card with a line border.
- **Answer card:** green with a measuring cup that fills to the dose when the answer is "Water"; white with a brown clock when the answer is "Wait".
- **Step card:** number pill, question as the title, one plain sentence, one small picture (bars or dose columns), the algorithm name as a small caption at the bottom.
- **Bars:** 14px track, rounded. Winner leaf green, loser leaf-mid, dry soil brown.
- **Details for the teacher:** a native `<details>` block with a key-value list, two checkboxes and a dark log.

## Voice

Talk like you are showing it to a five-year-old. "I try a little more, then a little less." First person for the helper, short sentences, no exclamation marks.

## Motion

Bars and the cup move with ease-out (~500 ms). Nothing pulses. `prefers-reduced-motion` turns all motion off.
