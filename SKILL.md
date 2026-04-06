---
name: auto-pop-sci
description: >-
  Generate math/science popularization videos with Manim animations and AI
  narration. Use when the user asks to create an explainer video, science
  animation, math tutorial, or pop-sci content on any topic. Handles the full
  pipeline from narrative design to final rendered video with synced audio.
---

# Auto Pop-Sci

Generate broadcast-quality science popularization videos from a topic prompt.
Stack: Manim (animation) + edge-tts (narration) + ffmpeg (audio sync).

## Parameters

Ask the user for these before starting. Defaults in parentheses.

| Param | Values | Default |
|-------|--------|---------|
| topic | any subject | (required) |
| language | `zh-CN`, `en-US`, `ja-JP`, ... | `zh-CN` |
| duration | `5min`, `10min`, `15min` | `10min` |
| audience | `general`, `cs-student`, `advanced` | `cs-student` |
| voice | any edge-tts voice | `zh-CN-YunxiNeural` |
| style | `3b1b`, `whiteboard`, `slides` | `3b1b` |

## Workflow

### Phase 0 -- Scaffold the project

```
uv init --name <topic>-animation --python ">=3.11"
uv add manim==0.20.1 edge-tts
```

Copy `scaffold/animation/base.py` into `<project>/animation/base.py`.
This file contains `SubtitleMixin` and the timestamp sync system -- NEVER regenerate it.

Create the project layout:

```
<topic>/
  plan.md              # Narrative outline
  script.md            # Full narration with [ANIM] cues
  animation/
    base.py            # FROM scaffold (do not modify)
    main.py            # Manim scenes
    build_video.py     # Build pipeline
  pyproject.toml
```

### Phase 1 -- Write the narrative plan (plan.md)

Structure the video using the 起承转合 (qi-cheng-zhuan-he) framework:

```
Part 1: 起 (Hook)     ~15-20% of duration
  - Real-life scenario or paradox that grabs attention
  - Title reveal

Part 2: 承 (Build)    ~30-35% of duration
  - Intuitive analogy or thought experiment
  - Build the core concept step by step
  - Formalize key properties

Part 3: 转 (Deepen)   ~30-35% of duration
  - Transition from intuition to math/formalism
  - Step-by-step derivation or proof
  - Key insight that connects back to the analogy

Part 4: 合 (Conclude) ~15-20% of duration
  - Real-world applications
  - Return to opening question
  - Philosophical or memorable closing line
```

Each section lists its Manim Scene class names and a one-line description.

### Phase 2 -- Write the narration script (script.md)

Write the COMPLETE narration text (~250 chars/min for Chinese, ~150 words/min for English).
Every paragraph maps to one `show_sub()` call in the Manim code.

Format:

```markdown
### S01 SceneName (start_time - end_time)

Narration text here. This is what the TTS will speak.

[ANIM: description of what happens on screen]

Next narration paragraph.

[ANIM: next animation description]
```

### Phase 3 -- Implement Manim scenes (animation/main.py)

Import `SubtitleMixin` from `base.py`:

```python
from base import SubtitleMixin, BG, ACCENT, ...

class S01_HookScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG
        self.show_sub("Narration text here.")
        # ... animations ...
        self.clear_all()
```

Rules:
- Every scene class inherits `(SubtitleMixin, Scene)`
- Every narration beat = one `self.show_sub("...")` call
- `show_sub` auto-waits based on TTS duration from `timing.json`
- End each scene with `self.clear_all()` or `self._save_stamps()` for the last scene

### Phase 4 -- Implement the build pipeline (animation/build_video.py)

Define `SCENE_SEGMENTS` dict mapping each scene to its TTS text list.

**CRITICAL**: The number of entries in `SCENE_SEGMENTS[scene]` MUST exactly match
the number of `show_sub()` calls in that scene class. Mismatches cause audio desync.

The build pipeline runs 5 phases:

```
Phase 1: Generate TTS → media/audio/segments/S01_SceneName_00.mp3, ...
         Save durations → media/timing.json
Phase 2: Render Manim → media/videos/main/1080p60/S01_SceneName.mp4
         Scenes read timing.json for wait durations
         Scenes write media/timestamps.json (renderer time per show_sub)
Phase 3: ffmpeg adelay → place each audio segment at its exact timestamp
         Merge with video → media/final/S01_SceneName.mp4
Phase 4: ffmpeg concat → media/final/<topic>_full.mp4
Phase 5: Generate SRT → media/final/<topic>_full.srt
```

See `scaffold/animation/build_video.py.tmpl` for the template.
See `docs/sync-architecture.md` for detailed explanation.

### Phase 5 -- Build and verify

```bash
uv run python animation/build_video.py
open media/final/<topic>_full.mp4
```

## Audio-Video Sync Rules (MANDATORY)

These rules were learned through extensive debugging. Violating any of them
will cause audio desync.

1. **NEVER use Manim's `add_sound()`** for multi-segment audio. It silently
   drops clips after the first one. Audio embedding must be done via ffmpeg.

2. **Generate TTS per subtitle segment**, not per scene. One `.mp3` file per
   `show_sub()` call. This is how we know the exact duration of each narration beat.

3. **Log Manim renderer timestamps** via `SubtitleMixin._log_timestamp()`.
   The timestamps record exactly when each subtitle appears in the video timeline.

4. **Use ffmpeg `adelay` filter** to place each audio segment at its logged
   timestamp position, then `amix` to combine. Use `volume=N` to compensate
   for amix volume division.

5. **Use `-c copy`** when concatenating scene videos. Re-encoding can introduce
   A/V sync drift.

6. **Segment count must match**. If a scene has N `show_sub()` calls, the
   `SCENE_SEGMENTS` dict for that scene must have exactly N entries.
   Audit this by running: `grep -c 'show_sub' animation/main.py` per class.

## Style Guide (3Blue1Brown)

When `style=3b1b`:
- Background: `#1a1a2e` (deep blue-black)
- Accent: `#f1c40f` (gold for highlights)
- Success: `#2ecc71`, Fail: `#e74c3c`
- Primary role color: `#3498db` (blue), Secondary: `#e67e22` (orange)
- Math formulas: `MathTex` with color highlights on key terms
- Subtitle bar: semi-transparent dark box at bottom, white text
- Transitions: `FadeIn`, `Write`, `Transform`, `ReplacementTransform`
- Chinese font: `STKaiti`; fallback: `Noto Sans CJK SC`

## Reference

- Working example: `examples/zero-knowledge-proof/`
- Sync architecture doc: `docs/sync-architecture.md`
- Contribution guide: `docs/contributing.md`
