"""
Lattice Cryptography pop-sci video -- build pipeline (v2 optimized).

Pipeline:
  1. Generate TTS per subtitle segment → timing.json
  2. Render Manim scenes (silent) → timestamps.json
  3. Concat silent videos into one full video
  4. ONE-PASS audio merge: place ALL segments at absolute timestamps
  5. Generate SRT subtitles
"""

import asyncio
import json
import os
import re
import subprocess
from pathlib import Path

import edge_tts

os.environ["PYTHONUNBUFFERED"] = "1"

ROOT = Path(__file__).resolve().parent.parent
MEDIA = ROOT / "media"
SEG_DIR = MEDIA / "audio" / "segments"
FINAL_DIR = MEDIA / "final"
VIDEO_DIR = MEDIA / "videos" / "main" / "1080p60"

VOICE = "zh-CN-YunxiNeural"

SCENE_ORDER = [
    "S01_HookScene",
    "S02_TitleScene",
    "S03_LatticeBasicsScene",
    "S04_Lattice3DScene",
    "S05_HardProblemsScene",
    "S06_LWEScene",
    "S07_EncryptionScene",
    "S08_ApplicationsScene",
    "S09_OutroScene",
]

SCENE_SEGMENTS = {
    "S01_HookScene": [
        "想象一下，你的银行账户密码、网购支付信息、甚至国家级别的军事机密，全都在一瞬间被人破解。这并非科幻小说，量子计算机的出现，正在让这一切成为可能。",
        "今天，互联网安全的基石是RSA和椭圆曲线加密。它们的安全性，建立在大数分解和离散对数这两个困难问题之上。但1994年，数学家Peter Shor证明，量子计算机可以在多项式时间内攻破这两个问题。",
        "换句话说，一旦大规模量子计算机问世，现在的加密体系将全线崩溃。那么问题来了：谁来守护后量子时代的数据安全？答案就藏在一个优雅的数学结构里——格。",
    ],
    "S02_TitleScene": [
        "格密码学，后量子时代的安全基石。",
        "今天我们将从最基础的概念出发，一步步理解格密码学为什么能抵抗量子攻击，以及它如何正在重塑整个密码学的版图。",
    ],
    "S03_LatticeBasicsScene": [
        "什么是格？其实非常直观。给定两个基向量b1和b2，格就是它们所有整数线性组合构成的点集。比如1倍b1加0倍b2就是(1,0)这个点。",
        "让我们一步步生成格点。每选一组整数系数，就确定了一个格点的位置。比如1倍b1加1倍b2就是(1,1)。所有整数组合铺满了整个平面，这就是一个完整的二维格。",
        "关键在于，同一个格可以有不同的基。好基近似正交，排列整齐。坏基几乎平行、极度倾斜，但生成的是完全相同的格点集。好基让计算变得容易，坏基则让同样的问题极其困难。",
        "这种好基与坏基之间的不对称性，正是格密码学安全性的根基。如果有人给你一组坏基，想要恢复出好基，在高维空间中几乎不可能。",
    ],
    "S04_Lattice3DScene": [
        "真实的格密码学工作在数百维甚至上千维空间。我们先来看看三维空间中的格是什么样子。这里每个点都是三个基向量的整数线性组合。",
        "旋转视角，你可以看到三维格具有丰富的空间结构。每个格点在三个方向上等间距排列，形成了一个立体的点阵。",
        "三维已经比二维复杂得多。而格密码学工作在256维甚至1024维空间，搜索空间呈指数级增长。在如此高的维度中，找到最短向量或最近向量，连量子计算机也无能为力。",
    ],
    "S05_HardProblemsScene": [
        "格密码学的安全性建立在两个核心困难问题上。第一个叫最短向量问题，简称SVP。给定格的基，从原点出发，想象一个不断膨胀的球体——它最先碰到的格点，就是最短向量。",
        "第二个核心问题叫最近向量问题，简称CVP。给定空间中一个目标点，找到离它最近的格点。这需要逐一排除错误候选，直到找到正确答案。",
        "SVP和CVP在高维空间中都是极其困难的问题。目前没有任何已知算法，包括量子算法，能够在多项式时间内解决它们。这两个问题的计算困难性，为格密码学提供了坚不可摧的数学基础。",
    ],
    "S06_LWEScene": [
        "现在让我们进入格密码学最核心的构造——带错误学习问题，英文简称LWE。它的核心思想是：给你秘密的近似线索，但加了随机噪声，你就无法还原秘密。",
        "让我们用具体数字来理解。假设秘密向量s等于(3,1)。取一个随机向量a1等于(2,5)。计算内积：2乘3等于6，5乘1等于5，所以a1点乘s等于11。",
        "现在加上一个随机小噪声。第一组噪声e1等于加1，所以公开的结果b1等于12。第二组a2等于(4,1)，内积13，加噪声减1，b2等于12。第三组类似，b3等于11。",
        "如果没有噪声，这些方程就是简单的线性方程组。2x加5y等于11，4x加y等于13。用高斯消元法：从第二个方程得到y等于13减4x，代入第一个方程，解出x等于3，y等于1。秘密轻松恢复！",
        "但有了噪声，方程变成了2x加5y等于12，4x加y等于12。同样的方法，解出x约等于2.67，y约等于1.33——完全偏离了真实答案(3,1)！微小的噪声彻底摧毁了精确求解的可能性。这就是LWE问题的威力。",
    ],
    "S07_EncryptionScene": [
        "那么如何用LWE构造加密方案？让我们用具体数字来走一遍。设模数q等于13，Alice的私钥s等于3。她生成多组(a, b)作为公钥，其中b等于a乘s加噪声，对13取模。",
        "Bob要发送消息m等于1。他从公钥中随机选两行，把a值求和得到u等于6，b值求和得到v等于7。然后加上q除以2的整数部分，也就是6，乘以消息1，得到密文c等于13对13取模等于0。",
        "Alice收到密文后解密：c减去u乘以私钥s，等于0减18，对13取模等于8。然后看8更接近0还是更接近6：到0的距离是5，到6的距离只有2。2小于5，所以消息是1，解密成功！",
        "这就是LWE加密的精妙之处：噪声让攻击者完全无法从公钥恢复私钥，但噪声又足够小，使得合法接收者能够通过简单的距离判断正确解密。安全性和正确性之间，存在一个精妙的平衡。",
    ],
    "S08_ApplicationsScene": [
        "格密码学不仅是理论上的突破，它正在改变整个密码学的格局。",
        "2022年，美国国家标准与技术研究院NIST正式选定了首批后量子密码标准。其中，密钥封装方案CRYSTALS-Kyber和数字签名方案CRYSTALS-Dilithium，都基于格密码学。从浏览器到手机，从云服务到政府通信，格密码学正在全面部署。",
        "更令人兴奋的是，格密码学还催生了全同态加密技术。这种技术允许你在完全不解密的情况下对密文进行任意计算。想象一下，云服务器可以处理你的数据，却完全不知道数据内容。这在医疗、金融、隐私计算等领域有着巨大的应用潜力。",
        "格还是构造先进零知识证明的利器，为区块链和数字身份提供后量子安全保障。",
    ],
    "S09_OutroScene": [
        "从一个简单的数学结构——空间中整齐排列的点阵，到守护全人类数字安全的最前沿武器。格密码学告诉我们，真正强大的防御，往往建立在最优雅的数学之上。在量子风暴来临之前，格密码学已经为我们筑起了坚不可摧的城墙。",
    ],
}

