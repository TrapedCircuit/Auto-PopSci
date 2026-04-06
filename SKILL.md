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
Stack: Manim + edge-tts + ffmpeg.

## Parameters

Ask the user (defaults in parentheses):

| Param | Values | Default |
|-------|--------|---------|
| topic | any subject | (required) |
| language | `zh-CN`, `en-US`, `ja-JP`, ... | `zh-CN` |
| duration | `5min`, `10min`, `15min` | `10min` |
| audience | `general`, `cs-student`, `advanced` | `cs-student` |
| voice | edge-tts voice name | `zh-CN-YunxiNeural` |

## Prerequisites Check

Before starting, verify the user has these installed:

```bash
uv --version          # Package manager
ffmpeg -version       # Audio/video processing
latex --version       # For Manim's MathTex (or xelatex)
```

## Workflow

### Phase 0 -- Scaffold the project

**Important**: Create the project directory OUTSIDE any existing uv workspace,
otherwise `uv init` adds it as a workspace member instead of standalone.

```bash
mkdir <topic> && cd <topic>
uv init --name <topic>-animation --python ">=3.11"
uv add manim==0.20.1 edge-tts
mkdir animation
rm -f main.py   # uv init creates a default main.py -- delete it
```

Create `animation/base.py` by reading the scaffold file from this skill's directory.
The file is at: `<this_skill_directory>/scaffold/animation/base.py`
To find the skill directory, resolve the path of this SKILL.md file.

If you cannot find the scaffold file, create `animation/base.py` with the content
shown in the "base.py Reference" section below.

**NEVER regenerate base.py from scratch.** It contains the sync-critical
`SubtitleMixin` class. Always copy it verbatim.

### Phase 1 -- Write the narrative plan (plan.md)

Structure using the 起承转合 framework:

```
Part 1: 起 (Hook)     ~15-20%  -- Real-life scenario, paradox, title reveal
Part 2: 承 (Build)    ~30-35%  -- Intuitive analogy, step-by-step concept building
Part 3: 转 (Deepen)   ~30-35%  -- Math/formalism, derivation, key insight
Part 4: 合 (Conclude) ~15-20%  -- Applications, return to opening, closing line
```

List Scene class names (e.g. `S01_HookScene`) with one-line descriptions.

### Phase 2 -- Write the narration script (script.md)

Write the COMPLETE narration text (~250 chars/min for Chinese, ~150 words/min English).

**Every paragraph = exactly one `show_sub()` call.** This mapping is critical for sync.

```markdown
### S01 SceneName (start_time - end_time)

Narration text here.

[ANIM: what happens on screen]

Next paragraph.

[ANIM: next animation]
```

### Phase 3 -- Implement Manim scenes (animation/main.py)

```python
from base import SubtitleMixin, BG, ACCENT, OK_CLR, FAIL_CLR, MUTED, CARD_BG, FONT

class S01_HookScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("First narration sentence.")  # NON-BLOCKING
        self.play(Write(title))                      # plays DURING narration
        self.play(FadeIn(diagram))
        self.pad_segment()                           # fill remaining TTS time

        self.show_sub("Second narration sentence.")
        self.play(Transform(a, b))
        self.pad_segment()

        self.clear_all()
```

Key pattern: **show_sub → animations → pad_segment**

- `show_sub()` is NON-BLOCKING. It shows the subtitle, then returns immediately.
  Animations after it play WHILE the narration audio plays.
- `pad_segment()` waits for any remaining TTS time after animations finish.
  If animations took longer than the narration, it does nothing.
- `clear_all()` auto-calls `pad_segment()` and saves timestamps.
- For the LAST scene: if it doesn't use `clear_all()`, call `self._save_stamps()`

### Phase 4 -- Implement the build pipeline (animation/build_video.py)

Read the template at `<this_skill_directory>/scaffold/animation/build_video.py.tmpl`
and fill in these values:

- `VOICE`: the edge-tts voice name (e.g. `"zh-CN-YunxiNeural"`)
- `SCENE_ORDER`: list of scene class names from main.py
- `SCENE_SEGMENTS`: dict mapping each scene to its TTS text list
- `SRT_DISPLAY`: dict mapping each scene to its subtitle display text

**CRITICAL RULE**: `len(SCENE_SEGMENTS[scene])` MUST equal the number of
`show_sub()` calls in that scene class. The template includes `verify_segments()`
which checks this automatically before building.

### Phase 5 -- Build and verify

```bash
uv run python animation/build_video.py
open media/final/*_full.mp4
```

The pipeline runs 5 phases automatically:

```
Phase 1: Generate TTS per segment → timing.json
Phase 2: Render Manim scenes (silent video + timestamps.json)
Phase 3: Concat silent videos into one full video (video-only, -an)
Phase 4: ONE-PASS audio merge → place ALL segments at absolute timestamps
         on the full timeline using ffmpeg adelay + amix
Phase 5: Generate SRT from timestamps
```

**Why one-pass merge matters**: The old approach (per-scene audio merge then
concat) caused AAC frame discontinuities at scene boundaries, producing
audible pops and silence gaps. The new approach creates a single continuous
audio track in one ffmpeg call -- zero boundary artifacts.

## Audio-Video Sync Rules (MANDATORY)

1. **NEVER use Manim's `add_sound()`** -- it drops audio clips silently
2. **TTS per segment** -- one `.mp3` per `show_sub()` call, not per scene
3. **Timestamp logging** -- `SubtitleMixin._log_timestamp()` records Manim render time
4. **One-pass audio merge** -- concat silent videos first, then place ALL audio
   at absolute timestamps in a single ffmpeg call. NEVER merge per-scene then concat.
