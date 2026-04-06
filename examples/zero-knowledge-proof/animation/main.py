"""
Zero-Knowledge Proof — 10-minute science-popularization Manim animation.
Narration-first design: each scene carries subtitle text matching script.md.
Audio sync via timestamp logging + ffmpeg post-merge.
"""

from manim import *
import numpy as np
from base import (
    SubtitleMixin, BG, PROVER_CLR, VERIFIER_CLR,
    OK_CLR, FAIL_CLR, ACCENT, MUTED, CARD_BG, FONT,
)


# ═════════════════════════════════════════════════════════════════════════════
# Part 1 · 起 — Hook & Title
# ═════════════════════════════════════════════════════════════════════════════

class S01_HookScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        # ── Scenario setup
        self.show_sub("想象一下这样的场景。")

        door = RoundedRectangle(
            width=2.4, height=3.6, corner_radius=0.15,
            fill_color="#2c3e50", fill_opacity=0.9,
            stroke_color=MUTED, stroke_width=3,
        ).shift(LEFT * 0.3)
        handle = Dot(radius=0.1, color=ACCENT).move_to(door.get_right() + LEFT * 0.35)
        guard = VGroup(
            Circle(radius=0.3, color=MUTED, stroke_width=3),
            Line(DOWN * 0.3, DOWN * 1.0, color=MUTED, stroke_width=3),
            Line(DOWN * 0.6 + LEFT * 0.4, DOWN * 0.6 + RIGHT * 0.4, color=MUTED, stroke_width=3),
        ).shift(RIGHT * 1.8 + DOWN * 0.2)

        self.play(FadeIn(door, handle, shift=DOWN * 0.3), run_time=0.8)
        self.play(FadeIn(guard, shift=RIGHT * 0.3), run_time=0.6)

        self.show_sub("保安拦住了你，问：「密码是什么？」\n你知道密码，但旁边还站着三个陌生人。")
        bubble = RoundedRectangle(
            width=2.2, height=0.6, corner_radius=0.12,
            fill_color=VERIFIER_CLR, fill_opacity=0.15,
            stroke_color=VERIFIER_CLR, stroke_width=2,
        ).next_to(guard, UP, buff=0.2)
        btxt = Text("密码是什么？", font=FONT, font_size=18, color=VERIFIER_CLR).move_to(bubble)
        self.play(FadeIn(bubble, btxt), run_time=0.6)

        # Bystanders
        bystanders = VGroup()
        for i, x in enumerate([3.8, 4.6, 5.4]):
            head = Circle(radius=0.18, color=FAIL_CLR, stroke_width=2).shift(RIGHT * x + UP * 0.2)
            q = Text("?", font_size=22, color=FAIL_CLR).move_to(head)
            bystanders.add(VGroup(head, q))
        self.play(FadeIn(bystanders, lag_ratio=0.3), run_time=1)
        self.wait(2)

        self.show_sub("你不想让他们听到密码，你甚至不完全信任这个保安会替你保密。")

        # Core question
        self.play(FadeOut(door, handle, guard, bubble, btxt, bystanders), run_time=0.6)
        core_q = Text(
            "能不能证明你知道密码\n却完全不说出密码本身？",
            font=FONT, font_size=38, color=WHITE, line_spacing=1.6,
        )
        self.show_sub("你能不能证明你知道密码，却完全不说出密码本身？")
        self.play(Write(core_q), run_time=2)

        # Paradox
        self.show_sub("乍一听，这像是一个悖论。证明你知道某样东西，不就意味着要把它展示出来吗？")
        paradox = Text("悖论？", font=FONT, font_size=52, color=ACCENT)
        qmark = Text("?", font_size=72, color=ACCENT).next_to(paradox, RIGHT, buff=0.2)
        pg = VGroup(paradox, qmark).center()
        self.play(ReplacementTransform(core_q, pg), run_time=1)

        # Resolution
        self.show_sub("但数学家告诉我们：不，这完全可以做到。\n而且这个想法，正在重新定义整个互联网的信任机制。")
        bang = Text("!", font_size=80, color=OK_CLR)
        self.play(ReplacementTransform(pg, bang), Flash(bang, color=ACCENT), run_time=1)

        self.clear_all()


class S02_TitleScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("这就是今天的主题——")

        lock_body = RoundedRectangle(
            width=1.2, height=1.0, corner_radius=0.15,
            fill_color=ACCENT, fill_opacity=0.9, stroke_color=WHITE, stroke_width=2,
        ).shift(DOWN * 0.2)
        lock_shackle = Arc(
            radius=0.45, start_angle=0, angle=PI,
            stroke_color=ACCENT, stroke_width=6,
        ).shift(UP * 0.5)
        keyhole = Circle(radius=0.12, fill_color=BG, fill_opacity=1, stroke_width=0).shift(DOWN * 0.05)
        keyhole_slit = Rectangle(width=0.08, height=0.22, fill_color=BG, fill_opacity=1, stroke_width=0).shift(DOWN * 0.2)
        lock = VGroup(lock_shackle, lock_body, keyhole, keyhole_slit).scale(0.8)

        self.play(FadeIn(lock, scale=0.5), run_time=0.8)
        self.play(lock.animate.scale(0.55).to_edge(UP, buff=0.8), run_time=0.8)

        title_cn = Text("零知识证明", font=FONT, font_size=58, color=WHITE)
        title_en = Text("Zero-Knowledge Proof", font_size=34, color=ACCENT)
        titles = VGroup(title_cn, title_en).arrange(DOWN, buff=0.35)
        titles.next_to(lock, DOWN, buff=0.6)

        self.show_sub("零知识证明。", wait=0)
        self.play(Write(title_cn), run_time=1.5)
        self.play(FadeIn(title_en, shift=UP * 0.3), run_time=0.8)
        self.wait(3)

        self.clear_all()


