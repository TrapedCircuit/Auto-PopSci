"""
Build pipeline for ZKP animation — timestamp-based audio sync.

Phase 1 — Generate TTS audio per subtitle segment, save durations to timing.json
Phase 2 — Render Manim scenes (silent video + timestamps.json)
Phase 3 — Build per-scene audio from segments placed at exact timestamps
Phase 4 — Merge audio + video per scene, concatenate into final video
Phase 5 — Generate SRT from timestamps
"""

import asyncio
import json
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
    "S01_HookScene", "S02_TitleScene", "S03_CaveIntroScene",
    "S04_CaveProtocolScene", "S05_ProbabilityScene", "S06_CoreInsightScene",
    "S07_PropertiesScene", "S08_MathBridgeScene", "S09_DiscreteLogScene",
    "S10_SchnorrProtocolScene", "S11_VerificationScene", "S12_SimulatorScene",
    "S13_ApplicationScene", "S14_OutroScene",
]

SCENE_SEGMENTS = {
    "S01_HookScene": [
        "想象一下这样的场景。",
        "你站在一扇门前，门后是一个高级私人会所。保安拦住了你，问：密码是什么？你知道密码，但旁边还站着三个陌生人。",
        "你不想让他们听到密码，你甚至不完全信任这个保安会替你保密。",
        "你能不能证明你知道密码，却完全不说出密码本身？",
        "乍一听，这像是一个悖论。证明你知道某样东西，不就意味着要把它展示出来吗？",
        "但数学家告诉我们：不，这完全可以做到。而且这个想法，正在重新定义整个互联网的信任机制。",
    ],
    "S02_TitleScene": [
        "这就是今天的主题，，",
        "零知识证明。",
    ],
    "S03_CaveIntroScene": [
        "让我们从一个经典的思想实验开始。这个实验叫做阿里巴巴的洞穴，是密码学家们最喜欢用来解释零知识证明的类比。",
        "想象一个环形洞穴，只有一个入口。深处有一道需要咒语才能打开的密码门，把通道分成了A路和B路。",
        "现在有两个人登场。Peggy，证明者。Victor，验证者。Peggy愿意证明她知道咒语，但绝不想把咒语告诉Victor。",
    ],
    "S04_CaveProtocolScene": [
        "他们约定了一套协议。",
        "第一步：Victor转过身去不看。Peggy随机选择A路或B路走进洞穴深处。",
        "第二步：Victor转过来，走到洞口，随机喊出一个方向，比如，请从B路出来！",
        "如果Peggy真的知道咒语，她可以念动咒语，穿过密码门，从指定方向走出来。漂亮，验证通过！",
        "但如果Peggy其实根本不知道咒语呢？",
        "她走进了A路，Victor喊从B出来。她打不开门，只能硬着头皮从A路出来。穿帮了！",
        "当然，她也有可能运气好，恰好选了对的路。但这个概率只有，百分之五十。",
    ],
    "S05_ProbabilityScene": [
        "百分之五十的通过率显然不够。但如果我们重复这个过程呢？",
        "重复2次，概率降到25%。5次，3%。10次，千分之一。20次？大约百万分之一。",
        "每多一轮，作弊空间就被压缩一半。这就是零知识证明的精妙之处：通过反复随机挑战，让谎言无处藏身。",
    ],
    "S06_CoreInsightScene": [
        "现在让我们站在Victor的角度想一想。",
        "他不知道Peggy从哪条路进去的，不知道咒语是什么，他甚至无法向第三个人复述这个证明。",
        "但Victor自己心里清楚：连续20轮都蒙对，这不是运气，这是实力。",
    ],
    "S07_PropertiesScene": [
        "密码学家把零知识证明的特性总结为三条。",
        "第一，完备性。如果Peggy确实知道咒语，只要双方诚实执行协议，Victor一定会被说服。",
        "第二，可靠性。如果Peggy在撒谎，她通过所有轮次挑战的概率趋近于零。",
        "第三，零知识性。Victor在整个过程中，除了确信Peggy知道咒语之外，没有获得任何额外信息。",
    ],
    "S08_MathBridgeScene": [
        "洞穴的故事很直观，但你可能会问：这真的能用数学实现吗？现实世界里可没有魔法洞穴。",
        "答案是，完全可以。我们需要一个数学版的密码门：一个正向计算很容易，但反向破解几乎不可能的问题。密码学家管这种问题叫做单向函数。",
    ],
    "S09_DiscreteLogScene": [
        "给你一个大素数p、一个生成元g，正向计算y等于g的x次方 mod p，非常快，计算机瞬间就能完成。",
        "但是反过来，已知g、p和y，要反推出x是多少？以目前人类的计算能力，当p足够大的时候，这基本上是不可能的。",
        "这就是我们的数学版密码门。知道x，就像知道咒语，你能轻松算出y，但别人看到y，猜不出x。",
    ],
    "S10_SchnorrProtocolScene": [
        "1989年，德国密码学家Claus-Peter Schnorr，基于离散对数难题，设计了一个优雅的零知识证明协议。",
        "假设公开信息是g、p和y，其中y等于g的x次方 mod p。Peggy知道秘密x，她要向Victor证明这一点。",
        "第一步，承诺。Peggy选一个随机数r，计算t等于g的r次方 mod p，然后把t发给Victor。这个随机数r就像她在洞穴里随机选路一样，它是一层保护x的面纱。",
        "第二步，挑战。Victor随机选一个数c，发给Peggy。这就像Victor在洞口随机喊方向。",
        "第三步，响应。Peggy计算s等于r加上c乘以x，把s发给Victor。注意，s把x巧妙地藏在了r的随机噪声里。",
        "第四步，验证。Victor检查一个等式：g的s次方，是否等于t乘以y的c次方，mod p。如果等式成立，验证通过。",
        "整个过程中，x从来没有被发送过。Victor只看到了三个数：t、c、s。",
    ],
    "S11_VerificationScene": [
        "为什么这个验证等式一定成立？让我们展开看一看。",
        "g的s次方……",
        "把s代入，就是g的r加cx次方。",
        "根据指数法则，这等于g的r次方乘以g的cx次方。",
        "而g的cx次方可以写成g的x次方的c次方，也就是y的c次方。",
        "所以最终等于t乘以y的c次方。等式两边完美吻合！",
        "等式两边完美吻合。证毕。",
    ],
    "S12_SimulatorScene": [
        "但等一下，等式成立只说明协议是正确的。还没有回答：为什么它是零知识的？",
        "这里有一个精妙的论证。想象存在一个模拟器，它完全不知道秘密x，但它能凭空生成一份和真实交互看起来一模一样的对话记录。",
        "模拟器的做法是：它先随机选c和s，然后反推出t等于g的s次方除以y的c次方。",
        "你把真实记录和模拟记录放在一起比较，数学上可以证明，它们的概率分布完全相同。",
        "如果Victor自己就能伪造出一模一样的对话记录，那这段真实的交互不可能教会他任何新东西。这就是零知识的数学本质。",
    ],
    "S13_ApplicationScene": [
        "零知识证明不只是纸上的数学。它正在深刻地改变现实世界。",
        "在区块链领域，zk-SNARKs和zk-STARKs让你能证明一笔交易合法，而不需要透露金额、发送方或接收方的任何信息。",
        "在身份验证中，你可以证明自己年满18岁，而不需要出示整张身份证。对方只知道你够年龄。",
        "在隐私计算中，多个机构可以联合分析数据、训练模型，而不需要互相暴露任何原始数据。",
    ],
    "S14_OutroScene": [
        "让我们回到最开始那个问题。",
        "你能不能证明你知道密码，却不泄露密码本身？",
        "现在我们知道了：答案是，可以。",
        "零知识证明告诉我们一个深刻的道理：证明一件事，不需要展示这件事本身。",
        "你只需要展示，你能做到，只有知道秘密才能做到的事情。",
    ],
}

