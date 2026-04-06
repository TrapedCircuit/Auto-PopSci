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
Phase 1          Phase 2              Phase 3            Phase 4             Phase 5
TTS per      ->  Manim render     ->  Concat silent  ->  ONE-PASS audio  ->  SRT
segment          (reads timing,       videos (-an)       merge on full       from
                  logs timestamps)                        timeline            timestamps
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

### Phase 3: Concatenate silent videos

All per-scene Manim videos are concatenated into one silent full video:

```
ffmpeg -f concat -safe 0 -i concat.txt -c copy -an silent_full.mp4
```

The `-an` flag strips any audio. `-c copy` avoids re-encoding.

### Phase 4: One-pass audio merge

A single ffmpeg call places ALL audio segments at their **absolute** positions
on the full video timeline:

```
ffmpeg -y -i silent_full.mp4 \
  -i S01_00.mp3 -i S01_01.mp3 -i S02_00.mp3 ... \
  -filter_complex \
    "[1:a]adelay=0|0[d0];
     [2:a]adelay=11033|11033[d1];
     [3:a]adelay=18567|18567[d2];
     ...
     [d0][d1][d2]...amix=inputs=N:duration=longest:dropout_transition=0,volume=N[aout]" \
  -map 0:v -map [aout] \
  -c:v copy -c:a aac -b:a 192k \
  output_full.mp4
```

Key details:
- `adelay` values are **absolute milliseconds** = scene_offset + local_timestamp
- Scene offsets are calculated from cumulative per-scene video durations
- `volume=N` compensates for amix dividing volume by number of inputs
- `-c:v copy` avoids video re-encoding
- This produces a **single continuous audio track** with zero boundary artifacts

### Why one-pass instead of per-scene merge?

The old approach (merge audio per-scene, then concat scenes with `-c copy`)
caused AAC frame discontinuities at scene boundaries. Each scene had its own
independently-encoded audio stream, and concatenating them created pops,
clicks, and silence gaps. The one-pass approach avoids this entirely by
encoding audio only once across the full timeline.

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

3. **One-pass audio merge**: NEVER merge audio per-scene then concat.
   Always concat silent videos first, then one ffmpeg call for all audio.

4. **Save timestamps in every scene**: The last scene must explicitly call
   `self._save_stamps()` if it doesn't use `self.clear_all()`.

5. **`show_sub()` is non-blocking**: Animations play DURING narration.
   Call `pad_segment()` after animations to fill remaining TTS time.