# ═════════════════════════════════════════════════════════════════════════════
# Part 2 · 承 — Intuition
# ═════════════════════════════════════════════════════════════════════════════

def build_cave(scale=0.85, offset=ORIGIN):
    """Return (cave_group, door_mob).  Indices: 0-5 walls, 6 door, 7 door_label, 8 A, 9 B, 10 entrance."""
    c = "#4a4a6a"
    w = 4
    left_w = Line(UP * 2.5 + LEFT * 1.5, DOWN * 0.5 + LEFT * 1.5, color=c, stroke_width=w)
    right_w = Line(UP * 2.5 + RIGHT * 1.5, DOWN * 0.5 + RIGHT * 1.5, color=c, stroke_width=w)
    left_in = Line(DOWN * 0.5 + LEFT * 1.5, DOWN * 2.5 + LEFT * 0.6, color=c, stroke_width=w)
    right_in = Line(DOWN * 0.5 + RIGHT * 1.5, DOWN * 2.5 + RIGHT * 0.6, color=c, stroke_width=w)
    bot_l = Line(DOWN * 2.5 + LEFT * 0.6, DOWN * 2.5 + LEFT * 0.15, color=c, stroke_width=w)
    bot_r = Line(DOWN * 2.5 + RIGHT * 0.6, DOWN * 2.5 + RIGHT * 0.15, color=c, stroke_width=w)
    door = DashedLine(DOWN * 2.5 + LEFT * 0.15, DOWN * 2.5 + RIGHT * 0.15, color=ACCENT, stroke_width=3, dash_length=0.08)
    door_lbl = Text("密码门", font=FONT, font_size=16, color=ACCENT).next_to(door, DOWN, buff=0.15)
    la = Text("A", font_size=24, color=PROVER_CLR).move_to(DOWN * 1.5 + LEFT * 1.0)
    lb = Text("B", font_size=24, color=PROVER_CLR).move_to(DOWN * 1.5 + RIGHT * 1.0)
    ent = Text("入口", font=FONT, font_size=18, color=MUTED).next_to(UP * 2.5, UP, buff=0.2)
    cave = VGroup(left_w, right_w, left_in, right_in, bot_l, bot_r, door, door_lbl, la, lb, ent)
    cave.scale(scale).shift(offset)
    return cave, door


class S03_CaveIntroScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("阿里巴巴的洞穴", font=FONT, font_size=42, color=WHITE)
        self.play(Write(sec), run_time=1)
        self.show_sub("让我们从一个经典的思想实验开始。\n这个实验叫做「阿里巴巴的洞穴」，是密码学家们最喜欢的类比。")
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3), run_time=0.6)

        self.show_sub("想象一个环形洞穴，只有一个入口。\n深处有一道需要咒语才能打开的密码门，把通道分成了 A 路和 B 路。")

        cave, door = build_cave(scale=0.85, offset=LEFT * 0.5)
        self.play(Create(cave), run_time=2.5)

        self.show_sub("现在有两个人登场。\nPeggy，证明者。Victor，验证者。\nPeggy 愿意证明她知道咒语，但绝不想把咒语告诉 Victor。")
        peggy = Dot(color=PROVER_CLR, radius=0.15).move_to(cave[0].get_start() + UP * 0.5 + LEFT * 0.3)
        p_lbl = Text("Peggy (证明者)", font=FONT, font_size=16, color=PROVER_CLR).next_to(peggy, LEFT, buff=0.15)
        victor = Dot(color=VERIFIER_CLR, radius=0.15).move_to(cave[1].get_start() + UP * 0.5 + RIGHT * 0.3)
        v_lbl = Text("Victor (验证者)", font=FONT, font_size=16, color=VERIFIER_CLR).next_to(victor, RIGHT, buff=0.15)
        self.play(FadeIn(peggy, p_lbl), FadeIn(victor, v_lbl), run_time=0.8)

        self.clear_all()