SRT_DISPLAY = {
    "S01_HookScene": ["想象一下这样的场景。","保安拦住了你，问：「密码是什么？」\n你知道密码，但旁边还站着三个陌生人。","你不想让他们听到密码，\n你甚至不完全信任这个保安会替你保密。","你能不能证明你知道密码，\n却完全不说出密码本身？","乍一听，这像是一个悖论。","但数学家告诉我们：不，这完全可以做到。"],
    "S02_TitleScene": ["这就是今天的主题——","零知识证明。"],
    "S03_CaveIntroScene": ["让我们从一个经典的思想实验开始：\n「阿里巴巴的洞穴」。","想象一个环形洞穴，深处有一道\n需要咒语才能打开的密码门。","两个人登场：证明者 Peggy 和验证者 Victor。"],
    "S04_CaveProtocolScene": ["他们约定了一套协议。","第一步：Victor 转身不看，\nPeggy 随机走进一条路。","第二步：Victor 随机喊出一个方向。","Peggy 穿过密码门，\n从指定方向走出——验证通过！","如果 Peggy 其实不知道咒语呢？","她打不开门，穿帮了！","运气好能蒙对——但概率只有 50%。"],
    "S05_ProbabilityScene": ["如果我们重复这个过程呢？","重复 10 次，只剩千分之一。\n20 次？大约百万分之一。","每多一轮，作弊空间就被压缩一半。"],
    "S06_CoreInsightScene": ["站在 Victor 的角度想一想。","他不知道 Peggy 走了哪条路，\n不知道咒语，甚至无法复述证明。","但连续 20 轮都蒙对？\n这不是运气，这是实力。"],
    "S07_PropertiesScene": ["零知识证明的三大性质——","完备性：真正知道咒语的人一定能通过验证。","可靠性：撒谎者几乎不可能蒙混过关。","零知识性：验证者除了知道结论，什么也没学到。"],
    "S08_MathBridgeScene": ["这真的能用数学实现吗？","我们需要一个数学版的「密码门」\n——单向函数。"],
    "S09_DiscreteLogScene": ["正向计算 y = g^x mod p，非常快。","反过来求 x？基本不可能。","这就是我们的数学版密码门。"],
    "S10_SchnorrProtocolScene": ["1989 年，Schnorr 设计了\n一个优雅的零知识证明协议。","公开信息：g, p, y = g^x mod p。","第一步，承诺：Peggy 发送 t = g^r mod p。","第二步，挑战：Victor 发送随机数 c。","第三步，响应：Peggy 发送 s = r + c·x。","第四步，验证：检查 g^s ≡ t·y^c (mod p)。","秘密 x 从未被发送过。"],
    "S11_VerificationScene": ["为什么验证等式成立？","g^s","= g^(r+cx)","= g^r · g^(cx)","= g^r · (g^x)^c","= t · y^c    等式完美吻合！","证毕。"],
    "S12_SimulatorScene": ["为什么它是「零知识」的？","存在一个模拟器，不知道 x，\n却能生成一模一样的对话记录。","模拟器先选 c 和 s，再反推 t。","真实记录与模拟记录——\n概率分布完全相同。","Victor 自己就能伪造同样的记录，\n所以真实交互不可能教会他新东西。"],
    "S13_ApplicationScene": ["零知识证明正在改变现实世界。","区块链：zk-SNARKs 让交易验证\n无需暴露任何隐私。","身份认证：证明年龄而不出示整张证件。","隐私计算：联合分析数据而不暴露原始信息。"],
    "S14_OutroScene": ["回到最开始那个问题——","你能不能证明你知道密码，\n却不泄露密码本身？","答案是：可以。","证明一件事，不需要展示这件事本身。","你只需要展示，你能做到\n只有知道秘密才能做到的事。"],
}


