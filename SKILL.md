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

```bash
uv init --name <topic>-animation --python ">=3.11"
uv add manim==0.20.1 edge-tts
mkdir animation
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
        self.show_sub("First narration sentence.")
        # ... animations ...
        self.show_sub("Second narration sentence.")
        # ... more animations ...
        self.clear_all()
```

Rules:
- Inherit `(SubtitleMixin, Scene)` -- SubtitleMixin MUST be first
- One `show_sub()` per narration paragraph from script.md
- `show_sub` auto-waits for the TTS duration (reads `media/timing.json`)
- End each scene with `self.clear_all()`
- For the LAST scene only: if it doesn't call `clear_all()`, call `self._save_stamps()` at the very end

### Phase 4 -- Implement the build pipeline (animation/build_video.py)

Read the template at `<this_skill_directory>/scaffold/animation/build_video.py.tmpl`
and fill in these values:

- `VOICE`: the edge-tts voice name (e.g. `"zh-CN-YunxiNeural"`)
- `SCENE_ORDER`: list of scene class names from main.py
- `SCENE_SEGMENTS`: dict mapping each scene to its TTS text list
- `SRT_DISPLAY`: dict mapping each scene to its subtitle display text

**CRITICAL RULE**: `len(SCENE_SEGMENTS[scene])` MUST equal the number of
`show_sub()` calls in that scene class. Run the verification step below.

### Phase 5 -- Verify segment counts

Before building, verify that segment counts match `show_sub()` counts.
For each scene class in main.py, count `show_sub` calls and compare with
`SCENE_SEGMENTS`. If they don't match, the audio WILL desync.

```python
# Quick check (add to end of build_video.py, run before build)
import re
with open("animation/main.py") as f:
    code = f.read()
for scene in SCENE_ORDER:
    n_seg = len(SCENE_SEGMENTS[scene])
    pattern = rf"class {scene}\b.*?(?=\nclass |\Z)"
    match = re.search(pattern, code, re.DOTALL)
    n_sub = match.group().count("show_sub(") if match else 0
    status = "OK" if n_seg == n_sub else "MISMATCH"
    print(f"  {scene}: {n_seg} segments, {n_sub} show_sub calls -- {status}")
```

Fix any mismatches before proceeding.

### Phase 6 -- Build and verify

```bash
uv run python animation/build_video.py
open media/final/*_full.mp4
```

## Audio-Video Sync Rules (MANDATORY)

1. **NEVER use Manim's `add_sound()`** -- it drops audio clips silently
2. **TTS per segment** -- one `.mp3` per `show_sub()` call, not per scene
3. **Timestamp logging** -- `SubtitleMixin._log_timestamp()` records Manim render time
4. **ffmpeg `adelay`** -- places audio at exact logged positions. Use `volume=N` for amix
5. **`-c copy` for concat** -- re-encoding causes drift
6. **Segment count must match** -- mismatches = desync. Always verify (Phase 5)

## Style Guide (3Blue1Brown)

- Background: `#1a1a2e`, Accent: `#f1c40f` (gold)
- Success: `#2ecc71`, Fail: `#e74c3c`
- Primary: `#3498db` (blue), Secondary: `#e67e22` (orange)
- Math: `MathTex` with color highlights
- Subtitle: semi-transparent dark box at bottom
- Transitions: `FadeIn`, `Write`, `Transform`, `ReplacementTransform`

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

    def show_sub(self, text: str, *, wait: float = -1, font_size: int = 26):
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
        if wait == -1:
            if tts_dur > 0:
                w = max(0.5, tts_dur - 0.5)
            else:
                cjk = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
                w = max(2.0, cjk * 0.22)
            self.wait(w)
        elif wait > 0:
            self.wait(wait)
        self._sub_idx += 1

    def hide_sub(self):
        if self._sub_group is not None:
            self.play(FadeOut(self._sub_group, run_time=0.3))
            self._sub_group = None

    def _save_stamps(self):
        _STAMPS_PATH.write_text(json.dumps(_STAMPS, indent=2))

    def clear_all(self, run_time=0.8):
        self._sub_group = None
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)
        self._save_stamps()
```

## Reference

- Working example: [examples/zero-knowledge-proof/](examples/zero-knowledge-proof/)
- Sync architecture: [docs/sync-architecture.md](docs/sync-architecture.md)
- Contributing new topics: [docs/contributing.md](docs/contributing.md)