class S04_CaveProtocolScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG
        cave, door = build_cave(scale=0.8, offset=LEFT * 2)
        self.add(cave)

        peggy = Dot(color=PROVER_CLR, radius=0.15).move_to(cave[0].get_start() + UP * 0.5 + LEFT * 0.3)
        victor = Dot(color=VERIFIER_CLR, radius=0.15).move_to(cave[1].get_start() + UP * 0.5 + RIGHT * 0.3)
        self.add(peggy, victor)

        sec = Text("协议演示", font=FONT, font_size=28, color=MUTED).to_edge(UP, buff=0.25)
        self.add(sec)

        # ── SUCCESS CASE ────────────────────────────────────────────────────
        success_lbl = Text("✓ 知道咒语", font=FONT, font_size=20, color=OK_CLR).to_edge(UR, buff=0.5)
        self.play(FadeIn(success_lbl), run_time=0.4)

        self.show_sub("他们约定了一套协议。", wait=2)

        # Step 1
        self.show_sub("第一步：Victor 转过身去不看。\nPeggy 随机选择 A 路或 B 路走进洞穴深处。")
        self.play(victor.animate.set_opacity(0.3), run_time=0.4)
        path_a_bottom = cave[2].get_end()
        self.play(peggy.animate.move_to(path_a_bottom + RIGHT * 0.25), run_time=1.2)

        # Step 2
        self.show_sub("第二步：Victor 转过来，走到洞口，\n随机喊出一个方向——比如「请从 B 路出来！」")
        self.play(victor.animate.set_opacity(1), run_time=0.3)
        bub = RoundedRectangle(width=1.8, height=0.55, corner_radius=0.12,
                               fill_color=VERIFIER_CLR, fill_opacity=0.15,
                               stroke_color=VERIFIER_CLR, stroke_width=2).next_to(victor, UP, buff=0.12)
        bt = Text("从 B 出来！", font=FONT, font_size=14, color=VERIFIER_CLR).move_to(bub)
        self.play(FadeIn(bub, bt), run_time=0.5)

        # Step 3 — success
        self.show_sub("如果 Peggy 真的知道咒语，她可以念动咒语，\n穿过密码门，从指定方向走出来。漂亮，验证通过！")
        self.play(door.animate.set_opacity(0.15), Flash(door, color=ACCENT, num_lines=8, line_length=0.2), run_time=0.6)
        path_b_bottom = cave[3].get_end()
        self.play(peggy.animate.move_to(path_b_bottom + LEFT * 0.25), run_time=0.6)
        self.play(peggy.animate.move_to(victor.get_center() + LEFT * 0.5 + DOWN * 0.3), run_time=0.6)
        check = Text("✓", font_size=42, color=OK_CLR).next_to(peggy, UP, buff=0.1)
        self.play(FadeIn(check, scale=1.5), run_time=0.4)

        # Reset
        self.play(FadeOut(bub, bt, check, success_lbl), run_time=0.4)
        door.set_opacity(1)
        peggy.move_to(cave[0].get_start() + UP * 0.5 + LEFT * 0.3)

        # ── FAILURE CASE ────────────────────────────────────────────────────
        fail_lbl = Text("✗ 不知道咒语", font=FONT, font_size=20, color=FAIL_CLR).to_edge(UR, buff=0.5)
        peggy_fake = peggy.copy().set_color(MUTED)
        self.play(FadeIn(fail_lbl), ReplacementTransform(peggy, peggy_fake), run_time=0.5)

        self.show_sub("但如果 Peggy 其实根本不知道咒语呢？")

        # Step 1 fail
        self.show_sub("她走进了 A 路，Victor 喊「从 B 出来」——\n她打不开门，只能硬着头皮从 A 路出来。穿帮了！")
        self.play(victor.animate.set_opacity(0.3), run_time=0.3)
        self.play(peggy_fake.animate.move_to(path_a_bottom + RIGHT * 0.25), run_time=1)

        # Step 2 fail
        self.play(victor.animate.set_opacity(1), run_time=0.3)
        bub2 = bub.copy().next_to(victor, UP, buff=0.12)
        bt2 = bt.copy().move_to(bub2)
        self.play(FadeIn(bub2, bt2), run_time=0.4)
        self.play(door.animate.set_color(FAIL_CLR), Wiggle(door), run_time=0.8)
        door.set_color(ACCENT)

        self.play(peggy_fake.animate.move_to(cave[0].get_start() + DOWN * 0.3), run_time=0.8)
        x_mark = Text("✗", font_size=42, color=FAIL_CLR).next_to(peggy_fake, UP, buff=0.1)
        caught = Text("穿帮！", font=FONT, font_size=22, color=FAIL_CLR).next_to(x_mark, RIGHT, buff=0.15)
        self.play(FadeIn(x_mark, caught, scale=1.3), run_time=0.5)

        self.show_sub("当然，她也有可能运气好，恰好选了对的路。\n但这个概率只有——百分之五十。")
        prob50 = MathTex(r"50\%", font_size=48, color=ACCENT).shift(RIGHT * 3.5)
        self.play(Write(prob50), run_time=0.6)

        self.clear_all()


class S05_ProbabilityScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("重复挑战", font=FONT, font_size=38, color=WHITE)
        self.play(Write(sec), run_time=0.6)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3))

        self.show_sub("百分之五十的通过率显然不够。但如果我们重复这个过程呢？")

        formula = MathTex(
            r"P(\text{cheat}) = \left(\frac{1}{2}\right)^n",
            font_size=38, color=ACCENT,
        ).next_to(sec, DOWN, buff=0.5)
        self.play(Write(formula), run_time=1.5)
        self.wait(0.5)

        axes = Axes(
            x_range=[0, 22, 5], y_range=[0, 1, 0.2],
            x_length=9, y_length=3.8,
            axis_config={"color": MUTED, "font_size": 18},
            tips=False,
        ).shift(DOWN * 0.6)
        xl = axes.get_x_axis_label(Text("轮次 n", font=FONT, font_size=18), edge=DOWN, direction=DOWN)
        yl = axes.get_y_axis_label(Text("概率", font=FONT, font_size=18), edge=LEFT, direction=LEFT)
        self.play(Create(axes), Write(xl), Write(yl), run_time=1)

        graph = axes.plot(lambda x: 0.5 ** x, x_range=[0.3, 22], color=FAIL_CLR)

        self.show_sub("重复 2 次，概率降到 25%。5 次，3%。\n10 次，千分之一。20 次？大约百万分之一。")
        self.play(Create(graph), run_time=2.5)

        annotations = [
            (2, r"25\%"), (5, r"3.1\%"), (10, r"0.1\%"), (20, r"0.0001\%"),
        ]
        dots = VGroup()
        for n, label in annotations:
            d = Dot(axes.c2p(n, 0.5 ** n), color=ACCENT, radius=0.06)
            t = MathTex(f"n={n}:\\;" + label, font_size=18, color=ACCENT).next_to(d, UR, buff=0.1)
            dots.add(VGroup(d, t))
        self.play(FadeIn(dots, lag_ratio=0.25), run_time=2)

        self.show_sub("每多一轮，作弊空间就被压缩一半。\n这就是零知识证明的精妙之处：通过反复随机挑战，让谎言无处藏身。")

        self.clear_all()


