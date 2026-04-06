"""
Auto Pop-Sci -- reusable subtitle + sync infrastructure for Manim scenes.

DO NOT MODIFY this file per-project. It provides:
  - SubtitleMixin: subtitle bar, TTS-driven wait, timestamp logging
  - Shared color palette and constants

Usage in main.py:

    from base import SubtitleMixin, BG, ACCENT, ...

    class S01_HookScene(SubtitleMixin, Scene):
        def construct(self):
            self.camera.background_color = BG

            self.show_sub("Narration line 1")   # subtitle appears, audio starts here
            self.play(Write(title))              # animation plays DURING narration
            self.play(FadeIn(diagram))           # more animations
            self.pad_segment()                   # wait for remaining narration time

            self.show_sub("Narration line 2")   # next segment
            self.play(Transform(a, b))
            self.pad_segment()

            self.clear_all()
"""

from manim import *
import json
from pathlib import Path

# ── Color palette (3Blue1Brown style) ───────────────────────────────────────
BG = "#1a1a2e"
PROVER_CLR = "#3498db"
VERIFIER_CLR = "#e67e22"
OK_CLR = "#2ecc71"
FAIL_CLR = "#e74c3c"
ACCENT = "#f1c40f"
MUTED = "#7f8c8d"
CARD_BG = "#16213e"
SUB_BOX_CLR = "#0d0d1a"
SHOW_SUBTITLES = False

import platform as _platform
_sys = _platform.system()
FONT = "STKaiti" if _sys == "Darwin" else "SimSun" if _sys == "Windows" else "Noto Sans CJK SC"

# ── Paths ───────────────────────────────────────────────────────────────────
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
    """
    Mixin for Manim Scene classes. Provides:
      1. Subtitle bar at bottom of screen
      2. Non-blocking show_sub() -- animations play DURING narration
      3. pad_segment() -- fills remaining time after animations finish
      4. Timestamp logging for post-render audio placement
    """

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
        """
        Mark the start of a narration segment and (optionally) show subtitle.
        Does NOT block -- animations after this call play DURING the narration.
        Call pad_segment() when animations are done to fill remaining time.
        Set SHOW_SUBTITLES = True in base.py to render subtitle bar on screen.
        """
        if self._seg_dur > 0:
            self.pad_segment()

        tts_dur = self._get_seg_duration()
        self._log_timestamp()

        if SHOW_SUBTITLES:
            new_txt = Text(
                text, font=FONT, font_size=font_size, color=WHITE, line_spacing=1.4,
            )
            if new_txt.width > 12:
                new_txt.width = 12
            box = RoundedRectangle(
                width=config.frame_width - 0.6,
                height=new_txt.height + 0.45,
                corner_radius=0.12,
                fill_color=SUB_BOX_CLR, fill_opacity=0.82,
                stroke_width=0,
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
        """Wait for the remaining TTS duration after animations have played."""
        if self._seg_dur <= 0:
            return
        elapsed = self.renderer.time - self._seg_start
        remaining = self._seg_dur - elapsed
        if remaining > 0.2:
            self.wait(remaining)
        self._seg_dur = 0

    def hide_sub(self):
        if SHOW_SUBTITLES and self._sub_group is not None:
            self.play(FadeOut(self._sub_group, run_time=0.3))
            self._sub_group = None

    def _save_stamps(self):
        _STAMPS_PATH.write_text(json.dumps(_STAMPS, indent=2))

    def clear_all(self, run_time=0.8):
        self.pad_segment()
        self._sub_group = None
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)
        self._save_stamps()
