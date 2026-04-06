# Audio-Video Sync Architecture

This document explains the timestamp-based sync pipeline that ensures narration
audio, visual animations, and subtitles stay perfectly aligned.

## The Problem

Manim renders video at its own pace. TTS generates audio independently.
If you simply overlay one on the other, they drift apart because:

- Manim animations take variable time (some `Write()` calls are 0.5s, some are 2s)
- TTS narration segments have their own fixed durations
- Concatenating scenes can introduce additional timing gaps

Naive approaches that **do not work**:

| Approach | Why it fails |
|----------|-------------|
| `Scene.add_sound()` | Silently drops audio clips after the first; only one survives |
| One TTS per scene + ffmpeg merge | No per-segment alignment; narration drifts within a scene |
| Character-count-based wait | Reading speed != TTS speed; accumulates error |

## The Solution: 5-Phase Timestamp Pipeline

```
Phase 1          Phase 2              Phase 3           Phase 4      Phase 5
TTS per      ->  Manim render     ->  ffmpeg adelay ->  Concat   ->  SRT
segment          (reads timing,       (place audio      scenes       from
                  logs timestamps)     at exact times)               timestamps
```

### Phase 1: Generate TTS per segment

Each `show_sub()` call in the Manim code corresponds to one narration segment.
We generate one MP3 file per segment and record its duration in `timing.json`.

```
media/audio/segments/
  S01_HookScene_00.mp3   (2.3s)
  S01_HookScene_01.mp3   (8.1s)
  ...
media/timing.json
  {"S01_HookScene": [2.304, 8.136, ...], ...}
```

### Phase 2: Render Manim (silent video + timestamps)

The Manim scenes import `SubtitleMixin` from `base.py`. When `show_sub()` is
called, it:

1. Reads `timing.json` to get the TTS duration for this segment
2. Logs the current renderer time to an in-memory dict
3. Shows the subtitle text on screen
4. Waits for `max(0.5, tts_duration - 0.5)` seconds

At scene end, `clear_all()` (or `_save_stamps()`) writes all accumulated
timestamps to `media/timestamps.json`:

```json
{
  "S01_HookScene": [0.0, 3.8, 19.3, 26.9, 33.7, 43.3],
  "S02_TitleScene": [0.0, 4.0],
  ...
}
```

These timestamps tell us **exactly when** each subtitle appeared in the
rendered video timeline.

### Phase 3: Place audio at timestamps via ffmpeg

For each scene, we use ffmpeg's `adelay` filter to position each audio
segment at its logged timestamp, then `amix` to combine them:

```
ffmpeg -y -i scene_video.mp4 \
  -i segment_00.mp3 -i segment_01.mp3 -i segment_02.mp3 \
  -filter_complex \
    "[1:a]adelay=0|0[d0];
     [2:a]adelay=3800|3800[d1];
     [3:a]adelay=19300|19300[d2];
     [d0][d1][d2]amix=inputs=3:duration=longest:dropout_transition=0,volume=3[aout]" \
  -map 0:v -map [aout] \
  -c:v copy -c:a aac -b:a 192k \
  output_scene.mp4
```

Key details:
- `adelay` values are in milliseconds, taken from `timestamps.json`
- `volume=N` compensates for amix dividing volume by number of inputs
- `-c:v copy` avoids video re-encoding

### Phase 4: Concatenate scenes

```
ffmpeg -f concat -safe 0 -i concat.txt -c copy final.mp4
```

Use `-c copy` (no re-encoding) to prevent any sync drift.

### Phase 5: Generate SRT

SRT timestamps are computed from:
- Scene start offset (cumulative duration of preceding scenes)
- Per-segment timestamp within the scene (from `timestamps.json`)
- Segment TTS duration (from `timing.json`) for the end time

## Critical Rules

1. **Segment count must match**: `len(SCENE_SEGMENTS[scene])` in build_video.py
   must equal the number of `show_sub()` calls in that scene class.

2. **Never use `add_sound()`**: Manim's built-in audio embedding is unreliable
   for multiple clips per scene.

3. **Always use `-c copy` for concat**: Re-encoding introduces drift.

4. **Save timestamps in every scene**: The last scene must explicitly call
   `self._save_stamps()` if it doesn't use `self.clear_all()`.