class S06_CoreInsightScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("现在让我们站在 Victor 的角度想一想。")

        victor_icon = VGroup(
            Circle(radius=0.35, color=VERIFIER_CLR, stroke_width=3),
            Text("V", font_size=28, color=VERIFIER_CLR),
        )
        victor_icon.shift(UP * 1.5)
        self.play(FadeIn(victor_icon), run_time=0.6)

        info_items = [
            ("Peggy 走了哪条路？", "❓", FAIL_CLR),
            ("咒语内容？", "❓", FAIL_CLR),
            ("能向第三人复述？", "✗", FAIL_CLR),
        ]
        cards = VGroup()
        for label, icon, clr in info_items:
            r = RoundedRectangle(width=3.2, height=0.7, corner_radius=0.1,
                                 fill_color=CARD_BG, fill_opacity=0.9,
                                 stroke_color=clr, stroke_width=1.5)
            lt = Text(label, font=FONT, font_size=18, color=WHITE).move_to(r).shift(LEFT * 0.4)
            it = Text(icon, font_size=24, color=clr).move_to(r).shift(RIGHT * 1.2)
            cards.add(VGroup(r, lt, it))
        cards.arrange(DOWN, buff=0.2).next_to(victor_icon, DOWN, buff=0.6)

        self.show_sub("他不知道 Peggy 从哪条路进去的，不知道咒语是什么，\n他甚至无法向第三个人复述这个证明。")
        for c in cards:
            self.play(FadeIn(c, shift=LEFT * 0.3), run_time=0.5)

        self.show_sub("但 Victor 自己心里清楚：\n连续 20 轮都蒙对，这不是运气，这是实力。")
        scoreboard = VGroup(
            Text("20 / 20 通过", font=FONT, font_size=32, color=OK_CLR),
            MathTex(r"P < 0.0001\%", font_size=24, color=ACCENT),
        ).arrange(DOWN, buff=0.2).shift(RIGHT * 3 + UP * 0.5)
        self.play(FadeIn(scoreboard, scale=1.2), run_time=0.8)

        self.clear_all()


class S07_PropertiesScene(SubtitleMixin, Scene):
    def _card(self, title_cn, title_en, desc, icon, border_clr):
        card = RoundedRectangle(width=3.5, height=4.2, corner_radius=0.18,
                                fill_color=CARD_BG, fill_opacity=0.9,
                                stroke_color=border_clr, stroke_width=2)
        icon.scale_to_fit_height(0.7)
        tc = Text(title_cn, font=FONT, font_size=22, color=border_clr)
        te = Text(title_en, font_size=15, color=MUTED)
        d = Text(desc, font=FONT, font_size=15, color=WHITE, line_spacing=1.4)
        content = VGroup(icon, tc, te, d).arrange(DOWN, buff=0.25)
        content.move_to(card)
        return VGroup(card, content)

    def construct(self):
        self.camera.background_color = BG
        sec = Text("三大性质", font=FONT, font_size=42, color=WHITE)
        self.play(Write(sec), run_time=0.8)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3))

        chk = VGroup(
            Line(ORIGIN, DR * 0.3 + RIGHT * 0.1, color=OK_CLR, stroke_width=6),
            Line(DR * 0.3 + RIGHT * 0.1, UR * 0.7 + RIGHT * 0.3, color=OK_CLR, stroke_width=6),
        )
        cross = VGroup(
            Line(UL * 0.3, DR * 0.3, color=FAIL_CLR, stroke_width=6),
            Line(UR * 0.3, DL * 0.3, color=FAIL_CLR, stroke_width=6),
        )
        bulb = VGroup(
            Circle(radius=0.22, color=ACCENT, stroke_width=3),
            Rectangle(width=0.18, height=0.12, color=ACCENT, stroke_width=3).shift(DOWN * 0.28),
        )

        c1 = self._card("完备性", "Completeness", "如果 Peggy 确实知道\n咒语，Victor 一定\n会被说服", chk, OK_CLR)
        c2 = self._card("可靠性", "Soundness", "如果 Peggy 在撒谎\n她几乎不可能通过\n所有轮次", cross, FAIL_CLR)
        c3 = self._card("零知识性", "Zero-Knowledge", "Victor 除了确信\n「Peggy 知道咒语」\n什么也没学到", bulb, ACCENT)
        cards = VGroup(c1, c2, c3).arrange(RIGHT, buff=0.35)
        cards.next_to(sec, DOWN, buff=0.55)

        self.show_sub("密码学家把零知识证明的特性总结为三条。", wait=2)

        narrations = [
            "第一，完备性。如果 Peggy 确实知道咒语，\n只要双方诚实执行协议，Victor 一定会被说服。",
            "第二，可靠性。如果 Peggy 在撒谎，\n她通过所有轮次挑战的概率趋近于零。",
            "第三，零知识性。Victor 在整个过程中，\n除了确信「Peggy 知道咒语」之外，没有获得任何额外信息。",
        ]
        for card, narr in zip([c1, c2, c3], narrations):
            self.show_sub(narr)
            self.play(FadeIn(card, shift=UP * 0.4), run_time=0.8)
        self.clear_all()


