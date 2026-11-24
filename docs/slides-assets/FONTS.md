# Fonts in the slides

The website fonts (Geologica, Onest, JetBrains Mono) are not installed on this Mac.
Keynote and PowerPoint would replace them with a random font, and text could overflow.

So `docs/presentation.pptx` uses fonts that every Mac already has:

| Role | Website | In the deck |
|---|---|---|
| Display, titles | Geologica 500 | Helvetica Neue |
| Body | Onest | Helvetica Neue |
| Numbers, units, code | JetBrains Mono | Menlo |

- On a Mac (Keynote or PowerPoint) the deck looks exactly as designed.
- On Windows PowerPoint, Helvetica Neue and Menlo are missing and fall back to similar fonts (usually Arial and a Courier-like mono). Layout stays close, but check before presenting.
- `docs/presentation.pdf` has the fonts embedded. If anything looks off on the defense computer, present the PDF.

Charts, the green title band and the QR code are PNG images in this folder, so they never change.

To change the fonts or the live URL, edit the top of `docs/build_slides.py` and run:

```
.venv/bin/python docs/build_slides.py --url https://your-live-url
```
