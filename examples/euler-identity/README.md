# Euler's Identity -- Example Project

A ~3 minute pop-sci video explaining Euler's Identity (e^{iπ} + 1 = 0),
from the five fundamental constants to the proof via Euler's formula.

## Build

```bash
uv sync
uv run python animation/build_video.py
open media/final/euler_full.mp4
```

## Scenes

| # | Class | Content |
|---|-------|---------|
| 01 | HookScene | "The most beautiful equation" |
| 02 | TitleScene | e^{iπ} + 1 = 0 |
| 03 | IngredientsScene | Five constants: 0, 1, π, e, i |
| 04 | ComplexPlaneScene | Complex plane, i = rotation |
| 05 | EulerFormulaScene | e^{iθ} = cosθ + i sinθ, unit circle |
| 06 | PlugInPiScene | θ = π → e^{iπ} = -1 → + 1 = 0 |
| 07 | BeautyScene | Five constants + three operations |
| 08 | OutroScene | "Simplicity is beauty" |

This example was generated as an E2E test of the Auto-PopSci skill.