# ═════════════════════════════════════════════════════════════════════════════
# Part 3 · 转 — Mathematics
# ═════════════════════════════════════════════════════════════════════════════

class S08_MathBridgeScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("洞穴的故事很直观，但你可能会问：\n这真的能用数学实现吗？现实世界里可没有魔法洞穴。")
        q = Text("?", font_size=100, color=ACCENT)
        self.play(FadeIn(q, scale=0.3), run_time=0.8)

        self.show_sub("答案是——完全可以。我们需要一个数学版的「密码门」：\n一个正向计算很容易，但反向破解几乎不可能的问题。\n密码学家管这种问题叫做单向函数。")
        self.play(FadeOut(q), run_time=0.4)

        box = RoundedRectangle(width=3, height=1.6, corner_radius=0.2,
                               fill_color=CARD_BG, fill_opacity=0.9,
                               stroke_color=MUTED, stroke_width=2)
        box_lbl = Text("f", font_size=36, color=WHITE).move_to(box)

        x_txt = MathTex("x", font_size=36, color=PROVER_CLR).next_to(box, LEFT, buff=1)
        fx_txt = MathTex("f(x)", font_size=36, color=VERIFIER_CLR).next_to(box, RIGHT, buff=1)

        fwd = Arrow(x_txt.get_right(), box.get_left(), buff=0.15, color=OK_CLR, stroke_width=4)
        fwd2 = Arrow(box.get_right(), fx_txt.get_left(), buff=0.15, color=OK_CLR, stroke_width=4)
        fwd_lbl = Text("容易", font=FONT, font_size=18, color=OK_CLR).next_to(fwd, UP, buff=0.1)

        bwd = Arrow(fx_txt.get_left(), box.get_right(), buff=0.15, color=FAIL_CLR, stroke_width=3,
                     max_tip_length_to_length_ratio=0.15)
        bwd.shift(DOWN * 0.8)
        lock_icon = Text("🔒", font_size=22).next_to(bwd, DOWN, buff=0.08)
        bwd_lbl = Text("几乎不可能", font=FONT, font_size=18, color=FAIL_CLR).next_to(lock_icon, DOWN, buff=0.08)

        self.play(FadeIn(box, box_lbl), run_time=0.6)
        self.play(FadeIn(x_txt), GrowArrow(fwd), GrowArrow(fwd2), FadeIn(fx_txt), Write(fwd_lbl), run_time=1.2)
        self.wait(1)
        self.play(GrowArrow(bwd), FadeIn(lock_icon, bwd_lbl), run_time=1)
        self.wait(3)

        self.clear_all()


class S09_DiscreteLogScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("离散对数问题", font=FONT, font_size=38, color=WHITE)
        self.play(Write(sec), run_time=0.6)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3))

        self.show_sub("给你一个大素数 p、一个生成元 g，\n正向计算 y = g^x mod p，非常快，计算机瞬间就能完成。")

        fwd_eq = MathTex(r"y = g^{x} \bmod p", font_size=40, color=OK_CLR)
        fwd_eq.shift(UP * 1)
        fwd_arrow = Arrow(LEFT * 2 + UP * 0.3, RIGHT * 2 + UP * 0.3, color=OK_CLR, stroke_width=3)
        fwd_label = Text("⚡ 瞬间完成", font=FONT, font_size=20, color=OK_CLR).next_to(fwd_arrow, DOWN, buff=0.15)

        self.play(Write(fwd_eq), run_time=1.2)
        self.play(GrowArrow(fwd_arrow), FadeIn(fwd_label), run_time=0.8)

        self.show_sub("但是反过来，已知 g、p 和 y，要反推出 x 是多少？\n以目前人类的计算能力，当 p 足够大的时候，这基本上是不可能的。")
        rev_eq = MathTex(r"x = \log_g y \bmod p \;\;???", font_size=36, color=FAIL_CLR)
        rev_eq.shift(DOWN * 1)
        bar_bg = RoundedRectangle(width=5, height=0.35, corner_radius=0.08,
                                  fill_color=MUTED, fill_opacity=0.3,
                                  stroke_color=MUTED, stroke_width=1).shift(DOWN * 1.8)
        bar_fill = RoundedRectangle(width=0.02, height=0.3, corner_radius=0.06,
                                    fill_color=FAIL_CLR, fill_opacity=0.9,
                                    stroke_width=0).align_to(bar_bg, LEFT).shift(DOWN * 1.8 + RIGHT * 0.02)
        bar_pct = Text("0.001%", font_size=16, color=FAIL_CLR).next_to(bar_bg, RIGHT, buff=0.2)
        infeasible = Text("计算上不可行", font=FONT, font_size=20, color=FAIL_CLR).next_to(bar_bg, DOWN, buff=0.2)

        self.play(Write(rev_eq), run_time=1)
        self.play(FadeIn(bar_bg, bar_fill, bar_pct), run_time=0.8)
        self.play(FadeIn(infeasible), run_time=0.5)

        self.show_sub("这就是我们的数学版密码门。\n知道 x，就像知道咒语——你能轻松算出 y，但别人看到 y，猜不出 x。")

        self.clear_all()


