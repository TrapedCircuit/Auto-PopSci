# Zero-Knowledge Proof -- Example Project

A 10-minute science popularization video explaining Zero-Knowledge Proofs,
from the Ali Baba cave analogy to the Schnorr protocol.

## Prerequisites

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) package manager
- ffmpeg (`brew install ffmpeg` on macOS)
- LaTeX distribution (for Manim's MathTex)

## Build

```bash
# Install dependencies
uv sync

# Run the full pipeline (TTS + render + audio merge + concat + SRT)
uv run python animation/build_video.py

# Output
open media/final/zkp_full.mp4       # Final video (1080p60, ~10 min)
open media/final/zkp_full.srt       # Subtitles
```

## Files

| File | Description |
|------|-------------|
| `plan.md` | Narrative outline (起承转合 structure) |
| `script.md` | Full narration script with `[ANIM]` cues |
| `animation/main.py` | 14 Manim scenes |
| `animation/build_video.py` | 5-phase build pipeline |

## Scenes

| # | Class | Content | Duration |
|---|-------|---------|----------|
| 01 | HookScene | Real-life scenario + paradox | ~55s |
| 02 | TitleScene | Lock icon + title | ~10s |
| 03 | CaveIntroScene | Ali Baba cave setup | ~38s |
| 04 | CaveProtocolScene | Protocol: success + failure | ~60s |
| 05 | ProbabilityScene | Probability decay chart | ~39s |
| 06 | CoreInsightScene | Victor's perspective | ~23s |
| 07 | PropertiesScene | Three property cards | ~34s |
| 08 | MathBridgeScene | One-way functions | ~32s |
| 09 | DiscreteLogScene | Discrete logarithm | ~39s |
| 10 | SchnorrProtocolScene | Schnorr protocol 4 steps | ~96s |
| 11 | VerificationScene | Equation expansion | ~43s |
| 12 | SimulatorScene | Simulator argument | ~57s |
| 13 | ApplicationScene | Real-world applications | ~37s |
| 14 | OutroScene | Closing + philosophy | ~43s |