def get_duration(path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "json", str(path)], capture_output=True, text=True)
    try:
        return float(json.loads(r.stdout)["format"]["duration"])
    except (KeyError, json.JSONDecodeError):
        return 2.0


async def phase1_generate_tts():
    """Generate TTS per segment, save durations to timing.json."""
    print("=== Phase 1: Generate TTS per segment ===")
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
        durs = []
        for i in range(len(SCENE_SEGMENTS[scene])):
            f = SEG_DIR / f"{scene}_{i:02d}.mp3"
            durs.append(round(get_duration(f), 3))
        timing[scene] = durs
        print(f"  {scene}: {len(durs)} segs, {sum(durs):.1f}s")

    timing_path = MEDIA / "timing.json"
    timing_path.write_text(json.dumps(timing, indent=2))
    return timing


def phase2_render_manim():
    """Render all scenes (silent video). They write timestamps.json."""
    print("\n=== Phase 2: Render Manim scenes (silent) ===")
    scenes = " ".join(SCENE_ORDER)
    subprocess.run(
        f"cd {ROOT} && uv run manim render -qh zkp_animation/main.py {scenes}",
        shell=True, capture_output=True)
    for s in SCENE_ORDER:
        p = VIDEO_DIR / f"{s}.mp4"
        d = get_duration(p) if p.exists() else 0
        print(f"  {s}: {d:.1f}s")