class S10_SchnorrProtocolScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("Schnorr 协议", font=FONT, font_size=36, color=WHITE)
        self.play(Write(sec), run_time=0.6)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.2))

        self.show_sub("1989 年，德国密码学家 Claus-Peter Schnorr\n基于离散对数难题，设计了一个优雅的零知识证明协议。")

        # Public params
        self.show_sub("假设公开信息是 g、p 和 y，其中 y = g^x mod p。\nPeggy 知道秘密 x，她要向 Victor 证明这一点。")
        pub = MathTex(r"g,\; p,\; y = g^x \bmod p", font_size=28, color=ACCENT)
        x_secret = MathTex(r"x\text{ (secret)}", font_size=22, color=FAIL_CLR)
        params = VGroup(pub, x_secret).arrange(RIGHT, buff=0.8).next_to(sec, DOWN, buff=0.35)
        self.play(Write(pub), Write(x_secret), run_time=1.2)

        # Columns
        p_rect = RoundedRectangle(width=2.8, height=0.6, corner_radius=0.12,
                                  fill_color=PROVER_CLR, fill_opacity=0.15,
                                  stroke_color=PROVER_CLR, stroke_width=2).shift(LEFT * 4.2 + UP * 0.8)
        p_lbl = Text("Prover", font_size=20, color=PROVER_CLR).move_to(p_rect)
        v_rect = RoundedRectangle(width=2.8, height=0.6, corner_radius=0.12,
                                  fill_color=VERIFIER_CLR, fill_opacity=0.15,
                                  stroke_color=VERIFIER_CLR, stroke_width=2).shift(RIGHT * 4.2 + UP * 0.8)
        v_lbl = Text("Verifier", font_size=20, color=VERIFIER_CLR).move_to(v_rect)
        self.play(FadeIn(p_rect, p_lbl, v_rect, v_lbl), run_time=0.6)

        y_pos = 0.0
        step_gap = 1.15

        # Step 1 — Commit
        self.show_sub("第一步，承诺。Peggy 选一个随机数 r，\n计算 t = g^r mod p，然后把 t 发给 Victor。\n这个随机数 r 就像她在洞穴里随机选路一样——它是一层保护 x 的面纱。")
        s1a = MathTex(r"r \xleftarrow{R} \mathbb{Z}_q", font_size=22, color=PROVER_CLR).move_to(LEFT * 4.2 + UP * y_pos)
        s1b = MathTex(r"t = g^r \bmod p", font_size=22, color=PROVER_CLR).next_to(s1a, DOWN, buff=0.15)
        a1 = Arrow(LEFT * 2.5 + UP * (y_pos - 0.15), RIGHT * 2.5 + UP * (y_pos - 0.15),
                    buff=0.1, color=WHITE, stroke_width=2, max_tip_length_to_length_ratio=0.08)
        a1l = MathTex("t", font_size=20, color=WHITE).next_to(a1, UP, buff=0.08)
        self.play(Write(s1a), run_time=0.6)
        self.play(Write(s1b), run_time=0.6)
        self.play(GrowArrow(a1), Write(a1l), run_time=0.5)

        # Step 2 — Challenge
        y2 = y_pos - step_gap
        self.show_sub("第二步，挑战。Victor 随机选一个数 c，发给 Peggy。\n这就像 Victor 在洞口随机喊方向。")
        s2 = MathTex(r"c \xleftarrow{R} \mathbb{Z}_q", font_size=22, color=VERIFIER_CLR).move_to(RIGHT * 4.2 + UP * y2)
        a2 = Arrow(RIGHT * 2.5 + UP * y2, LEFT * 2.5 + UP * y2,
                    buff=0.1, color=WHITE, stroke_width=2, max_tip_length_to_length_ratio=0.08)
        a2l = MathTex("c", font_size=20, color=WHITE).next_to(a2, UP, buff=0.08)
        self.play(Write(s2), run_time=0.6)
        self.play(GrowArrow(a2), Write(a2l), run_time=0.5)

        # Step 3 — Response
        y3 = y2 - step_gap
        self.show_sub("第三步，响应。Peggy 计算 s = r + c·x，把 s 发给 Victor。\n注意，s 把 x 巧妙地藏在了 r 的随机噪声里。")
        s3 = MathTex(r"s = r + c \cdot x", font_size=22, color=PROVER_CLR).move_to(LEFT * 4.2 + UP * y3)
        a3 = Arrow(LEFT * 2.5 + UP * y3, RIGHT * 2.5 + UP * y3,
                    buff=0.1, color=WHITE, stroke_width=2, max_tip_length_to_length_ratio=0.08)
        a3l = MathTex("s", font_size=20, color=WHITE).next_to(a3, UP, buff=0.08)
        self.play(Write(s3), run_time=0.6)
        self.play(GrowArrow(a3), Write(a3l), run_time=0.5)

        # Step 4 — Verify
        y4 = y3 - step_gap
        self.show_sub("第四步，验证。Victor 检查一个等式：\ng^s 是否等于 t · y^c (mod p)。如果等式成立——验证通过。")
        verify = MathTex(r"g^s \stackrel{?}{\equiv} t \cdot y^c \pmod{p}", font_size=26, color=VERIFIER_CLR)
        verify.move_to(RIGHT * 4.2 + UP * y4)
        vbox = SurroundingRectangle(verify, color=OK_CLR, buff=0.12, corner_radius=0.08)
        self.play(Write(verify), run_time=0.8)
        self.play(Create(vbox), run_time=0.5)

        # Key insight
        self.show_sub("整个过程中，x 从来没有被发送过。\nVictor 只看到了三个数：t、c、s。")
        insight = RoundedRectangle(width=10, height=0.7, corner_radius=0.12,
                                   fill_color=CARD_BG, fill_opacity=0.9,
                                   stroke_color=ACCENT, stroke_width=2).shift(DOWN * 3)
        itxt = Text("秘密 x 从未被发送 — Victor 只看到 t, c, s",
                     font=FONT, font_size=20, color=ACCENT).move_to(insight)
        self.play(FadeIn(insight, itxt), run_time=0.8)
        self.wait(2.5)

        self.clear_all()


