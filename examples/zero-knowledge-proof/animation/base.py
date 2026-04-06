"""
Auto Pop-Sci -- reusable subtitle + sync infrastructure for Manim scenes.

DO NOT MODIFY this file per-project. It provides:
  - SubtitleMixin: subtitle bar, TTS-driven wait, timestamp logging
  - Shared color palette and constants

Import in your main.py:
    from base import SubtitleMixin, BG, ACCENT, PROVER_CLR, ...
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

# CJK font selection: STKaiti (macOS), Noto Sans CJK SC (Linux), SimSun (Windows)
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


# ── SubtitleMixin ───────────────────────────────────────────────────────────
class SubtitleMixin:
    """
    Mixin for Manim Scene classes that provides:
      1. A subtitle bar at the bottom of the screen
      2. TTS-driven wait times (reads media/timing.json)
      3. Timestamp logging for audio sync (writes media/timestamps.json)

    Usage:
        class MyScene(SubtitleMixin, Scene):
            def construct(self):
                self.camera.background_color = BG
                self.show_sub("Narration text")
                # ... animations ...
                self.clear_all()
    """

    _sub_group: VGroup | None = None
    _sub_idx: int = 0

    def _get_seg_duration(self) -> float:
        """Get TTS duration for the current segment from timing.json."""
        name = self.__class__.__name__
        if name in _TIMING and self._sub_idx < len(_TIMING[name]):
            return _TIMING[name][self._sub_idx]
        return -1

    def _log_timestamp(self):
        """Record the current renderer time for post-render audio placement."""
        name = self.__class__.__name__
        if name not in _STAMPS:
            _STAMPS[name] = []
        t = self.renderer.time
        _STAMPS[name].append(round(t, 4))

    def show_sub(self, text: str, *, wait: float = -1, font_size: int = 26):
        """
        Show subtitle text and wait for TTS duration.

        Args:
            text: Subtitle text displayed on screen
            wait: -1 = auto (use TTS duration), 0 = no wait, >0 = explicit seconds
            font_size: subtitle font size
        """
        tts_dur = self._get_seg_duration()
        self._log_timestamp()

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
        """Persist timestamps to disk. Called by clear_all and at end of last scene."""
        _STAMPS_PATH.write_text(json.dumps(_STAMPS, indent=2))

    def clear_all(self, run_time=0.8):
        """Fade out everything and save timestamps."""
        self._sub_group = None
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)
        self._save_stamps()
