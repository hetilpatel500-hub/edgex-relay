# DEMO SAMPLE: Pitch deck (Hearthloop, fictional)

> **Portfolio sample. Not client work.** "Hearthloop" is a fictional
> startup made up by Edgex. Market, traction, team and ask figures are
> labeled placeholders. The competitor rows use real public prices found
> 2026-09-25 (see `gig4-market-research-DEMO.md`). Written with AI
> assistance and reviewed.

Files:
- `gig3-pitch-deck-DEMO-hearthloop.pptx`: the editable deck (9 slides).
- `gig3-pitch-deck-DEMO-hearthloop.pdf`: PDF copy. Upload this to the
  pitch deck gig's gallery.
- `gig3-hearthloop-spec.json`: the slide content the deck was built from.

How it was built (same as real orders):

```
python3 ../tools/build_deck.py gig3-hearthloop-spec.json gig3-pitch-deck-DEMO-hearthloop.pptx
soffice --headless --convert-to pdf gig3-pitch-deck-DEMO-hearthloop.pptx
```

No watermark, no paid tool. Charts are native PowerPoint charts, so the
buyer can edit the numbers (right-click > Edit Data). Every slide footer
says "DEMO SAMPLE, fictional company".

## Slides

1. **Hearthloop**: title, one-line pitch, demo note.
2. **The problem**: bulky single-use bottles; no storage; refill shops need a trip.
3. **Our solution**: today vs. with Hearthloop.
4. **How it works**: 3 steps.
5. **Market (placeholder)**: TAM / SAM / SOM layout; real orders cite sources.
6. **Traction (placeholder)**: editable bar chart, demo numbers.
7. **Competition**: table with real, cited competitor prices plus the demo company.
8. **Team (placeholder)**: three cards.
9. **The ask**: amount placeholder and use-of-funds bars.

An earlier version was made in Gamma (https://gamma.app/docs/i001pc4nq7l92cd).
It is not used: free Gamma exports carry a "Made with Gamma" watermark.
