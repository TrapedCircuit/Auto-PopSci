"""Euler's Identity -- build pipeline (one-pass audio merge)."""

import asyncio
import json
import re
import subprocess
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent.parent
MEDIA = ROOT / "media"
SEG_DIR = MEDIA / "audio" / "segments"
FINAL_DIR = MEDIA / "final"
VIDEO_DIR = MEDIA / "videos" / "main" / "1080p60"

VOICE = "zh-CN-YunxiNeural"

SCENE_ORDER = [
    "S01_HookScene", "S02_TitleScene", "S03_IngredientsScene",
    "S04_ComplexPlaneScene", "S05_EulerFormulaScene", "S06_PlugInPiScene",
    "S07_BeautyScene", "S08_OutroScene",
]

SCENE_SEGMENTS = {
    "S01_HookScene": [
        "数学家们投票选出了人类历史上最美丽的公式。获胜的不是什么复杂的定理，而是一个极其简洁的等式。",
        "它只用了五个数字和三种运算，却把数学中最重要的五个常数，联系在了一起。",
    ],
    "S02_TitleScene": [
        "这就是欧拉恒等式。",
    ],
    "S03_IngredientsScene": [
        "让我们先认识一下这五位主角。零，加法的起点。一，乘法的起点。圆周率π，圆的灵魂。自然常数e，增长的本质。虚数单位i，它满足i的平方等于负一。",
        "这五个数分别来自数学的不同分支，看似毫无关联。欧拉恒等式说的是：它们之间存在一个惊人的等式。",
    ],
    "S04_ComplexPlaneScene": [
        "要理解这个等式，我们先要理解虚数i到底意味着什么。",
        "乘以负一意味着翻转方向。乘以i呢？i的平方等于负一，所以乘两次i等于翻转。那乘一次i，就是旋转九十度。",
        "这就是复平面：横轴是实数，纵轴是虚数。乘以i就是逆时针旋转九十度。",
    ],
    "S05_EulerFormulaScene": [
        "现在登场的是欧拉公式。它说，e的i乘以θ次方，等于cos θ加上i乘以sin θ。",
        "当θ从零开始增大，e的iθ次方会在复平面的单位圆上移动。θ就是旋转的角度。",
        "欧拉公式把指数函数和三角函数，通过虚数i，完美地统一在了一起。",
    ],
    "S06_PlugInPiScene": [
        "现在，让我们把θ设为π。cos π等于负一，sin π等于零。",
        "所以e的iπ次方等于负一。两边加一，就得到了欧拉恒等式：e的iπ次方加一等于零。",
    ],
    "S07_BeautyScene": [
        "为什么说它是最美丽的等式？因为它用了五个最基本的常数和三种最基本的运算。一个等式，把整个数学大厦的地基连在了一起。",
    ],
    "S08_OutroScene": [
        "简洁即美。在数学的世界里，最深刻的真理，往往藏在最简单的形式之中。",
        "这就是欧拉恒等式的美。",
    ],
}

SRT_DISPLAY = {
    "S01_HookScene": ["数学家们投票选出了\n人类历史上最美丽的公式。", "它只用了五个数字和三种运算，\n却把五个最重要的常数联系在了一起。"],
    "S02_TitleScene": ["这就是欧拉恒等式。"],
    "S03_IngredientsScene": ["五位主角：0, 1, π, e, i", "它们来自不同分支，\n却被一个等式联系在一起。"],
    "S04_ComplexPlaneScene": ["虚数 i 意味着什么？", "乘以 i = 旋转 90°", "复平面：实轴 + 虚轴"],
    "S05_EulerFormulaScene": ["欧拉公式：e^{iθ} = cosθ + i·sinθ", "e^{iθ} 在单位圆上移动", "指数函数与三角函数的统一"],
    "S06_PlugInPiScene": ["令 θ = π：cos π = -1, sin π = 0", "e^{iπ} + 1 = 0"],
    "S07_BeautyScene": ["五个常数 + 三种运算 = 一个等式"],
    "S08_OutroScene": ["简洁即美。", "这就是欧拉恒等式的美。"],
}


def get_duration(path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "json", str(path)], capture_output=True, text=True)
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except (KeyError, json.JSONDecodeError):
        return 2.0


def verify_segments():
    print("=== Verify segment counts ===")
    with open(ROOT / "animation" / "main.py") as f:
        code = f.read()
    ok = True
    for scene in SCENE_ORDER:
        n_seg = len(SCENE_SEGMENTS[scene])
        pattern = rf"class {scene}\b.*?(?=\nclass |\Z)"
        match = re.search(pattern, code, re.DOTALL)
        n_sub = match.group().count("show_sub(") if match else 0
        status = "OK" if n_seg == n_sub else "MISMATCH"
        if status != "OK":
            ok = False
        print(f"  {scene}: {n_seg} segments, {n_sub} show_sub -- {status}")
    if not ok:
        raise SystemExit("Fix mismatches!")
    print()


async def phase1_generate_tts():
    print("=== Phase 1: Generate TTS ===")
    SEG_DIR.mkdir(parents=True, exist_ok=True)
    for scene in SCENE_ORDER:
        for i, text in enumerate(SCENE_SEGMENTS[scene]):
            out = SEG_DIR / f"{scene}_{i:02d}.mp3"
            if not out.exists() or out.stat().st_size < 100:
                comm = edge_tts.Communicate(text, VOICE, rate="-5%", pitch="+0Hz")
                await comm.save(str(out))
                print(f"    {out.name}")
    timing = {}
    for scene in SCENE_ORDER:
        durs = [round(get_duration(SEG_DIR / f"{scene}_{i:02d}.mp3"), 3)
                for i in range(len(SCENE_SEGMENTS[scene]))]
        timing[scene] = durs
        print(f"  {scene}: {len(durs)} segs, {sum(durs):.1f}s")
    (MEDIA / "timing.json").write_text(json.dumps(timing, indent=2))


