"""
Build pipeline for ZK-STARKs animation — one-pass audio merge.

Phase 1 — Generate TTS per subtitle segment → timing.json
Phase 2 — Render Manim scenes (silent) → timestamps.json
Phase 3 — Concat silent videos into one full video (video-only)
Phase 4 — ONE-PASS audio merge: place ALL segments at absolute timestamps
Phase 5 — Generate SRT subtitles
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
    "S03_PrereqPolyScene",
    "S04_PrereqFieldScene",
    "S05_CoreIdeaScene",
    "S06_ArithmetizationScene",
    "S07_PolynomialTestScene",
    "S08_FRIIntroScene",
    "S09_FRIStepsScene",
    "S10_WhyTransparentScene",
    "S11_FullPipelineScene",
    "S12_ApplicationScene",
    "S13_OutroScene",
]

SCENE_SEGMENTS = {
    "S01_HookScene": [
        "假设你是一个国家的审计官。",
        "一台超级计算机刚刚处理了100亿笔金融交易，声称所有交易全部合规。你信吗？",
        "要你自己重新验算一遍？那可能需要几个月。但如果我告诉你，有一种数学方法，能让你在几毫秒内就确认这台超级计算机没有撒谎呢？",
        "而且，这个验证过程不需要信任任何人，不需要任何秘密仪式，完全公开透明。",
    ],
    "S02_TitleScene": [
        "这就是今天的主角，，",
        "ZK-STARKs。",
    ],
    "S03_PrereqPolyScene": [
        "在深入STARKs之前，我们需要先认识两个关键工具。第一个是多项式。",
        "你一定见过这样的函数：f(x)等于2x的平方加3x加1。这是一个二次多项式。",
        "多项式有一个非常强大的性质。如果两个不同的d次多项式，它们最多只能在d个点上相交。",
        "来看个例子。f(x)等于2x平方加3x加1，g(x)等于x平方加5x加1。它们都是二次的，所以最多只有2个交点。",
        "换句话说，如果我在一个很大的范围里随机选一个点去检查，两个不同多项式恰好在这个点上相等的概率极低。",
        "这意味着什么？多项式就像指纹，几乎不可能伪造。",
    ],
    "S04_PrereqFieldScene": [
        "第二个关键工具是有限域。",
        "你一定知道取模运算。比如在模7的世界里，3加5等于1，因为8 mod 7等于1。",
        "在这个世界里，数字只有0到6，做加减乘除全部绕着圈来。这就是一个有限域。",
        "为什么要用有限域？因为计算机处理实数会有精度误差，但模运算是精确的。每一步计算都可以被完美复现。",
        "当我们把多项式放在有限域上，就得到了STARKs的数学语言。接下来，你会看到它的威力。",
    ],
    "S05_CoreIdeaScene": [
        "现在来看STARKs最核心的思想。",
        "一句话概括：证明一个计算是正确的，等价于证明你知道一个满足特定约束的多项式。",
        "具体来说，任何计算过程都可以被记录为一张执行轨迹表。每一行是一步的状态。",
        "我们把这张表编码成一个多项式。如果这个多项式满足所有约束条件，就说明原始计算是正确的。",
        "而验证者只需要在几个随机点上检查这个多项式，就能以极高的概率确认它是否正确。",
    ],
    "S06_ArithmetizationScene": [
        "让我们用一个具体的例子来理解。假设要证明一个类似斐波那契的计算。",
        "规则是：a₀等于1，a₁等于1，之后每个数等于前两个数之和。",
        "我们要证明自己正确地算到了第1000步。",
        "先来看具体数字。第一个约束：起始值必须是1。",
        "第二个约束：每一步都满足递推关系。比如a₂等于a₁加a₀，也就是2等于1加1。a₃等于a₂加a₁，3等于2加1。",
        "现在把这些值编码到一个多项式P上。P经过点(0,1)，(1,1)，(2,2)，(3,3)，以此类推。",
        "约束条件变成了多项式等式：P在x乘ω²处的值，等于P在x乘ω处加上P在x处的值。",
        "如果P在整个特殊域上都满足这个等式，那原始计算就是正确的。",
    ],
    "S07_PolynomialTestScene": [
        "但验证者不会逐点检查，那就跟重新计算一样慢了。",
        "相反，验证者随机挑几个点抽查。",
        "还记得多项式的指纹性质吗？如果证明者作弊，他提交的不是正确的多项式，那么在随机点上暴露的概率极高。",
        "每多检查一个点，作弊成功的概率就指数级下降。这和零知识证明中反复挑战的逻辑一模一样。",
    ],
    "S08_FRIIntroScene": [
        "但还有一个关键问题：验证者怎么确认证明者提交的东西真的是一个低次多项式，而不是随便编的数据？",
        "这就是FRI协议要解决的问题。FRI，全称是Fast Reed-Solomon Interactive Oracle Proof of Proximity。",
        "FRI的核心思想，用一句话说：把多项式反复对折，每折一次度数减半，直到折成一个常数。",
        "就像你把一张写满数字的纸条反复对折。每折一次，长度减半。折了log n次之后，纸条只剩一个点，这一个点你可以直接验证。",
    ],
    "S09_FRIStepsScene": [
        "让我们看看FRI的具体步骤。假设证明者有一个d次多项式f(x)，他在一个大小为N的域上提交了所有N个点的值。",
        "第一轮折叠：验证者发送一个随机数α。",
        "证明者计算新多项式f₁(x)，方法是把f的偶数项和奇数项用α线性组合。新多项式的度数变成了d除以2。",
        "第二轮：验证者再发一个随机数β。证明者再折一次，度数变成d除以4。",
        "就这样反复折叠。每一轮，度数减半，域也缩小一半。",
        "经过log(N)轮之后，多项式变成了一个常数。常数的验证是平凡的，直接比对就行。",
        "最后，验证者还会随机抽查几个折叠步骤的一致性。如果都通过，证明有效！",
    ],
    "S10_WhyTransparentScene": [
        "现在你可能会问：这和SNARKs有什么区别？",
        "最关键的区别是：SNARKs需要一个可信设置。在初始化时，需要生成一些秘密参数，然后销毁。如果有人偷偷保留了这些参数，整个系统的安全性就崩溃了。",
        "而STARKs完全不需要可信设置。它只依赖哈希函数。所有参数都是公开透明的，没有任何秘密。",
        "还有一个重要优势：STARKs是抗量子的。因为它基于哈希函数，而不是椭圆曲线。即使未来量子计算机出现，STARKs依然安全。",
    ],
    "S11_FullPipelineScene": [
        "让我们把整条流水线串起来。",
        "首先，你有一个计算任务。把它的执行轨迹记录下来。",
        "然后，通过算术化，把轨迹编码成多项式和约束。",
        "接着，用FRI协议证明这个多项式是低次的。",
        "最终生成一个简短的证明。证明者可能花了几分钟生成证明，但验证者只需要几毫秒就能验证。",
        "而且证明的大小是对数级的，计算量翻10倍，证明只长了一点点。",
    ],
    "S12_ApplicationScene": [
        "ZK-STARKs已经在改变真实世界了。",
        "在以太坊生态中，StarkNet用STARKs把数千笔交易压缩成一个证明，提交到主链。这让以太坊的吞吐量提升了几百倍，而安全性丝毫不减。",
        "Starkware开发了一门叫Cairo的编程语言。用Cairo写的程序，每一步执行都自动生成STARK证明。",
        "更远的未来，可验证计算可以应用到AI推理、科学模拟、甚至选举计票。任何需要信任的计算都可以被证明。",
    ],
    "S13_OutroScene": [
        "让我们回到开头那个场景。",
        "超级计算机说它检查了100亿笔交易。现在你不需要盲目信任它。",
        "它只需要附上一个STARK证明。你在几毫秒内就能验证这个证明，如果验证通过，数学保证了计算一定是正确的。",
        "不需要信任任何人，不需要任何秘密。",
        "ZK-STARKs让我们第一次拥有了这样的能力：用数学取代信任，用证明取代权威。",
    ],
}

SRT_DISPLAY = {
    "S01_HookScene": [
        "假设你是一个国家的审计官。",
        "一台超级计算机刚刚处理了 100 亿笔金融交易，\n声称所有交易全部合规。你信吗？",
        "要你自己重新验算？可能需要几个月。\n但有一种方法，几毫秒内就能确认。",
        "这个验证过程不需要信任任何人，\n完全公开透明。",
    ],
    "S02_TitleScene": [
        "这就是今天的主角——",
        "ZK-STARKs",
    ],
    "S03_PrereqPolyScene": [
        "预备知识一：多项式",
        "f(x) = 2x² + 3x + 1，\n一个二次多项式。",
        "不同的 d 次多项式\n最多只能在 d 个点上相交。",
        "f(x) = 2x²+3x+1 vs g(x) = x²+5x+1\n最多 2 个交点。",
        "随机选点检查，\n两个不同多项式匹配的概率极低。",
        "多项式就像指纹——几乎不可能伪造。",
    ],
    "S04_PrereqFieldScene": [
        "预备知识二：有限域",
        "在模 7 的世界里，\n3 + 5 = 1（因为 8 mod 7 = 1）",
        "数字只有 0 到 6，\n加减乘除全部绕着圈来。",
        "计算机处理实数有精度误差，\n但模运算是精确的。",
        "多项式 + 有限域 → STARKs 的数学语言",
    ],
    "S05_CoreIdeaScene": [
        "STARKs 的核心思想",
        "正确的计算 ↔ 满足约束的多项式",
        "任何计算过程都可以被记录为\n一张「执行轨迹」表。",
        "把执行轨迹编码成多项式，\n满足约束 = 计算正确。",
        "验证者只需在几个随机点上检查，\n就能以极高概率确认正确性。",
    ],
    "S06_ArithmetizationScene": [
        "用斐波那契数列来理解算术化。",
        "a₀=1, a₁=1, aᵢ = aᵢ₋₁ + aᵢ₋₂",
        "要证明正确算到了第 1000 步。",
        "第一个约束：起始值必须是 1。",
        "a₂ = a₁ + a₀ = 2\na₃ = a₂ + a₁ = 3",
        "把值编码到多项式 P 上：\nP(0)=1, P(1)=1, P(2)=2, P(3)=3, ...",
        "P(ω²x) = P(ωx) + P(x)",
        "P 在特殊域上满足等式\n→ 原始计算正确 ✓",
    ],
    "S07_PolynomialTestScene": [
        "逐点检查太慢了。",
        "验证者随机挑几个点抽查。",
        "作弊的多项式在随机点上\n暴露的概率极高。",
        "每多检查一个点，\n作弊概率指数级下降。",
    ],
    "S08_FRIIntroScene": [
        "怎么确认提交的是低次多项式？",
        "FRI 协议：\nFast Reed-Solomon IOP of Proximity",
        "把多项式反复对折，\n每折一次度数减半，直到变常数。",
        "像折纸条一样，\nlog n 次后只剩一个点可直接验证。",
    ],
    "S09_FRIStepsScene": [
        "证明者在大小为 N 的域上\n提交所有点的值。",
        "第一轮：验证者发送随机数 α。",
        "偶数项 + 奇数项线性组合\n→ 度数减半。",
        "第二轮：再折一次，度数变为 d/4。",
        "反复折叠，每轮度数减半。",
        "log(N) 轮后变成常数，\n直接比对即可。",
        "随机抽查折叠一致性\n→ 证明有效 ✓",
    ],
    "S10_WhyTransparentScene": [
        "SNARKs vs STARKs",
        "SNARKs 需要可信设置\n→ 有毒废料问题",
        "STARKs 只依赖哈希函数\n→ 完全透明，无秘密",
        "STARKs 基于哈希函数\n→ 抗量子计算",
    ],
    "S11_FullPipelineScene": [
        "STARK 全流程",
        "计算 → 执行轨迹",
        "轨迹 → 多项式约束",
        "多项式 → FRI 证明",
        "证明者 ~ 分钟\n验证者 ~ 毫秒 ⚡",
        "证明大小 = O(log² n)\n对数级增长",
    ],
    "S12_ApplicationScene": [
        "ZK-STARKs 正在改变真实世界。",
        "StarkNet：以太坊 L2\n数千笔交易压缩成一个证明",
        "Cairo：每步执行\n自动生成 STARK 证明",
        "AI 推理 · 科学模拟 · 选举计票\n任何计算都可被证明",
    ],
    "S13_OutroScene": [
        "回到开头那个场景——",
        "超级计算机检查了 100 亿笔交易\n现在你不需要盲目信任它。",
        "附上 STARK 证明，几毫秒验证\n数学保证计算正确。",
        "不需要信任任何人，不需要任何秘密。",
        "用数学取代信任，用证明取代权威。",
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
                        comm = edge_tts.Communicate(text, VOICE, rate="+10%", pitch="+0Hz")
                        await comm.save(str(out))
                        print(f"    {out.name}")
                        break
                    except Exception as e:
                        if attempt < 2:
                            print(f"    RETRY {out.name}: {e}")
                            await asyncio.sleep(2 ** attempt)
                        else:
                            print(f"    FAILED {out.name}: {e}")
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
    r = subprocess.run(
        f"cd {ROOT} && PYTHONUNBUFFERED=1 uv run manim render -qh animation/main.py {scenes}",
        shell=True, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print(f"  RENDER ERROR:\n{r.stderr[-1000:]}")
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
    ], capture_output=True, text=True, timeout=120)
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
        f":dropout_transition=0:normalize=0[aout]"
    )

    output = FINAL_DIR / "zkstark_full.mp4"
    cmd.extend([
        "-filter_complex", ";".join(filter_parts),
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        str(output),
    ])

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
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

    srt_path = FINAL_DIR / "zkstark_full.srt"
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