class S11_VerificationScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("为什么验证成立？", font=FONT, font_size=36, color=WHITE)
        self.play(Write(sec), run_time=0.6)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.35))

        self.show_sub("为什么这个验证等式一定成立？让我们展开看一看。")

        eqs = [
            (r"g^s", WHITE),
            (r"= g^{\,r\, +\, c\,x}", WHITE),
            (r"= g^r \cdot g^{\,c\,x}", WHITE),
            (r"= g^r \cdot (g^x)^c", WHITE),
            (r"= t \cdot y^c", ACCENT),
        ]
        tex_objs = VGroup(*[MathTex(e, font_size=38, color=c) for e, c in eqs])
        tex_objs.arrange(DOWN, buff=0.38).center()

        narrations = [
            "g 的 s 次方……",
            "把 s 代入，就是 g 的 r 加 cx 次方。",
            "根据指数法则，这等于 g^r 乘以 g^{cx}。",
            "而 g^{cx} 可以写成 (g^x) 的 c 次方，也就是 y 的 c 次方。",
            "所以最终等于 t 乘以 y^c。等式两边完美吻合！",
        ]

        for tex, narr in zip(tex_objs, narrations):
            self.show_sub(narr)
            self.play(Write(tex), run_time=1)

        qed = MathTex(r"\blacksquare", font_size=36, color=OK_CLR)
        qed.next_to(tex_objs, RIGHT, buff=0.5).align_to(tex_objs[-1], DOWN)
        self.show_sub("等式两边完美吻合。证毕。")
        self.play(FadeIn(qed, scale=1.5), run_time=0.5)

        self.clear_all()


