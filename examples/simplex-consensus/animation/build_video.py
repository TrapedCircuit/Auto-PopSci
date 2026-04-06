"""
Simplex Consensus -- build pipeline.
Generates TTS, renders Manim, merges audio+video, produces SRT.
"""

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
    "S01_HookScene",
    "S02_TitleScene",
    "S03_ByzantineScene",
    "S04_ConsensusBasicsScene",
    "S05_PriorWorkScene",
    "S06_SimplexOverviewScene",
    "S07_ProtocolDetailScene",
    "S08_KeyInsightScene",
    "S09_LivenessScene",
    "S10_ApplicationScene",
    "S11_OutroScene",
]

SCENE_SEGMENTS = {
    "S01_HookScene": [  # 3
        "你在手机上转了一笔账。银行的服务器收到了请求——但不是一台服务器，而是几十台。它们必须对这笔交易的结果达成一致。",
        "现在想象一下：如果其中有几台服务器被黑客入侵了呢？它们可能故意发送虚假消息，对不同的伙伴说不同的话，试图搅乱整个系统。",
        "在不可信的网络中，如何让诚实的节点达成一致？这个问题困扰了计算机科学家四十年。",
    ],
    "S02_TitleScene": [  # 3
        "2023 年，康奈尔大学的 Benjamin Chan 和 Rafael Pass 发表了一篇论文。",
        "他们的协议叫做 Simplex——名字本身就是一个宣言：共识可以很简单。",
        "今天我们就来拆解这个算法。我们会先聊一些必要的预备知识，然后一步步看 Simplex 到底是怎么工作的。",
    ],
    "S03_ByzantineScene": [  # 5
        "先来认识一个经典问题。公元前的拜占庭帝国，几位将军围攻一座城池。他们需要统一行动：要么全体进攻，要么全体撤退。",
        "但问题是——其中可能有叛徒。叛徒会对不同的将军发送矛盾的命令，试图让他们行动不一致。",
        "这就是著名的「拜占庭将军问题」。翻译成计算机语言就是：n 个节点中，最多 f 个是恶意的。",
        "数学家证明了一个关键结论：要容忍 f 个拜占庭节点，我们至少需要 n 大于 3f。换句话说，恶意节点必须少于总数的三分之一。",
        "而且做决定时，我们需要至少三分之二的票数——也就是所谓的法定人数，quorum。这样即使恶意节点同时给两边投票，两个矛盾的决定也不可能同时凑齐法定人数。",
    ],
    "S04_ConsensusBasicsScene": [  # 4
        "有了这些基础，我们来看共识协议到底需要保证什么。",
        "第一，一致性。任何两个诚实节点输出的交易日志，要么相同，要么一个是另一个的前缀。绝对不能出现分叉。",
        "第二，活性。在网络状况良好的时候，新的交易必须能在有限时间内被确认。系统不能卡死。",
        "还有一个关键假设：部分同步网络。好的时候，消息在 Δ 秒内送达；坏的时候，完全没保证。我们要求：好的时候能推进，坏的时候至少不能出错。",
    ],
    "S05_PriorWorkScene": [  # 3
        "这些问题并不新鲜。1999 年的 PBFT 协议是开山之作，但它的协议流程极其复杂，光是论文就有几十页。",
        "后来的 Tendermint 更简洁，但有一个效率瓶颈：每轮的 leader 需要先等待 2Δ 时间来收集信息，超时设为 6Δ。一个恶意 leader 可以浪费整整 6Δ 的时间。",
        "Simplex 的目标很明确：更简单的协议、更短的超时、同样的安全性。",
    ],
    "S06_SimplexOverviewScene": [  # 6
        "现在进入正题。Simplex 的结构非常清晰。",
        "协议按「迭代」推进，每一轮有一个随机选出的 leader。",
        "每轮的流程只有三步。第一步，leader 提出一个区块提案，广播给所有人。",
        "第二步，节点验证提案的合法性，如果通过就投票。当收集到至少三分之二的投票，这个区块就被「公证」了——notarized。",
        "第三步，看到公证区块后，节点进入下一轮，并发送 finalize 消息。如果三分之二的节点都发了 finalize，这一轮就被最终确认了。",
        "但如果 leader 是恶意的，迟迟不提案呢？每个节点有一个 3Δ 的计时器。超时后，节点投票给一个「空块」——dummy block，保证协议不会卡死。",
    ],
    "S07_ProtocolDetailScene": [  # 6
        "让我们用一个具体例子来走一遍完整流程。假设有四个节点，其中一个是恶意的。",
        "第一轮，节点 A 被选为 leader。A 打包交易，生成一个新区块，广播给 B、C、D。",
        "B、C、D 收到提案后验证区块的合法性：交易是否有效？父链是否已公证？如果一切合格，它们各自投票。",
        "A 也给自己投票。现在我们有了来自 A、B、C 三个诚实节点的投票——三票！大于等于三分之二乘以四，也就是三票——区块被公证了。",
        "恶意节点 D 可能投了票也可能没投，但这不影响结果。公证达成后，A、B、C 发送 finalize 消息并进入第二轮。",
        "三个 finalize 达到法定人数——第一轮被最终确认。交易正式写入账本。",
    ],
    "S08_KeyInsightScene": [  # 6
        "现在来看 Simplex 最精妙的设计。",
        "还记得超时后节点会投 dummy block 吗？关键观察是：一个诚实节点，要么发 finalize 消息，要么投 dummy block，但绝不会两者都做。",
        "为什么？因为发 finalize 说明节点在超时前就看到了公证区块，已经进入下一轮。而投 dummy block 说明超时了还没看到公证区块。这两件事不可能同时发生。",
        "这意味着什么？三分之二的 finalize 消息和三分之二的 dummy block 投票，不可能同时存在。",
        "这就是 Simplex 安全性的核心。如果一个区块被最终确认了——有三分之二的 finalize——那就不可能有三分之二的 dummy vote。所以没有人能看到一个公证的空块来替代这个已确认的区块。",
        "再加上之前的 quorum intersection——同一高度不可能有两个不同的非空公证区块——Simplex 的一致性就完美地建立了。",
    ],
    "S09_LivenessScene": [  # 4
        "安全性解决了，那活性呢？",
        "如果 leader 是诚实的，协议推进非常快。Leader 提案，节点投票，公证达成——整个过程只需要 2 倍的实际网络延迟 δ。",
        "如果 leader 是恶意的，最坏情况下等 3Δ 超时，投 dummy block，然后进入下一轮。",
        "对比 Tendermint 的 6Δ 超时，Simplex 的恶意 leader 浪费时间减半。这就是去掉 leader 2Δ 等待带来的效率提升。",
    ],
    "S10_ApplicationScene": [  # 3
        "Simplex 不只是一篇论文。它已经走进了生产系统。",
        "Solana 的下一代共识 Alpenglow 采用了 Simplex 的思想。Commonware 库将 Simplex 作为核心共识模块。Ava Labs 也在他们的系统中实现了 Simplex。",
        "从 2023 年的学术论文到多个区块链的生产部署，Simplex 用了不到两年时间。这在共识协议的历史上极为罕见。",
    ],
    "S11_OutroScene": [  # 5
        "让我们回到最开始的问题。",
        "在一个充满不信任的网络中，如何让诚实的节点达成一致？",
        "Simplex 的回答出人意料的简单：每轮一个 leader、一次投票、一个超时。通过 finalize 和 dummy vote 的互斥性，用最少的规则，构建最坚固的安全保证。",
        "Leonardo da Vinci 说过：「简单是终极的复杂。」Simplex 正是这句话在分布式系统中最好的注脚。",
        "这就是 Simplex 共识算法的美。",
    ],
}

