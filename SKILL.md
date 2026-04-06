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

If you cannot find the scaffold file, copy `animation/base.py` from any
working example (e.g. `examples/euler-identity/animation/base.py`).

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

### Phase 2.5 -- Review Harness (MANDATORY)

Before implementing animations, review the plan and script against BOTH
checklists below. This is the most impactful quality gate -- a boring or
confusing script cannot be saved by good animations. If any item fails,
revise `plan.md` and `script.md` before proceeding to Phase 3.

#### Pop-sci communication checklist

Score each dimension. For any score below "good", rewrite the offending
segments before moving on.

1. **Hook strength**: Does the opening create genuine curiosity within 30s?
   Is there a question, paradox, or surprising fact -- not a textbook intro?
2. **Analogy quality**: Are analogies vivid, accurate, and grounded in
   everyday experience? Do they illuminate without oversimplifying?
3. **Jargon management**: Is every technical term explained before or upon
   first use? Could a simpler word work? Are there terms that never get used
   after being introduced?
4. **Cognitive scaffolding**: Does each concept build on the previous one?
   Is there a clear ladder from intuition to formalism, with no logical leaps?
5. **Narrative tension**: Is there an emotional arc? Does the script create
   "why?" questions and deliver satisfying "aha!" moments?
6. **Information density**: Is each segment digestible in one breath? More
   than one new concept per `show_sub()` call is a red flag -- split it.
7. **Transition flow**: Do segments connect with natural bridges ("But
   wait...", "So now the question becomes..."), not just topic jumps?
8. **Closing resonance**: Does the ending tie back to the opening and leave
   the viewer with a sense of wonder or a new mental model?

#### Animation clarity checklist

1. **Concrete before abstract**: Every formula must be preceded by a concrete
   numerical example. Never show `a·s + e = b` without first showing
   `2×3 + 5×1 + 1 = 12` with step-by-step highlighting.
2. **One idea per segment**: Each `show_sub()` should introduce exactly one
   concept. If you need two sentences to explain, split into two segments.
3. **Visual anchors**: Every abstract statement needs a visual counterpart.
   "Noise destroys solvability" → show the Gaussian elimination failing
   with actual numbers side-by-side.
4. **Step-by-step derivation**: For any math derivation, show each algebraic
   step on its own line, animating with `Write()` progressively. Use
   `TransformMatchingTex` for equation transitions (like 3Blue1Brown).
5. **Spatial intuition**: For geometric/algebraic topics, include at least one
   scene with 3D-like visualization (see "3D Visualization" section below).

If any item fails, revise the script and plan before proceeding to Phase 3.

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

### Build pipeline rules

1. **Render all scenes in ONE manim process** -- `_STAMPS` dict accumulates
   across scenes; per-scene rendering breaks timestamp continuity.
2. **Add TTS retry logic** -- edge-tts can hit transient network errors;
   retry up to 3 times with backoff.
3. **Set `PYTHONUNBUFFERED=1`** -- so build progress is visible in real-time.
4. **Add `timeout=600`** to subprocess calls -- prevents hung renders from
   blocking the pipeline forever.
5. **Never use `capture_output=True` alone** -- always use `text=True` and
   log stderr on failure for debugging.

## Audio-Video Sync Rules (MANDATORY)

1. **NEVER use Manim's `add_sound()`** -- it drops audio clips silently
2. **TTS per segment** -- one `.mp3` per `show_sub()` call, not per scene
3. **Timestamp logging** -- `SubtitleMixin._log_timestamp()` records Manim render time
4. **One-pass audio merge** -- concat silent videos first, then place ALL audio
   at absolute timestamps in a single ffmpeg call. NEVER merge per-scene then concat.
5. **Segment count must match** -- mismatches = desync. `verify_segments()` checks this

## Style Guide (3Blue1Brown)

### Subtitles

Subtitles are **off by default** (`SHOW_SUBTITLES = False` in `base.py`).
The SRT file is always generated for external subtitle use.
To enable on-screen subtitle bars, set `SHOW_SUBTITLES = True` in `base.py`.

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

### Step-by-step math derivations (3Blue1Brown style)

The single most important quality signal. Every derivation must be animated
progressively, never shown as a complete block.

```python
# GOOD: step-by-step with progressive reveal
step1 = MathTex(r"2x + 5y", "=", "11", font_size=30)
self.play(Write(step1, run_time=0.5))

step2 = MathTex(r"y = 13 - 4x", font_size=26)
step2.next_to(step1, DOWN, aligned_edge=LEFT, buff=0.3)
self.play(Write(step2, run_time=0.4))

step3 = MathTex(r"x = 3", font_size=30, color=OK_CLR)
step3.next_to(step2, DOWN, buff=0.3)
box = SurroundingRectangle(step3, corner_radius=0.08, color=OK_CLR)
self.play(Write(step3), Create(box))

# BAD: showing complete derivation at once
full = MathTex(r"2x+5y=11 \Rightarrow y=13-4x \Rightarrow x=3")
self.play(Write(full))  # student has no time to follow!
```

For equation transformations, use `TransformMatchingTex`:
```python
eq1 = MathTex(r"e^{i\pi}", "=", r"\cos\pi", "+", r"i\sin\pi")
eq2 = MathTex(r"e^{i\pi}", "=", "(-1)", "+", r"i \cdot 0")
self.play(TransformMatchingTex(eq1, eq2), run_time=1)
```

### Concrete before abstract

For any abstract formula, **always precede it with a concrete worked example**:
show specific numbers first, animate each operation, then generalize.

```python
# FIRST: concrete example with specific numbers
self.show_sub("Let's see how cosine similarity works")
comp = MathTex("3", r"\times", "4", "+", "1", r"\times", "2", "=", "14")
self.play(Write(comp))  # animate step by step

# THEN: general formula
self.show_sub("In general, we compute the dot product")
formula = MathTex(r"\vec{a} \cdot \vec{b} = \sum a_i b_i")
```

### 3D visualization (spatial topics only)

**NEVER use `ThreeDScene` with `Dot3D`/`Sphere`** -- Cairo renders each sphere
as a parametric surface; 50+ spheres can OOM or hang for minutes.

Instead, use **oblique projection** with regular `Dot` in a normal `Scene`.
See [examples/lattice-crypto/](examples/lattice-crypto/) `S04_Lattice3DScene`
for a working `_proj()` implementation with camera rotation.

### Things to AVOID
- `letter_spacing` parameter in `Text()` -- Manim does not support it
- Raw `\text{}` in `MathTex` for Chinese -- use separate `Text()` objects
- Overly long `run_time` on `Write()` -- keep under 2.5s for readability
- Plain text-only scenes -- always add at least one visual element
- `ThreeDScene` + `Dot3D`/`Sphere` for many points -- use `_proj()` instead
- Showing formulas without a preceding concrete numerical example
- Dumping a complete derivation on screen at once without progressive reveal

## Reference

- Working example: [examples/zero-knowledge-proof/](examples/zero-knowledge-proof/)
- Sync architecture: [docs/sync-architecture.md](docs/sync-architecture.md)
- Contributing new topics: [docs/contributing.md](docs/contributing.md)