class S12_SimulatorScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("为什么是「零知识」？", font=FONT, font_size=36, color=WHITE)
        self.play(Write(sec), run_time=0.6)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3))

        self.show_sub("但等一下——等式成立只说明协议是正确的。\n还没有回答：为什么它是零知识的？")

        self.show_sub("这里有一个精妙的论证。\n想象存在一个「模拟器」——它完全不知道秘密 x，\n但它能凭空生成一份和真实交互看起来一模一样的对话记录。")

        # Real panel
        rh = Text("真实交互", font=FONT, font_size=20, color=PROVER_CLR)
        rb = RoundedRectangle(width=4.8, height=3.2, corner_radius=0.12,
                              fill_color=CARD_BG, fill_opacity=0.9,
                              stroke_color=PROVER_CLR, stroke_width=2)
        rs = VGroup(
            MathTex(r"1.\; r \leftarrow \mathbb{Z}_q", font_size=18, color=WHITE),
            MathTex(r"2.\; t = g^r \bmod p", font_size=18, color=WHITE),
            MathTex(r"3.\; c \leftarrow \text{Verifier}", font_size=18, color=WHITE),
            MathTex(r"4.\; s = r + cx", font_size=18, color=WHITE),
            MathTex(r"\Rightarrow (t,\, c,\, s)", font_size=18, color=ACCENT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        rh.next_to(rb, UP, buff=0.12)
        rs.move_to(rb)

        # Sim panel
        sh = Text("模拟器 (不知道 x)", font=FONT, font_size=20, color=VERIFIER_CLR)
        sb = RoundedRectangle(width=4.8, height=3.2, corner_radius=0.12,
                              fill_color=CARD_BG, fill_opacity=0.9,
                              stroke_color=VERIFIER_CLR, stroke_width=2)
        ss = VGroup(
            MathTex(r"1.\; c \leftarrow \mathbb{Z}_q", font_size=18, color=WHITE),
            MathTex(r"2.\; s \leftarrow \mathbb{Z}_q", font_size=18, color=WHITE),
            MathTex(r"3.\; t = g^s \cdot y^{-c}", font_size=18, color=WHITE),
            MathTex(r"\Rightarrow (t,\, c,\, s)", font_size=18, color=ACCENT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        sh.next_to(sb, UP, buff=0.12)
        ss.move_to(sb)

        real_grp = VGroup(rh, rb, rs)
        sim_grp = VGroup(sh, sb, ss)
        panels = VGroup(real_grp, sim_grp).arrange(RIGHT, buff=0.5).shift(DOWN * 0.3)

        self.play(FadeIn(rb), Write(rh), run_time=0.6)
        for s in rs:
            self.play(Write(s), run_time=0.4)
        self.wait(0.5)

        self.show_sub("模拟器的做法是：它先随机选 c 和 s，\n然后反推出 t = g^s · y^{-c}。")
        self.play(FadeIn(sb), Write(sh), run_time=0.6)
        for s in ss:
            self.play(Write(s), run_time=0.4)

        self.show_sub("你把真实记录和模拟记录放在一起比较——\n数学上可以证明，它们的概率分布完全相同。")
        # Highlight equivalence
        eq = MathTex(r"\cong", font_size=44, color=OK_CLR)
        eq.move_to((rb.get_right() + sb.get_left()) / 2)
        el = Text("分布相同！", font=FONT, font_size=18, color=OK_CLR).next_to(eq, DOWN, buff=0.12)
        self.play(Write(eq), Write(el), run_time=0.8)
        self.play(rb.animate.set_stroke(color=OK_CLR), sb.animate.set_stroke(color=OK_CLR), run_time=0.6)

        self.show_sub("如果 Victor 自己就能伪造出一模一样的对话记录，\n那这段真实的交互不可能教会他任何新东西。\n这就是「零知识」的数学本质。")

        self.clear_all()


# ═════════════════════════════════════════════════════════════════════════════
# Part 4 · 合 — Synthesis & Outro
# ═════════════════════════════════════════════════════════════════════════════

class S13_ApplicationScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("现实世界中的零知识证明", font=FONT, font_size=38, color=WHITE)
        self.play(Write(sec), run_time=0.8)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.35))

        apps = [
            ("zk-SNARKs / zk-STARKs", "证明交易合法\n不透露任何交易细节", PROVER_CLR,
             "区块链隐私"),
            ("身份认证", "证明你年满 18 岁\n无需出示整张身份证", VERIFIER_CLR,
             "选择性披露"),
            ("隐私计算", "多方联合计算结果\n不暴露任何原始数据", ACCENT,
             "数据协作"),
        ]

        cards = VGroup()
        for name, desc, clr, tag in apps:
            card = RoundedRectangle(width=3.5, height=3.0, corner_radius=0.18,
                                    fill_color=CARD_BG, fill_opacity=0.9,
                                    stroke_color=clr, stroke_width=2)
            tag_txt = Text(tag, font=FONT, font_size=14, color=MUTED)
            n = Text(name, font=FONT, font_size=18, color=clr)
            d = Text(desc, font=FONT, font_size=14, color=WHITE, line_spacing=1.3)
            VGroup(tag_txt, n, d).arrange(DOWN, buff=0.3).move_to(card)
            cards.add(VGroup(card, tag_txt, n, d))

        cards.arrange(RIGHT, buff=0.35).next_to(sec, DOWN, buff=0.6)

        self.show_sub("零知识证明不只是纸上的数学。它正在深刻地改变现实世界。", wait=2)

        narrations = [
            "在区块链领域，zk-SNARKs 和 zk-STARKs 让你能证明一笔交易合法，\n而不需要透露金额、发送方或接收方的任何信息。",
            "在身份验证中，你可以证明自己年满 18 岁，\n而不需要出示整张身份证。对方只知道你够年龄。",
            "在隐私计算中，多个机构可以联合分析数据、训练模型，\n而不需要互相暴露任何原始数据。",
        ]
        for card, narr in zip(cards, narrations):
            self.show_sub(narr)
            self.play(FadeIn(card, shift=UP * 0.4), run_time=0.8)
        self.clear_all()


class S14_OutroScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        # Callback to opening
        self.show_sub("让我们回到最开始那个问题。")
        q = Text(
            "你能不能证明你知道密码\n却不泄露密码本身？",
            font=FONT, font_size=34, color=WHITE, line_spacing=1.6,
        )
        self.show_sub("你能不能证明你知道密码，却不泄露密码本身？")
        self.play(Write(q), run_time=2)

        self.show_sub("现在我们知道了：答案是——可以。")
        ans = Text("可以。", font=FONT, font_size=64, color=OK_CLR)
        self.play(ReplacementTransform(q, ans), run_time=1.2)

        self.play(FadeOut(ans), run_time=0.6)

        # Philosophy
        self.show_sub("零知识证明告诉我们一个深刻的道理：\n证明一件事，不需要展示这件事本身。")
        p1 = Text(
            "证明一件事\n不需要展示这件事本身",
            font=FONT, font_size=32, color=WHITE, line_spacing=1.5,
        )
        self.play(Write(p1), run_time=2)

        self.show_sub("你只需要展示，你能做到只有知道秘密才能做到的事情。")
        p2 = Text(
            "你只需要展示\n你能做到只有知道秘密\n才能做到的事",
            font=FONT, font_size=28, color=ACCENT, line_spacing=1.5,
        )
        self.play(ReplacementTransform(p1, p2), run_time=1.5)

        self.play(FadeOut(p2), run_time=0.6)

        # Final line
        self.hide_sub()
        final = Text(
            "在不暴露秘密的前提下\n证明你掌握真理",
            font=FONT, font_size=42, color=ACCENT, line_spacing=1.6,
        )
        self.play(Write(final), run_time=2.5)
        self.wait(3)

        coda = Text("这就是零知识证明的美。", font=FONT, font_size=28, color=MUTED)
        coda.next_to(final, DOWN, buff=0.6)
        self.play(FadeIn(coda, shift=UP * 0.2), run_time=1)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=2)
        self._save_stamps()