SRT_DISPLAY = {
    "S01_HookScene": [
        "你在手机上转了一笔账\n银行的服务器必须对交易结果达成一致",
        "如果有几台服务器被黑客入侵\n故意发送虚假消息呢？",
        "在不可信的网络中 如何让诚实的节点达成一致？",
    ],
    "S02_TitleScene": [
        "2023年 Benjamin Chan 和 Rafael Pass\n发表了一篇论文",
        "Simplex——共识可以很简单",
        "今天我们来拆解这个算法",
    ],
    "S03_ByzantineScene": [
        "拜占庭帝国 几位将军围攻一座城池\n他们需要统一行动",
        "其中可能有叛徒\n发送矛盾的命令",
        "拜占庭将军问题：n个节点中 最多f个是恶意的",
        "要容忍f个拜占庭节点 需要 n > 3f",
        "法定人数 quorum：至少三分之二的票数",
    ],
    "S04_ConsensusBasicsScene": [
        "共识协议需要保证什么？",
        "一致性：诚实节点的日志不分叉",
        "活性：网络正常时 交易必须被确认",
        "部分同步网络：好时候Δ秒送达 坏时候无保证",
    ],
    "S05_PriorWorkScene": [
        "PBFT (1999)：开山之作但极其复杂",
        "Tendermint：leader等待2Δ 超时6Δ",
        "Simplex：更简单 更短超时 同样安全",
    ],
    "S06_SimplexOverviewScene": [
        "Simplex 的结构非常清晰",
        "按「迭代」推进 每轮一个随机 leader",
        "第一步：leader 提出区块提案",
        "第二步：投票 → 公证 (Notarization)",
        "第三步：Finalize → 最终确认",
        "3Δ 超时 → 投 dummy block",
    ],
    "S07_ProtocolDetailScene": [
        "n=4 f=1 的具体例子",
        "A 作为 leader 广播区块给 B C D",
        "B C D 验证并投票",
        "3票 ≥ ⌈2n/3⌉ = 3 区块被公证",
        "A B C 发送 finalize 进入第二轮",
        "第一轮最终确认 交易写入账本",
    ],
    "S08_KeyInsightScene": [
        "Simplex 最精妙的设计",
        "Finalize 与 Dummy Vote 互斥",
        "超时前看到公证→finalize\n超时后→dummy vote",
        "⅔ finalize 和 ⅔ dummy vote 不可能同时存在",
        "被最终确认 → 不存在公证的空块",
        "Quorum intersection → 一致性成立",
    ],
    "S09_LivenessScene": [
        "安全性解决了 那活性呢？",
        "诚实leader：2δ完成",
        "恶意leader：3Δ+δ 超时后投dummy",
        "Simplex 3Δ vs Tendermint 6Δ 减半",
    ],
    "S10_ApplicationScene": [
        "Simplex 已走进生产系统",
        "Solana Alpenglow / Commonware / Ava Labs",
        "从论文到生产部署 不到两年",
    ],
    "S11_OutroScene": [
        "回到最开始的问题",
        "如何在不信任的网络中达成一致？",
        "每轮一个leader 一次投票 一个超时\nfinalize与dummy vote互斥",
        "简单是终极的复杂",
        "这就是 Simplex 共识算法的美",
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
        raise SystemExit("Fix mismatches before building!")
    print()


async def phase1_generate_tts():
    print("=== Phase 1: Generate TTS ===")
    SEG_DIR.mkdir(parents=True, exist_ok=True)
    for scene in SCENE_ORDER:
        for i, text in enumerate(SCENE_SEGMENTS[scene]):
            out = SEG_DIR / f"{scene}_{i:02d}.mp3"
            if not out.exists() or out.stat().st_size < 100:
                for attempt in range(3):
                    try:
                        comm = edge_tts.Communicate(text, VOICE, rate="+12%", pitch="+0Hz")
                        await comm.save(str(out))
                        print(f"    {out.name}")
                        break
                    except Exception as e:
                        if attempt < 2:
                            print(f"    Retry {attempt+1} for {out.name}: {e}")
                            await asyncio.sleep(2 ** attempt)
                        else:
                            raise
    timing = {}
    for scene in SCENE_ORDER:
        durs = [round(get_duration(SEG_DIR / f"{scene}_{i:02d}.mp3"), 3)
                for i in range(len(SCENE_SEGMENTS[scene]))]
        timing[scene] = durs
        print(f"  {scene}: {len(durs)} segs, {sum(durs):.1f}s")
    (MEDIA / "timing.json").write_text(json.dumps(timing, indent=2))
    return timing


def phase2_render_manim():
    print("\n=== Phase 2: Render Manim (silent) ===")
    scenes = " ".join(SCENE_ORDER)
    subprocess.run(
        f"cd {ROOT} && PYTHONUNBUFFERED=1 uv run manim render -qh animation/main.py {scenes}",
        shell=True, text=True, timeout=600)
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
    ], capture_output=True, timeout=120)
    dur = get_duration(silent)
    print(f"  Silent video: {dur:.1f}s")
    return silent, dur


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

    output = FINAL_DIR / "output_full.mp4"
    cmd.extend([
        "-filter_complex", ";".join(filter_parts),
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        str(output),
    ])

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
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
            srt_lines.extend([str(idx), f"{_fmt(start)} --> {_fmt(end)}", display[i], ""])
            idx += 1

    srt_path = FINAL_DIR / "output_full.srt"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
    print(f"  SRT: {srt_path} ({idx - 1} entries)")


def _fmt(s: float) -> str:
    h, m = int(s // 3600), int((s % 3600) // 60)
    sec, ms = int(s % 60), int((s % 1) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


async def main():
    verify_segments()
    await phase1_generate_tts()
    phase2_render_manim()
    silent, _ = phase3_concat_silent()
    phase4_merge_audio(silent)
    phase5_generate_srt()
    print("\n=== Done! ===")


if __name__ == "__main__":
    asyncio.run(main())