def phase2_render_manim():
    print("\n=== Phase 2: Render Manim (silent) ===")
    scenes = " ".join(SCENE_ORDER)
    subprocess.run(
        f"cd {ROOT} && uv run manim render -qh animation/main.py {scenes}",
        shell=True, capture_output=True)
    for s in SCENE_ORDER:
        p = VIDEO_DIR / f"{s}.mp4"
        print(f"  {s}: {get_duration(p):.1f}s" if p.exists() else f"  {s}: MISSING!")


def phase3_concat_silent():
    print("\n=== Phase 3: Concat silent videos ===")
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    concat = FINAL_DIR / "concat.txt"
    lines = [f"file '{VIDEO_DIR / f'{s}.mp4'}'" for s in SCENE_ORDER
             if (VIDEO_DIR / f"{s}.mp4").exists()]
    concat.write_text("\n".join(lines))

    silent = FINAL_DIR / "silent_full.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat), "-c", "copy", "-an", str(silent),
    ], capture_output=True)
    dur = get_duration(silent)
    print(f"  Silent video: {dur:.1f}s")
    return silent


def phase4_merge_audio(silent_path):
    print("\n=== Phase 4: One-pass audio merge ===")
    stamps = json.loads((MEDIA / "timestamps.json").read_text())

    scene_offsets = {}
    cumulative = 0.0
    for s in SCENE_ORDER:
        scene_offsets[s] = cumulative
        p = VIDEO_DIR / f"{s}.mp4"
        if p.exists():
            cumulative += get_duration(p)

    all_segments = []
    for scene in SCENE_ORDER:
        if scene not in stamps:
            continue
        base = scene_offsets[scene]
        for i, local_t in enumerate(stamps[scene]):
            seg_file = SEG_DIR / f"{scene}_{i:02d}.mp3"
            if seg_file.exists():
                abs_ms = int((base + local_t) * 1000)
                all_segments.append((abs_ms, str(seg_file)))

    n = len(all_segments)
    print(f"  Placing {n} audio segments on full timeline")

    cmd = ["ffmpeg", "-y", "-i", str(silent_path)]
    for _, path in all_segments:
        cmd.extend(["-i", path])

    filter_parts = []
    for i, (delay_ms, _) in enumerate(all_segments):
        filter_parts.append(f"[{i+1}:a]adelay={delay_ms}|{delay_ms}[d{i}]")

    mix_labels = "".join(f"[d{i}]" for i in range(n))
    filter_parts.append(
        f"{mix_labels}amix=inputs={n}:duration=longest"
        f":dropout_transition=0,volume={n}[aout]"
    )

    output = FINAL_DIR / "euler_full.mp4"
    cmd.extend([
        "-filter_complex", ";".join(filter_parts),
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        str(output),
    ])

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERROR: {r.stderr[-500:]}")
    else:
        dur = get_duration(output)
        print(f"  Final: {output} ({dur:.1f}s / {dur/60:.1f} min)")


def phase5_generate_srt():
    print("\n=== Phase 5: Generate SRT ===")
    stamps = json.loads((MEDIA / "timestamps.json").read_text())
    timing = json.loads((MEDIA / "timing.json").read_text())
    scene_offsets = {}
    cumulative = 0.0
    for s in SCENE_ORDER:
        scene_offsets[s] = cumulative
        p = VIDEO_DIR / f"{s}.mp4"
        if p.exists():
            cumulative += get_duration(p)

    srt_lines = []
    idx = 1
    for scene in SCENE_ORDER:
        if scene not in stamps:
            continue
        ts_list, durs, display = stamps[scene], timing.get(scene, []), SRT_DISPLAY.get(scene, [])
        base = scene_offsets[scene]
        for i in range(min(len(ts_list), len(display), len(durs))):
            start, end = base + ts_list[i], base + ts_list[i] + durs[i] - 0.1
            h1, m1, s1, ms1 = int(start // 3600), int((start % 3600) // 60), int(start % 60), int((start % 1) * 1000)
            h2, m2, s2, ms2 = int(end // 3600), int((end % 3600) // 60), int(end % 60), int((end % 1) * 1000)
            srt_lines.extend([str(idx), f"{h1:02d}:{m1:02d}:{s1:02d},{ms1:03d} --> {h2:02d}:{m2:02d}:{s2:02d},{ms2:03d}", display[i], ""])
            idx += 1
    (FINAL_DIR / "euler_full.srt").write_text("\n".join(srt_lines), encoding="utf-8")
    print(f"  SRT: {idx - 1} entries")


async def main():
    verify_segments()
    await phase1_generate_tts()
    phase2_render_manim()
    silent = phase3_concat_silent()
    phase4_merge_audio(silent)
    phase5_generate_srt()
    print("\n=== Done! ===")
    print(f"  Video:     {FINAL_DIR / 'euler_full.mp4'}")
    print(f"  Subtitles: {FINAL_DIR / 'euler_full.srt'}")


if __name__ == "__main__":
    asyncio.run(main())