5. **Segment count must match** -- mismatches = desync. `verify_segments()` checks this

## Style Guide (3Blue1Brown)

### Colors
- Background: `#1a1a2e`, Card bg: `#16213e`, Subtitle bg: `#0d0d1a`
- Accent: `#f1c40f` (gold), Success: `#2ecc71`, Fail: `#e74c3c`
- Primary: `#3498db` (blue), Secondary: `#e67e22` (orange), Muted: `#7f8c8d`
- Assign each key concept its own color and use consistently across scenes

### Math formulas
- Use `MathTex` with separate strings per sub-expression for color targeting:
  `MathTex("e", "^{", "i", r"\pi", "}", font_size=72)` then `eq[0].set_color(...)`
- Use `TransformMatchingTex` for derivation steps (animates matching parts)
- Frame key results with `SurroundingRectangle(corner_radius=0.12)`

### Layout patterns
- **Card grid**: `RoundedRectangle` with field tag + symbol + description + separator line
- **Two-tier**: constants/icons on top row, operations/arrows below, result at bottom
- **Section titles**: smaller muted text at top, `FadeIn(shift=DOWN*0.15)` entrance
- **Decorative**: soft glow circles behind hero formulas (low opacity fill + stroke)

### Animation patterns
- Staggered entrance: `FadeIn(item, shift=UP*0.4)` with `lag_ratio` or loop
- Emphasis: `scale=0.7` on FadeIn for a "pop" effect
- Step labels: show before derivation, fade out after
- Unit circle: `TracedPath` + `always_redraw` for cos/sin projection lines
- Final reveal: double frame (inner solid + outer faint)

### Things to AVOID
- `letter_spacing` parameter in `Text()` -- Manim does not support it
- Raw `\text{}` in `MathTex` for Chinese -- use separate `Text()` objects
- Overly long `run_time` on `Write()` -- keep under 2.5s for readability
- Plain text-only scenes -- always add at least one visual element

## base.py Reference

If you cannot find the scaffold file, create `animation/base.py` with this exact content:

```python
from manim import *
import json
from pathlib import Path

BG = "#1a1a2e"
PROVER_CLR = "#3498db"
VERIFIER_CLR = "#e67e22"
OK_CLR = "#2ecc71"
FAIL_CLR = "#e74c3c"
ACCENT = "#f1c40f"
MUTED = "#7f8c8d"
CARD_BG = "#16213e"
SUB_BOX_CLR = "#0d0d1a"
import platform as _platform
_sys = _platform.system()
FONT = "STKaiti" if _sys == "Darwin" else "SimSun" if _sys == "Windows" else "Noto Sans CJK SC"

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_TIMING_PATH = _PROJECT_ROOT / "media" / "timing.json"
_STAMPS_PATH = _PROJECT_ROOT / "media" / "timestamps.json"

def _load_timing() -> dict:
    if _TIMING_PATH.exists():
        return json.loads(_TIMING_PATH.read_text())
    return {}

_TIMING = _load_timing()
_STAMPS: dict[str, list[float]] = {}

class SubtitleMixin:
    _sub_group: VGroup | None = None
    _sub_idx: int = 0
    _seg_start: float = 0.0
    _seg_dur: float = 0.0

    def _get_seg_duration(self) -> float:
        name = self.__class__.__name__
        if name in _TIMING and self._sub_idx < len(_TIMING[name]):
            return _TIMING[name][self._sub_idx]
        return -1

    def _log_timestamp(self):
        name = self.__class__.__name__
        if name not in _STAMPS:
            _STAMPS[name] = []
        _STAMPS[name].append(round(self.renderer.time, 4))

    def show_sub(self, text: str, *, font_size: int = 26):
        if self._seg_dur > 0:
            self.pad_segment()
        tts_dur = self._get_seg_duration()
        self._log_timestamp()
        new_txt = Text(text, font=FONT, font_size=font_size, color=WHITE, line_spacing=1.4)
        if new_txt.width > 12:
            new_txt.width = 12
        box = RoundedRectangle(
            width=config.frame_width - 0.6, height=new_txt.height + 0.45,
            corner_radius=0.12, fill_color=SUB_BOX_CLR, fill_opacity=0.82, stroke_width=0,
        )
        box.to_edge(DOWN, buff=0.22)
        new_txt.move_to(box)
        grp = VGroup(box, new_txt)
        anims = []
        if self._sub_group is not None:
            anims.append(FadeOut(self._sub_group, run_time=0.3))
        anims.append(FadeIn(grp, run_time=0.4))
        self.play(*anims)
        self._sub_group = grp
        self._seg_start = self.renderer.time
        if tts_dur > 0:
            self._seg_dur = tts_dur
        else:
            cjk = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
            self._seg_dur = max(2.0, cjk * 0.22)
        self._sub_idx += 1

    def pad_segment(self):
        if self._seg_dur <= 0:
            return
        elapsed = self.renderer.time - self._seg_start
        remaining = self._seg_dur - elapsed
        if remaining > 0.2:
            self.wait(remaining)
        self._seg_dur = 0

    def hide_sub(self):
        if self._sub_group is not None:
            self.play(FadeOut(self._sub_group, run_time=0.3))
            self._sub_group = None

    def _save_stamps(self):
        _STAMPS_PATH.write_text(json.dumps(_STAMPS, indent=2))

    def clear_all(self, run_time=0.8):
        self.pad_segment()
        self._sub_group = None
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)
        self._save_stamps()
```

## Reference

- Working example: [examples/zero-knowledge-proof/](examples/zero-knowledge-proof/)
- Sync architecture: [docs/sync-architecture.md](docs/sync-architecture.md)
- Contributing new topics: [docs/contributing.md](docs/contributing.md)
