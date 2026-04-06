# Auto Pop-Sci

Generate broadcast-quality math/science popularization videos automatically
using [Manim](https://www.manim.community/) animations and AI narration.

**Stack**: Manim (animation) + edge-tts (AI voice) + ffmpeg (audio sync) + uv (package management)

## What It Does

Given a topic (e.g. "Zero-Knowledge Proofs"), Auto Pop-Sci guides you through:

1. **Narrative design** -- structured outline using the 起承转合 (hook / build / deepen / conclude) framework
2. **Script writing** -- complete narration text with animation cues
3. **Manim animation** -- 3Blue1Brown-style scenes with math formulas, diagrams, and transitions
4. **AI narration** -- natural-sounding voice via Microsoft Edge TTS (free, supports 40+ languages)
5. **Synced final video** -- timestamp-based pipeline ensures audio, video, and subtitles stay perfectly aligned

## Install

One-command install via the [skills CLI](https://github.com/vercel-labs/skills)
(works with Cursor, Claude Code, Codex, and 40+ agents):

```bash
npx skills add TrapedCircuit/Auto-PopSci
```

## Quick Start

After installing, ask your agent:

> "Generate a 10-minute science video explaining the Fourier Transform"

The agent will follow the skill instructions to scaffold the project, write the
narrative, implement animations, and build the final video.

### Build the Examples

```bash
# Transformer (~5 min)
cd examples/transformer
uv sync
uv run python animation/build_video.py
open media/final/transformer_full.mp4

# Lattice Cryptography (~10 min, has 3D visualization)
cd examples/lattice-crypto
uv sync
uv run python animation/build_video.py
open media/final/output_full.mp4
```

## Parameters

| Parameter | Options | Default |
|-----------|---------|---------|
| **topic** | Any math/science subject | (required) |
| **language** | `zh-CN`, `en-US`, `ja-JP`, ... | `zh-CN` |
| **duration** | `5min`, `10min`, `15min` | `10min` |
| **audience** | `general`, `cs-student`, `advanced` | `cs-student` |
| **voice** | Any [edge-tts voice](https://gist.github.com/BettyJJ/17cbaa1de96235a7f5773b8571a4b138) | `zh-CN-YunxiNeural` |
| **style** | `3b1b`, `whiteboard`, `slides` | `3b1b` |

## Project Structure

```
Auto-PopSci/
  SKILL.md                          # Cursor Agent Skill
  scaffold/                         # Reusable template files
    animation/
      base.py                       # SubtitleMixin (sync infrastructure)
      build_video.py.tmpl           # Build pipeline template
    pyproject.toml.tmpl
  examples/
    zero-knowledge-proof/           # Working example (~10 min video)
      plan.md                       # Narrative outline
      script.md                     # Full narration (~2400 chars)
      animation/
        main.py                     # 14 Manim scenes
        build_video.py              # Build pipeline
    transformer/                    # Working example (~5 min video)
      plan.md                       # Narrative outline
      script.md                     # Full narration (~1100 chars)
      animation/
        main.py                     # 8 Manim scenes
        build_video.py              # Build pipeline
    lattice-crypto/                 # Working example (~10 min, has 3D)
      plan.md                       # Narrative outline
      script.md                     # Full narration (~2500 chars)
      animation/
        main.py                     # 9 scenes (incl. 3D lattice)
        build_video.py              # Build pipeline
  docs/
    sync-architecture.md            # How the audio sync works
    contributing.md                 # How to add new topics
```

## Audio Sync Pipeline

The hardest part of this project is keeping audio, video, and subtitles in sync.
We use a 5-phase timestamp-based approach:

```
Phase 1: TTS per segment  -->  timing.json (durations)
Phase 2: Render Manim     -->  timestamps.json (render times)
Phase 3: ffmpeg adelay    -->  audio placed at exact positions
Phase 4: Concat scenes    -->  final video (-c copy, no re-encode)
Phase 5: Generate SRT     -->  subtitles from real timestamps
```

See [docs/sync-architecture.md](docs/sync-architecture.md) for the full explanation
and the critical rules that must not be violated.

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | >= 3.11 | Runtime |
| [uv](https://docs.astral.sh/uv/) | latest | Package management |
| [manim](https://www.manim.community/) | 0.20.1 (pinned) | Animation rendering |
| [edge-tts](https://github.com/rany2/edge-tts) | >= 7.2.8 | AI voice synthesis |
| ffmpeg | latest | Audio merge + video concat |
| LaTeX | any | Manim's MathTex rendering |

## Contributing

Want to add a new topic? See [docs/contributing.md](docs/contributing.md).

## License

MIT