def phase3_build_audio():
    """Build per-scene audio by placing TTS segments at logged timestamps."""
    print("\n=== Phase 3: Build audio tracks from timestamps ===")
    stamps_path = MEDIA / "timestamps.json"
    if not stamps_path.exists():
        print("  ERROR: timestamps.json missing. Scenes must be rendered first.")
        return
    stamps = json.loads(stamps_path.read_text())
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    for scene in SCENE_ORDER:
        if scene not in stamps:
            print(f"  SKIP {scene}: no timestamps")
            continue
        ts_list = stamps[scene]
        n_segs = len(SCENE_SEGMENTS[scene])
        vid_path = VIDEO_DIR / f"{scene}.mp4"
        vid_dur = get_duration(vid_path) if vid_path.exists() else 60

        # Build ffmpeg filter to overlay each segment at its timestamp
        inputs = []
        filter_parts = []
        # Silent base track matching video duration
        inputs.extend(["-f", "lavfi", "-t", str(vid_dur), "-i", "anullsrc=r=44100:cl=mono"])
        for i in range(min(n_segs, len(ts_list))):
            seg_file = SEG_DIR / f"{scene}_{i:02d}.mp3"
            if not seg_file.exists():
                continue
            inputs.extend(["-i", str(seg_file)])

        # Amerge each segment onto the silent base at its timestamp
        n_actual = min(n_segs, len(ts_list))
        if n_actual == 0:
            continue

        # Use adelay to position each segment, then amix all
        mix_inputs = ["[0]"]
        for i in range(n_actual):
            delay_ms = int(ts_list[i] * 1000)
            filter_parts.append(f"[{i+1}]adelay={delay_ms}|{delay_ms}[d{i}]")
            mix_inputs.append(f"[d{i}]")

        filter_parts.append(f"{''.join(mix_inputs)}amix=inputs={n_actual + 1}:duration=longest:dropout_transition=0[out]")
        filter_str = ";".join(filter_parts)

        out_path = FINAL_DIR / f"{scene}.mp4"
        cmd = ["ffmpeg", "-y"] + inputs + [
            "-filter_complex", filter_str,
            "-map", "0:v" if vid_path.exists() else "",
            "-map", "[out]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(vid_dur),
            str(out_path),
        ]
        # Use video from rendered scene + generated audio
        cmd = [
            "ffmpeg", "-y",
            "-i", str(vid_path),
        ]
        for i in range(n_actual):
            cmd.extend(["-i", str(SEG_DIR / f"{scene}_{i:02d}.mp3")])

        filter_parts_v2 = []
        for i in range(n_actual):
            delay_ms = int(ts_list[i] * 1000)
            filter_parts_v2.append(f"[{i+1}:a]adelay={delay_ms}|{delay_ms}[d{i}]")

        mix_labels = "".join(f"[d{i}]" for i in range(n_actual))
        filter_parts_v2.append(f"{mix_labels}amix=inputs={n_actual}:duration=longest:dropout_transition=0,volume={n_actual}[aout]")

        cmd.extend([
            "-filter_complex", ";".join(filter_parts_v2),
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-t", str(vid_dur),
            str(out_path),
        ])

        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ERROR {scene}: {r.stderr[-200:]}")
        else:
            print(f"  {scene}: {n_actual} segments placed at {[f'{t:.1f}s' for t in ts_list[:n_actual]]}")


def phase4_concatenate():
    """Concatenate scene videos into final."""
    print("\n=== Phase 4: Concatenate ===")
    concat = FINAL_DIR / "concat.txt"
    lines = []
    for s in SCENE_ORDER:
        p = FINAL_DIR / f"{s}.mp4"
        if p.exists():
            lines.append(f"file '{p}'")
    concat.write_text("\n".join(lines))

    output = FINAL_DIR / "zkp_full.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat),
        "-c", "copy",
        str(output),
    ], capture_output=True)
    dur = get_duration(output)
    print(f"  Final: {output} ({dur:.1f}s / {dur/60:.1f} min)")


def phase5_generate_srt():
    """Generate SRT from timestamps."""
    print("\n=== Phase 5: Generate SRT ===")
    stamps = json.loads((MEDIA / "timestamps.json").read_text())
    timing = json.loads((MEDIA / "timing.json").read_text())

    srt_lines = []
    idx = 1
    scene_offsets = {}
    cumulative = 0.0

    # Calculate scene start offsets
    for s in SCENE_ORDER:
        scene_offsets[s] = cumulative
        p = FINAL_DIR / f"{s}.mp4"
        if p.exists():
            cumulative += get_duration(p)

    for scene in SCENE_ORDER:
        if scene not in stamps:
            continue
        ts_list = stamps[scene]
        durs = timing.get(scene, [])
        display = SRT_DISPLAY.get(scene, [])
        base = scene_offsets.get(scene, 0)

        for i in range(min(len(ts_list), len(display), len(durs))):
            start = base + ts_list[i]
            end = start + durs[i] - 0.1
            srt_lines.extend([str(idx), f"{_fmt(start)} --> {_fmt(end)}", display[i], ""])
            idx += 1

    srt_path = FINAL_DIR / "zkp_full.srt"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
    print(f"  SRT: {srt_path} ({idx - 1} entries)")


def _fmt(s: float) -> str:
    h, m = int(s // 3600), int((s % 3600) // 60)
    sec, ms = int(s % 60), int((s % 1) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


async def main():
    timing = await phase1_generate_tts()
    phase2_render_manim()
    phase3_build_audio()
    phase4_concatenate()
    phase5_generate_srt()
    print("\n=== Done! ===")
    print(f"  Video:     {FINAL_DIR / 'zkp_full.mp4'}")
    print(f"  Subtitles: {FINAL_DIR / 'zkp_full.srt'}")


if __name__ == "__main__":
    asyncio.run(main())
