"""Transformer -- build pipeline (one-pass audio merge)."""

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
    "S01_HookScene", "S02_OverviewScene", "S03_EmbeddingScene",
    "S04_SelfAttentionScene", "S05_MultiHeadScene",
    "S06_TransformerBlockScene", "S07_ApplicationScene", "S08_OutroScene",
]

SCENE_SEGMENTS = {
    "S01_HookScene": [
        "你有没有想过，ChatGPT是怎么理解你的问题，并给出流畅回答的？这一切的秘密，来自2017年的一篇论文。",
        "这篇论文的标题只有五个英文单词：Attention Is All You Need。注意力，就是你所需要的一切。它提出了一个全新的模型架构。",
        "这个架构的名字叫做Transformer。今天，我们就来揭开它的神秘面纱。",
    ],
    "S02_OverviewScene": [
        "Transformer最初是为机器翻译设计的。它的核心结构分为两部分：左边是编码器，负责理解输入的句子；右边是解码器，负责一个词一个词地生成翻译结果。",
        "但它最革命性的创新，不在于这个结构本身，而是一种叫做自注意力的机制。让我们一步步来理解它。",
    ],
    "S03_EmbeddingScene": [
        "在进入注意力之前，我们先要把文字变成计算机能处理的数字。每个词会被映射成一个高维向量，这个过程叫词嵌入。语义相近的词，在向量空间中距离更近。",
        "但仅有词嵌入还不够。句子中词的顺序至关重要。我吃鱼和鱼吃我，意思完全不同。所以Transformer用位置编码，把每个词在句子中的位置信息，加入到向量里。",
    ],
    "S04_SelfAttentionScene": [
        "现在来到Transformer的核心：自注意力机制。它要解决的问题是，一个词的含义，往往取决于它周围的词。比如苹果这个词，在不同语境中含义完全不同。",
        "自注意力是这样工作的：每个词的向量经过三次线性变换，得到三个新向量。查询向量Q代表这个词在问什么，键向量K代表这个词能提供什么信息，值向量V代表这个词的实际内容。",
        "然后，用Q和K做点积运算，除以一个缩放因子，经过softmax得到注意力权重。最后用权重对V加权求和。这样，每个词的新表示就融合了整个句子的上下文信息。",
    ],
    "S05_MultiHeadScene": [
        "但只用一组注意力可能不够全面。一个词和其他词之间的关系是多维度的：有语法关系、有语义关系、有指代关系。",
        "所以Transformer使用了多头注意力。它同时运行多组独立的注意力计算，每一组叫做一个头，关注不同维度的关系。最后把所有头的结果拼接在一起，通过线性变换融合。",
    ],
    "S06_TransformerBlockScene": [
        "注意力只是Transformer块的一半。注意力的输出还要通过一个前馈神经网络，对每个位置的表示做进一步的非线性变换。",
        "此外，每个子层都有残差连接和层归一化。残差连接让梯度更容易传播，层归一化让训练更加稳定。把多个这样的块堆叠起来，模型就能学习越来越抽象的特征。",
    ],
    "S07_ApplicationScene": [
        "Transformer的影响远远超出了机器翻译。GPT只用了解码器，却成为了最强大的文本生成模型。BERT只用了编码器，却革新了自然语言理解。",
        "更令人惊叹的是，Vision Transformer证明了注意力机制不只适用于文字，也能处理图像。如今，Transformer已经成为深度学习的通用架构。",
    ],
    "S08_OutroScene": [
        "从一篇论文到改变整个人工智能领域，Transformer用一个简洁而优雅的思想，重新定义了机器理解世界的方式。",
        "注意力，就是你所需要的一切。",
    ],
}

SRT_DISPLAY = {
    "S01_HookScene": [
        "ChatGPT的秘密来自2017年的一篇论文",
        "Attention Is All You Need",
        "这个架构叫做 Transformer",
    ],
    "S02_OverviewScene": [
        "编码器理解输入，解码器生成输出",
        "核心创新：自注意力机制",
    ],
    "S03_EmbeddingScene": [
        "词嵌入：每个词映射为高维向量",
        "位置编码：加入词序信息",
    ],
    "S04_SelfAttentionScene": [
        "一个词的含义取决于上下文",
        "Q(查询)、K(键)、V(值) 三路变换",
        "注意力权重 → 加权求和 → 上下文向量",
    ],
    "S05_MultiHeadScene": [
        "单头注意力只能关注一种关系",
        "多头注意力：多组并行，拼接融合",
    ],
    "S06_TransformerBlockScene": [
        "注意力 + FFN + 残差 + 层归一化",
        "堆叠多个块，学习更抽象的特征",
    ],
    "S07_ApplicationScene": [
        "GPT(解码器) · BERT(编码器)",
        "Transformer：深度学习的通用架构",
    ],
    "S08_OutroScene": [
        "从一篇论文到改变AI领域",
        "Attention Is All You Need",
    ],
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

    output = FINAL_DIR / "transformer_full.mp4"
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
        ts_list = stamps[scene]
        durs = timing.get(scene, [])
        display = SRT_DISPLAY.get(scene, [])
        base = scene_offsets[scene]
        for i in range(min(len(ts_list), len(display), len(durs))):
            start = base + ts_list[i]
            end = start + durs[i] - 0.1
            srt_lines.extend([
                str(idx),
                f"{_fmt(start)} --> {_fmt(end)}",
                display[i],
                "",
            ])
            idx += 1

    (FINAL_DIR / "transformer_full.srt").write_text(
        "\n".join(srt_lines), encoding="utf-8",
    )
    print(f"  SRT: {idx - 1} entries")


def _fmt(s: float) -> str:
    h, m = int(s // 3600), int((s % 3600) // 60)
    sec, ms = int(s % 60), int((s % 1) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


async def main():
    verify_segments()
    await phase1_generate_tts()
    phase2_render_manim()
    silent = phase3_concat_silent()
    phase4_merge_audio(silent)
    phase5_generate_srt()
    print("\n=== Done! ===")
    print(f"  Video:     {FINAL_DIR / 'transformer_full.mp4'}")
    print(f"  Subtitles: {FINAL_DIR / 'transformer_full.srt'}")


if __name__ == "__main__":
    asyncio.run(main())