SRT_DISPLAY = {
    "S01_HookScene": [
        "量子计算机的出现，正在让加密体系面临前所未有的威胁",
        "RSA和椭圆曲线加密，将被量子计算机在多项式时间内攻破",
        "答案就藏在一个优雅的数学结构里——格",
    ],
    "S02_TitleScene": [
        "格密码学，后量子时代的安全基石",
        "从基础概念到量子抗性，一步步揭开格密码学的面纱",
    ],
    "S03_LatticeBasicsScene": [
        "给定两个基向量，格就是所有整数线性组合的点集",
        "让我们一步步生成格点：每个整数组合对应一个格点",
        "同一个格可以有不同的基：好基整齐，坏基倾斜",
        "这种不对称性，正是格密码学安全性的根基",
    ],
    "S04_Lattice3DScene": [
        "真实的格存在于高维空间，让我们先看看三维的格",
        "旋转视角，感受三维格的空间结构",
        "格密码学工作在数百维，搜索空间呈指数爆炸",
    ],
    "S05_HardProblemsScene": [
        "SVP：找到距离原点最近的非零格点",
        "CVP：给定目标点，找到离它最近的格点",
        "这两个问题连量子计算机也无法高效求解，是格密码学的基石",
    ],
    "S06_LWEScene": [
        "LWE的核心思想：给出秘密的近似线索，但无法还原秘密",
        "假设秘密s=(3,1)，取随机向量，逐步计算内积",
        "每一步加上随机小噪声，得到近似等式",
        "没有噪声？两个方程就能用高斯消元轻松求解",
        "加入噪声后，同样的方法得到完全错误的答案！",
    ],
    "S07_EncryptionScene": [
        "Alice选择私钥s=3，在模13下生成公钥",
        "Bob用公钥加密消息：选取行求和，再加上⌊q/2⌋",
        "Alice解密：c - u*s mod 13，看结果更接近0还是⌊q/2⌋",
        "噪声让攻击者无法破解，又足够小让合法者正确解密",
    ],
    "S08_ApplicationsScene": [
        "格密码学正在改变整个密码学的格局",
        "NIST选定Kyber和Dilithium作为首批后量子密码标准",
        "全同态加密：在不解密的情况下对密文进行任意计算",
        "格还为区块链和数字身份提供后量子安全的零知识证明",
    ],
    "S09_OutroScene": [
        "格密码学：从优雅的数学到守护人类数字安全的最前沿武器",
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
                            print(f"    RETRY {out.name} ({e.__class__.__name__})")
                            await asyncio.sleep(2)
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
    print("\n=== Phase 2: Render Manim (silent) ===", flush=True)
    scenes = " ".join(SCENE_ORDER)
    r = subprocess.run(
        f"cd {ROOT} && uv run manim render -qh --disable_caching animation/main.py {scenes}",
        shell=True, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print(f"  Manim stderr (last 500 chars):\n{r.stderr[-500:]}", flush=True)
    for s in SCENE_ORDER:
        p = VIDEO_DIR / f"{s}.mp4"
        print(f"  {s}: {get_duration(p):.1f}s" if p.exists() else f"  {s}: MISSING!",
              flush=True)


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
