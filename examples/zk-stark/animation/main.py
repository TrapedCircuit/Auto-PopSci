"""
ZK-STARKs — 10-minute science-popularization Manim animation.
Narration-first design: each scene carries subtitle text matching script.md.
Audio sync via timestamp logging + ffmpeg post-merge.
"""

from manim import *
import numpy as np
from base import (
    SubtitleMixin, BG, PROVER_CLR, VERIFIER_CLR,
    OK_CLR, FAIL_CLR, ACCENT, MUTED, CARD_BG, FONT,
)

SECONDARY = "#e67e22"
POLY_CLR = "#9b59b6"
FIELD_CLR = "#1abc9c"


# ═════════════════════════════════════════════════════════════════════════════
# Part 1 · 起 — Hook & Prerequisites
# ═════════════════════════════════════════════════════════════════════════════

class S01_HookScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("假设你是一个国家的审计官。")
        auditor = VGroup(
            Circle(radius=0.35, color=VERIFIER_CLR, stroke_width=3),
            Text("审计官", font=FONT, font_size=16, color=VERIFIER_CLR),
        ).arrange(DOWN, buff=0.15).shift(LEFT * 4)
        self.play(FadeIn(auditor, shift=UP * 0.3), run_time=0.8)

        self.show_sub(
            "一台超级计算机刚刚处理了100亿笔金融交易，"
            "声称所有交易全部合规。你信吗？"
        )
        server = RoundedRectangle(
            width=2.4, height=1.8, corner_radius=0.15,
            fill_color=CARD_BG, fill_opacity=0.9,
            stroke_color=PROVER_CLR, stroke_width=2,
        )
        srv_label = Text("超级计算机", font=FONT, font_size=16, color=PROVER_CLR)
        srv_icon = VGroup(
            *[Rectangle(width=1.6, height=0.15, fill_color=PROVER_CLR,
                        fill_opacity=0.3, stroke_width=0).shift(UP * (0.3 - i * 0.25))
              for i in range(4)]
        ).move_to(server)
        srv_label.next_to(server, UP, buff=0.15)
        srv_grp = VGroup(server, srv_icon, srv_label)
        counter = Text("10,000,000,000 笔", font=FONT, font_size=20, color=ACCENT)
        counter.next_to(server, DOWN, buff=0.3)
        self.play(FadeIn(srv_grp, shift=DOWN * 0.3), run_time=0.8)
        self.play(Write(counter), run_time=1)

        self.show_sub(
            "要你自己重新验算一遍？那可能需要几个月。"
            "但如果我告诉你，有一种数学方法，"
            "能让你在几毫秒内就确认这台超级计算机没有撒谎呢？"
        )
        slow = VGroup(
            Text("重新验算", font=FONT, font_size=22, color=FAIL_CLR),
            Text("→ 几个月", font=FONT, font_size=22, color=FAIL_CLR),
        ).arrange(RIGHT, buff=0.3).shift(RIGHT * 3 + UP * 0.8)
        fast = VGroup(
            Text("数学验证", font=FONT, font_size=22, color=OK_CLR),
            Text("→ 几毫秒 ⚡", font=FONT, font_size=22, color=OK_CLR),
        ).arrange(RIGHT, buff=0.3).shift(RIGHT * 3 + DOWN * 0.2)
        self.play(FadeIn(slow, shift=LEFT * 0.3), run_time=0.6)
        self.play(FadeIn(fast, shift=LEFT * 0.3), run_time=0.6)

        self.show_sub(
            "而且，这个验证过程不需要信任任何人，"
            "不需要任何秘密仪式，完全公开透明。"
        )
        transparent = Text("完全公开透明", font=FONT, font_size=32, color=ACCENT)
        transparent.shift(DOWN * 2.5)
        self.play(Write(transparent), run_time=1)

        self.clear_all()


class S02_TitleScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("这就是今天的主角——")
        shield = VGroup(
            Polygon(
                UP * 1.2, LEFT * 0.9 + UP * 0.6, LEFT * 0.9 + DOWN * 0.3,
                DOWN * 0.9, RIGHT * 0.9 + DOWN * 0.3, RIGHT * 0.9 + UP * 0.6,
                fill_color=ACCENT, fill_opacity=0.15,
                stroke_color=ACCENT, stroke_width=3,
            ),
            MathTex(r"\pi", font_size=42, color=ACCENT),
        ).scale(0.7)
        self.play(FadeIn(shield, scale=0.5), run_time=0.6)
        self.play(shield.animate.scale(0.5).to_edge(UP, buff=0.6), run_time=0.6)

        self.show_sub("ZK-STARKs。")
        title = Text("ZK-STARKs", font_size=56, color=WHITE)
        full = Text(
            "Zero-Knowledge Scalable Transparent\nARguments of Knowledge",
            font_size=22, color=ACCENT, line_spacing=1.4,
        )
        titles = VGroup(title, full).arrange(DOWN, buff=0.4)
        self.play(Write(title), run_time=1.2)
        self.play(FadeIn(full, shift=UP * 0.2), run_time=0.8)
        self.wait(2)

        self.clear_all()


class S03_PrereqPolyScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("在深入STARKs之前，我们需要先认识两个关键工具。第一个是多项式。")
        sec = Text("预备知识：多项式", font=FONT, font_size=36, color=WHITE)
        self.play(Write(sec), run_time=0.8)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3), run_time=0.5)

        self.show_sub("你一定见过这样的函数：f(x)等于2x的平方加3x加1。这是一个二次多项式。")
        axes = Axes(
            x_range=[-3, 3, 1], y_range=[-2, 20, 5],
            x_length=8, y_length=4,
            axis_config={"color": MUTED, "font_size": 16},
            tips=False,
        ).shift(DOWN * 0.5)
        f_eq = MathTex(r"f(x) = 2x^2 + 3x + 1", font_size=32, color=POLY_CLR)
        f_eq.next_to(axes, UP, buff=0.3).shift(LEFT * 1.5)
        f_graph = axes.plot(lambda x: 2 * x**2 + 3 * x + 1, x_range=[-3, 2.5], color=POLY_CLR)
        self.play(Create(axes), run_time=0.8)
        self.play(Write(f_eq), Create(f_graph), run_time=1.2)

        self.show_sub(
            "多项式有一个非常强大的性质。"
            "如果两个不同的d次多项式，它们最多只能在d个点上相交。"
        )
        prop = Text(
            "不同的 d 次多项式\n最多 d 个交点",
            font=FONT, font_size=20, color=ACCENT, line_spacing=1.3,
        )
        prop_box = SurroundingRectangle(prop, color=ACCENT, buff=0.15, corner_radius=0.1)
        prop_grp = VGroup(prop_box, prop).to_edge(RIGHT, buff=0.4).shift(UP * 1.5)
        self.play(FadeIn(prop_grp), run_time=0.8)

        self.show_sub(
            "来看个例子。f(x)等于2x平方加3x加1，g(x)等于x平方加5x加1。"
            "它们都是二次的，所以最多只有2个交点。"
        )
        g_eq = MathTex(r"g(x) = x^2 + 5x + 1", font_size=32, color=SECONDARY)
        g_eq.next_to(f_eq, DOWN, buff=0.2, aligned_edge=LEFT)
        g_graph = axes.plot(lambda x: x**2 + 5 * x + 1, x_range=[-3, 2.5], color=SECONDARY)
        self.play(Write(g_eq), Create(g_graph), run_time=1)

        x1, x2 = 0.0, -2.0
        y1 = 2 * x1**2 + 3 * x1 + 1
        y2 = 2 * x2**2 + 3 * x2 + 1
        d1 = Dot(axes.c2p(x1, y1), color=ACCENT, radius=0.08)
        d2 = Dot(axes.c2p(x2, y2), color=ACCENT, radius=0.08)
        l1 = MathTex(r"x=0", font_size=16, color=ACCENT).next_to(d1, UR, buff=0.1)
        l2 = MathTex(r"x=-2", font_size=16, color=ACCENT).next_to(d2, UL, buff=0.1)
        self.play(FadeIn(d1, d2, l1, l2, scale=1.3), run_time=0.8)

        self.show_sub(
            "换句话说，如果我在一个很大的范围里随机选一个点去检查，"
            "两个不同多项式恰好在这个点上相等的概率极低。"
        )
        prob = MathTex(
            r"P(\text{match}) \leq \frac{d}{|S|}", font_size=30, color=ACCENT,
        ).shift(DOWN * 3)
        self.play(Write(prob), run_time=0.8)

        self.show_sub("这意味着什么？多项式就像指纹——几乎不可能伪造。")
        fingerprint = Text("多项式 ≈ 指纹", font=FONT, font_size=28, color=ACCENT)
        fp_box = SurroundingRectangle(fingerprint, color=ACCENT, buff=0.15, corner_radius=0.1)
        fp_grp = VGroup(fp_box, fingerprint).shift(DOWN * 3)
        self.play(ReplacementTransform(prob, fp_grp), run_time=0.8)

        self.clear_all()


class S04_PrereqFieldScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("第二个关键工具是有限域。")
        sec = Text("预备知识：有限域", font=FONT, font_size=36, color=WHITE)
        self.play(Write(sec), run_time=0.8)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3), run_time=0.5)

        self.show_sub(
            "你一定知道取模运算。比如在模7的世界里，"
            "3加5等于1，因为8 mod 7等于1。"
        )
        eq1 = MathTex("3", "+", "5", "=", "8", font_size=38, color=WHITE)
        eq2 = MathTex("8", r"\bmod", "7", "=", "1", font_size=38, color=FIELD_CLR)
        eqs = VGroup(eq1, eq2).arrange(DOWN, buff=0.4).shift(UP * 0.5)
        self.play(Write(eq1), run_time=0.8)
        self.play(Write(eq2), run_time=0.8)

        self.show_sub(
            "在这个世界里，数字只有0到6，"
            "做加减乘除全部绕着圈来。这就是一个有限域。"
        )
        self.play(FadeOut(eqs), run_time=0.4)
        ring = Circle(radius=1.8, color=FIELD_CLR, stroke_width=2).shift(LEFT * 0.5)
        nums = VGroup()
        for i in range(7):
            angle = PI / 2 - i * TAU / 7
            pos = ring.get_center() + 1.8 * np.array([np.cos(angle), np.sin(angle), 0])
            n = Text(str(i), font_size=24, color=WHITE)
            n.move_to(pos)
            dot = Dot(pos, radius=0.06, color=FIELD_CLR)
            nums.add(VGroup(dot, n))
        self.play(Create(ring), FadeIn(nums, lag_ratio=0.1), run_time=1.5)

        arrow_start_angle = PI / 2 - 3 * TAU / 7
        arrow_end_angle = PI / 2 - 1 * TAU / 7
        arc_arrow = Arc(
            radius=2.1, start_angle=arrow_start_angle,
            angle=(arrow_end_angle - arrow_start_angle) % TAU,
            color=ACCENT, stroke_width=3,
        ).shift(LEFT * 0.5)
        arc_label = MathTex(r"3 + 5 \equiv 1", font_size=22, color=ACCENT)
        arc_label.next_to(arc_arrow, RIGHT, buff=0.2)
        self.play(Create(arc_arrow), Write(arc_label), run_time=1)

        self.show_sub(
            "为什么要用有限域？因为计算机处理实数会有精度误差，"
            "但模运算是精确的。每一步计算都可以被完美复现。"
        )
        comp = VGroup(
            VGroup(
                Text("浮点数", font=FONT, font_size=18, color=FAIL_CLR),
                MathTex(r"0.1 + 0.2 = 0.300...04", font_size=22, color=FAIL_CLR),
            ).arrange(DOWN, buff=0.15),
            VGroup(
                Text("模运算", font=FONT, font_size=18, color=OK_CLR),
                MathTex(r"3 + 5 \equiv 1 \pmod{7}", font_size=22, color=OK_CLR),
            ).arrange(DOWN, buff=0.15),
        ).arrange(RIGHT, buff=1.5).shift(RIGHT * 3)
        self.play(FadeIn(comp, shift=LEFT * 0.3), run_time=1)

        self.show_sub(
            "当我们把多项式放在有限域上，就得到了STARKs的数学语言。"
            "接下来，你会看到它的威力。"
        )
        combo = Text("多项式 + 有限域 → STARKs", font=FONT, font_size=26, color=ACCENT)
        combo_box = SurroundingRectangle(combo, color=ACCENT, buff=0.15, corner_radius=0.1)
        combo_grp = VGroup(combo_box, combo).shift(DOWN * 2.8)
        self.play(FadeIn(combo_grp, shift=UP * 0.2), run_time=0.8)

        self.clear_all()


# ═════════════════════════════════════════════════════════════════════════════
# Part 2 · 承 — Core Idea
# ═════════════════════════════════════════════════════════════════════════════

class S05_CoreIdeaScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("现在来看STARKs最核心的思想。")
        sec = Text("核心思想", font=FONT, font_size=38, color=WHITE)
        self.play(Write(sec), run_time=0.6)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3), run_time=0.5)

        self.show_sub(
            "一句话概括：证明一个计算是正确的，"
            "等价于证明你知道一个满足特定约束的多项式。"
        )
        core = Text(
            "正确的计算 ↔ 满足约束的多项式",
            font=FONT, font_size=28, color=ACCENT,
        )
        core_box = SurroundingRectangle(core, color=ACCENT, buff=0.15, corner_radius=0.1)
        core_grp = VGroup(core_box, core).next_to(sec, DOWN, buff=0.6)
        self.play(FadeIn(core_grp, shift=UP * 0.2), run_time=1)

        self.show_sub(
            "具体来说，任何计算过程都可以被记录为一张执行轨迹表。"
            "每一行是一步的状态。"
        )
        self.play(core_grp.animate.shift(UP * 0.8).scale(0.8), run_time=0.4)
        headers = ["步骤", "寄存器 A", "寄存器 B"]
        rows = [
            ["0", "1", "1"],
            ["1", "1", "2"],
            ["2", "2", "3"],
            ["3", "3", "5"],
            ["...", "...", "..."],
        ]
        table_grp = VGroup()
        for j, h in enumerate(headers):
            t = Text(h, font=FONT, font_size=16, color=ACCENT)
            t.move_to(LEFT * 2.5 + RIGHT * j * 2.5 + UP * 0.5)
            table_grp.add(t)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                t = Text(val, font=FONT, font_size=16, color=WHITE)
                t.move_to(LEFT * 2.5 + RIGHT * j * 2.5 + DOWN * (i * 0.45))
                table_grp.add(t)
        hline = Line(LEFT * 4 + UP * 0.25, RIGHT * 3 + UP * 0.25, color=MUTED, stroke_width=1)
        table_grp.add(hline)
        table_grp.shift(DOWN * 0.5)
        self.play(FadeIn(table_grp, lag_ratio=0.05), run_time=1.5)

        self.show_sub(
            "我们把这张表编码成一个多项式。"
            "如果这个多项式满足所有约束条件，"
            "就说明原始计算是正确的。"
        )
        poly_text = MathTex(r"P(x) \longleftrightarrow \text{trace}", font_size=30, color=POLY_CLR)
        poly_text.shift(DOWN * 3)
        self.play(Write(poly_text), run_time=0.8)

        self.show_sub(
            "而验证者只需要在几个随机点上检查这个多项式，"
            "就能以极高的概率确认它是否正确。"
        )
        check = Text("随机抽查 → 高概率验证", font=FONT, font_size=22, color=OK_CLR)
        check.next_to(poly_text, DOWN, buff=0.3)
        self.play(FadeIn(check, shift=UP * 0.2), run_time=0.6)

        self.clear_all()


class S06_ArithmetizationScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub(
            "让我们用一个具体的例子来理解。"
            "假设要证明一个类似斐波那契的计算。"
        )
        sec = Text("算术化", font=FONT, font_size=36, color=WHITE)
        self.play(Write(sec), run_time=0.6)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3), run_time=0.4)

        self.show_sub(
            "规则是：a₀等于1，a₁等于1，之后每个数等于前两个数之和。"
        )
        fibs = [1, 1, 2, 3, 5, 8, 13, 21]
        fib_mobs = VGroup()
        for i, v in enumerate(fibs):
            t = MathTex(str(v), font_size=32, color=ACCENT if i < 2 else WHITE)
            fib_mobs.add(t)
        fib_mobs.arrange(RIGHT, buff=0.5).shift(UP * 1)
        labels = VGroup()
        for i, fm in enumerate(fib_mobs):
            l = MathTex(f"a_{{{i}}}", font_size=18, color=MUTED)
            l.next_to(fm, DOWN, buff=0.15)
            labels.add(l)
        self.play(FadeIn(fib_mobs, lag_ratio=0.15), FadeIn(labels, lag_ratio=0.15), run_time=2)

        self.show_sub("我们要证明自己正确地算到了第1000步。")
        ellipsis = MathTex(r"\cdots \; a_{1000}", font_size=28, color=ACCENT)
        ellipsis.next_to(fib_mobs, RIGHT, buff=0.3)
        self.play(FadeIn(ellipsis), run_time=0.6)

        self.show_sub("先来看具体数字。第一个约束：起始值必须是1。")
        box0 = SurroundingRectangle(fib_mobs[0], color=ACCENT, buff=0.1, corner_radius=0.06)
        box1 = SurroundingRectangle(fib_mobs[1], color=ACCENT, buff=0.1, corner_radius=0.06)
        c1 = MathTex(r"a_0 = 1, \; a_1 = 1", font_size=26, color=ACCENT).shift(DOWN * 0.8)
        self.play(Create(box0), Create(box1), Write(c1), run_time=0.8)

        self.show_sub(
            "第二个约束：每一步都满足递推关系。比如a₂等于a₁加a₀，"
            "也就是2等于1加1。a₃等于a₂加a₁，3等于2加1。"
        )
        r1 = MathTex(r"a_2 = a_1 + a_0 \;\Rightarrow\; 2 = 1 + 1", font_size=22, color=WHITE)
        r2 = MathTex(r"a_3 = a_2 + a_1 \;\Rightarrow\; 3 = 2 + 1", font_size=22, color=WHITE)
        recurs = VGroup(r1, r2).arrange(DOWN, buff=0.2, aligned_edge=LEFT).shift(DOWN * 1.8)
        self.play(Write(r1), run_time=0.6)
        self.play(Write(r2), run_time=0.6)

        self.show_sub(
            "现在把这些值编码到一个多项式P上。"
            "P经过点(0,1)，(1,1)，(2,2)，(3,3)，以此类推。"
        )
        self.play(FadeOut(box0, box1, c1, recurs, ellipsis, labels), run_time=0.4)
        self.play(fib_mobs.animate.shift(UP * 0.5).scale(0.7), run_time=0.4)

        axes = Axes(
            x_range=[0, 7, 1], y_range=[0, 22, 5],
            x_length=8, y_length=3.2,
            axis_config={"color": MUTED, "font_size": 14},
            tips=False,
        ).shift(DOWN * 1)
        pts = VGroup()
        for i, v in enumerate(fibs):
            d = Dot(axes.c2p(i, v), color=POLY_CLR, radius=0.06)
            pts.add(d)
        self.play(Create(axes), run_time=0.6)
        self.play(FadeIn(pts, lag_ratio=0.1), run_time=1)

        xs = np.arange(8)
        ys = np.array(fibs, dtype=float)
        coeffs = np.polyfit(xs, ys, 7)
        poly_fn = np.poly1d(coeffs)
        curve = axes.plot(lambda x: float(poly_fn(x)), x_range=[0, 7], color=POLY_CLR)
        self.play(Create(curve), run_time=1)

        self.show_sub(
            "约束条件变成了多项式等式："
            "P在x乘ω²处的值，等于P在x乘ω处加上P在x处的值。"
        )
        constraint = MathTex(
            r"P(\omega^2 \cdot x)", "=",
            r"P(\omega \cdot x)", "+", r"P(x)",
            font_size=28, color=ACCENT,
        ).shift(DOWN * 3.2)
        cbox = SurroundingRectangle(constraint, color=ACCENT, buff=0.12, corner_radius=0.08)
        self.play(Write(constraint), Create(cbox), run_time=1)

        self.show_sub(
            "如果P在整个特殊域上都满足这个等式，"
            "那原始计算就是正确的。"
        )
        checks = VGroup(*[
            MathTex(r"\checkmark", font_size=18, color=OK_CLR).move_to(axes.c2p(i, fibs[i]) + UP * 0.3)
            for i in range(len(fibs))
        ])
        self.play(FadeIn(checks, lag_ratio=0.1), run_time=1)

        self.clear_all()


class S07_PolynomialTestScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("但验证者不会逐点检查——那就跟重新计算一样慢了。")
        cross = Text("逐点检查 ✗", font=FONT, font_size=32, color=FAIL_CLR)
        self.play(FadeIn(cross), run_time=0.6)
        self.play(FadeOut(cross), run_time=0.4)

        self.show_sub("相反，验证者随机挑几个点抽查。")
        axes = Axes(
            x_range=[0, 10, 1], y_range=[0, 10, 2],
            x_length=9, y_length=4.5,
            axis_config={"color": MUTED, "font_size": 14},
            tips=False,
        ).shift(DOWN * 0.3)
        curve = axes.plot(lambda x: 0.05 * x**3 - 0.3 * x**2 + 2 * x + 1,
                          x_range=[0, 10], color=POLY_CLR)
        self.play(Create(axes), Create(curve), run_time=1)

        sample_xs = [2.3, 5.1, 7.8]
        dots = VGroup()
        for sx in sample_xs:
            sy = 0.05 * sx**3 - 0.3 * sx**2 + 2 * sx + 1
            d = Dot(axes.c2p(sx, sy), color=ACCENT, radius=0.1)
            d.set_z_index(10)
            dots.add(d)
        self.play(FadeIn(dots, scale=1.5), run_time=0.8)
        self.play(*[Flash(d, color=ACCENT, num_lines=6, line_length=0.15) for d in dots], run_time=0.6)

        self.show_sub(
            "还记得多项式的指纹性质吗？"
            "如果证明者作弊，他提交的不是正确的多项式，"
            "那么在随机点上暴露的概率极高。"
        )
        sz_lemma = MathTex(
            r"P(\text{cheat}) \leq \frac{d}{|F|}",
            font_size=30, color=ACCENT,
        ).to_edge(RIGHT, buff=0.8).shift(UP * 1.5)
        self.play(Write(sz_lemma), run_time=0.8)

        self.show_sub(
            "每多检查一个点，作弊成功的概率就指数级下降。"
            "这和零知识证明中反复挑战的逻辑一模一样。"
        )
        decay_text = MathTex(
            r"\left(\frac{d}{|F|}\right)^k \to 0",
            font_size=30, color=OK_CLR,
        ).next_to(sz_lemma, DOWN, buff=0.4)
        self.play(Write(decay_text), run_time=0.8)

        self.clear_all()


# ═════════════════════════════════════════════════════════════════════════════
# Part 3 · 转 — The FRI Protocol
# ═════════════════════════════════════════════════════════════════════════════

class S08_FRIIntroScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub(
            "但还有一个关键问题：验证者怎么确认证明者提交的东西"
            "真的是一个低次多项式，而不是随便编的数据？"
        )
        q = Text("低次多项式？还是随机数据？", font=FONT, font_size=28, color=ACCENT)
        self.play(Write(q), run_time=1)

        self.show_sub(
            "这就是FRI协议要解决的问题。"
            "FRI，全称是Fast Reed-Solomon Interactive Oracle Proof of Proximity。"
        )
        self.play(q.animate.scale(0.6).to_edge(UP, buff=0.3), run_time=0.4)
        fri_full = Text(
            "Fast Reed-Solomon\nInteractive Oracle Proof of Proximity",
            font_size=22, color=ACCENT, line_spacing=1.3,
        )
        fri_full.next_to(q, DOWN, buff=0.4)
        self.play(FadeIn(fri_full, shift=UP * 0.2), run_time=0.8)

        self.show_sub(
            "FRI的核心思想，用一句话说："
            "把多项式反复对折，每折一次度数减半，直到折成一个常数。"
        )
        self.play(FadeOut(fri_full), run_time=0.3)
        bars = VGroup()
        for i in range(16):
            b = Rectangle(
                width=0.35, height=1.5 + 0.2 * np.sin(i * 0.8),
                fill_color=POLY_CLR, fill_opacity=0.7, stroke_width=0,
            )
            bars.add(b)
        bars.arrange(RIGHT, buff=0.05).shift(DOWN * 0.5)
        fold_label = Text("N 个值", font=FONT, font_size=18, color=MUTED)
        fold_label.next_to(bars, DOWN, buff=0.2)
        self.play(FadeIn(bars, lag_ratio=0.05), Write(fold_label), run_time=1)

        self.show_sub(
            "就像你把一张写满数字的纸条反复对折。"
            "每折一次，长度减半。"
            "折了log n次之后，纸条只剩一个点，"
            "这一个点你可以直接验证。"
        )
        for step in range(4):
            n = len(bars)
            half = n // 2
            new_bars = VGroup()
            for i in range(half):
                b = Rectangle(
                    width=0.35, height=bars[i].height * 0.8,
                    fill_color=POLY_CLR, fill_opacity=0.7, stroke_width=0,
                )
                new_bars.add(b)
            new_bars.arrange(RIGHT, buff=0.05).move_to(bars.get_center())
            new_label = Text(
                f"N/{2**(step+1)}" if step < 3 else "1",
                font=FONT, font_size=18, color=MUTED,
            )
            new_label.next_to(new_bars, DOWN, buff=0.2)
            self.play(
                ReplacementTransform(bars, new_bars),
                ReplacementTransform(fold_label, new_label),
                run_time=0.6,
            )
            bars = new_bars
            fold_label = new_label
        check = MathTex(r"\checkmark", font_size=48, color=OK_CLR)
        check.next_to(bars, UP, buff=0.3)
        self.play(FadeIn(check, scale=1.5), run_time=0.5)

        self.clear_all()


class S09_FRIStepsScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("FRI 折叠", font=FONT, font_size=36, color=WHITE)
        self.play(Write(sec), run_time=0.6)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3), run_time=0.4)

        self.show_sub(
            "让我们看看FRI的具体步骤。"
            "假设证明者有一个d次多项式f(x)，"
            "他在一个大小为N的域上提交了所有N个点的值。"
        )
        n_bars = 16
        bars = VGroup()
        for i in range(n_bars):
            h = 1.0 + 0.5 * np.sin(i * 0.6 + 1)
            b = Rectangle(
                width=0.4, height=h,
                fill_color=PROVER_CLR, fill_opacity=0.7, stroke_width=0,
            )
            bars.add(b)
        bars.arrange(RIGHT, buff=0.04).shift(UP * 0.3)
        bar_label = MathTex(r"f(x) \text{ on } D,\; |D|=N", font_size=22, color=PROVER_CLR)
        bar_label.next_to(bars, UP, buff=0.2)
        self.play(FadeIn(bars, lag_ratio=0.05), Write(bar_label), run_time=1.2)

        self.show_sub("第一轮折叠：验证者发送一个随机数α。")
        alpha = MathTex(r"\alpha \xleftarrow{R} \mathbb{F}",
                        font_size=24, color=VERIFIER_CLR)
        alpha.to_edge(RIGHT, buff=0.5).shift(UP * 2)
        self.play(Write(alpha), run_time=0.6)

        self.show_sub(
            "证明者计算新多项式f₁(x)，方法是把f的偶数项和奇数项"
            "用α线性组合。新多项式的度数变成了d除以2。"
        )
        half = n_bars // 2
        new_bars = VGroup()
        for i in range(half):
            h = 0.8 + 0.4 * np.sin(i * 0.9 + 0.5)
            b = Rectangle(
                width=0.5, height=h,
                fill_color=SECONDARY, fill_opacity=0.7, stroke_width=0,
            )
            new_bars.add(b)
        new_bars.arrange(RIGHT, buff=0.06).shift(DOWN * 2)
        new_label = MathTex(r"f_1(x),\; \deg = d/2", font_size=22, color=SECONDARY)
        new_label.next_to(new_bars, DOWN, buff=0.2)
        fold_arrow = Arrow(bars.get_bottom(), new_bars.get_top(), buff=0.15,
                           color=ACCENT, stroke_width=2)
        fold_text = Text("折叠", font=FONT, font_size=16, color=ACCENT)
        fold_text.next_to(fold_arrow, RIGHT, buff=0.1)
        self.play(
            GrowArrow(fold_arrow), Write(fold_text),
            FadeIn(new_bars, lag_ratio=0.05), Write(new_label),
            run_time=1.2,
        )

        self.show_sub(
            "第二轮：验证者再发一个随机数β。"
            "证明者再折一次，度数变成d除以4。"
        )
        beta = MathTex(r"\beta \xleftarrow{R} \mathbb{F}",
                       font_size=24, color=VERIFIER_CLR)
        beta.next_to(alpha, DOWN, buff=0.2)
        self.play(Write(beta), run_time=0.4)

        quarter = half // 2
        q_bars = VGroup()
        for i in range(quarter):
            h = 0.6 + 0.3 * np.sin(i * 1.2)
            b = Rectangle(
                width=0.6, height=h,
                fill_color=FIELD_CLR, fill_opacity=0.7, stroke_width=0,
            )
            q_bars.add(b)
        q_bars.arrange(RIGHT, buff=0.08).move_to(new_bars.get_center())
        q_label = MathTex(r"f_2(x),\; \deg = d/4", font_size=22, color=FIELD_CLR)
        q_label.next_to(q_bars, DOWN, buff=0.2)
        self.play(
            FadeOut(fold_arrow, fold_text),
            ReplacementTransform(new_bars, q_bars),
            ReplacementTransform(new_label, q_label),
            run_time=0.8,
        )

        self.show_sub(
            "就这样反复折叠。每一轮，度数减半，域也缩小一半。"
        )
        self.play(FadeOut(q_bars, q_label, bars, bar_label, alpha, beta), run_time=0.5)

        stages = [("N", PROVER_CLR), ("N/2", SECONDARY), ("N/4", FIELD_CLR),
                  ("N/8", ACCENT), ("…", MUTED), ("1", OK_CLR)]
        stage_mobs = VGroup()
        for label, clr in stages:
            r = RoundedRectangle(width=1.2, height=0.6, corner_radius=0.1,
                                 fill_color=clr, fill_opacity=0.2,
                                 stroke_color=clr, stroke_width=2)
            t = Text(label, font_size=20, color=clr)
            t.move_to(r)
            stage_mobs.add(VGroup(r, t))
        stage_mobs.arrange(RIGHT, buff=0.3)
        arrows_between = VGroup()
        for i in range(len(stage_mobs) - 1):
            a = Arrow(
                stage_mobs[i].get_right(), stage_mobs[i + 1].get_left(),
                buff=0.08, color=MUTED, stroke_width=2,
                max_tip_length_to_length_ratio=0.15,
            )
            arrows_between.add(a)
        self.play(FadeIn(stage_mobs, lag_ratio=0.15), run_time=1.5)
        self.play(FadeIn(arrows_between, lag_ratio=0.15), run_time=1)

        self.show_sub(
            "经过log(N)轮之后，多项式变成了一个常数。"
            "常数的验证是平凡的——直接比对就行。"
        )
        box_final = SurroundingRectangle(stage_mobs[-1], color=OK_CLR, buff=0.12, corner_radius=0.08)
        check = MathTex(r"\checkmark", font_size=36, color=OK_CLR)
        check.next_to(stage_mobs[-1], UP, buff=0.2)
        self.play(Create(box_final), FadeIn(check, scale=1.3), run_time=0.6)

        self.show_sub(
            "最后，验证者还会随机抽查几个折叠步骤的一致性。"
            "如果都通过——证明有效！"
        )
        spot_checks = VGroup()
        for i in [0, 2, 3]:
            arrow = Arrow(
                stage_mobs[i].get_bottom() + DOWN * 0.3,
                stage_mobs[i].get_bottom(),
                buff=0.05, color=ACCENT, stroke_width=2,
            )
            spot_checks.add(arrow)
        self.play(FadeIn(spot_checks, lag_ratio=0.2), run_time=0.8)
        valid = Text("证明有效 ✓", font=FONT, font_size=28, color=OK_CLR)
        valid.shift(DOWN * 2)
        self.play(FadeIn(valid, scale=1.2), run_time=0.6)

        self.clear_all()


class S10_WhyTransparentScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("现在你可能会问：这和SNARKs有什么区别？")
        sec = Text("SNARKs vs STARKs", font_size=34, color=WHITE)
        self.play(Write(sec), run_time=0.6)
        self.play(sec.animate.scale(0.65).to_edge(UP, buff=0.3), run_time=0.4)

        snark_col = VGroup(
            Text("zk-SNARKs", font_size=24, color=PROVER_CLR),
            RoundedRectangle(width=4, height=3.5, corner_radius=0.15,
                             fill_color=CARD_BG, fill_opacity=0.9,
                             stroke_color=PROVER_CLR, stroke_width=2),
        ).arrange(DOWN, buff=0.15)
        stark_col = VGroup(
            Text("zk-STARKs", font_size=24, color=OK_CLR),
            RoundedRectangle(width=4, height=3.5, corner_radius=0.15,
                             fill_color=CARD_BG, fill_opacity=0.9,
                             stroke_color=OK_CLR, stroke_width=2),
        ).arrange(DOWN, buff=0.15)
        cols = VGroup(snark_col, stark_col).arrange(RIGHT, buff=0.8).shift(DOWN * 0.3)

        snark_items = VGroup(
            Text("可信设置: 需要 ⚠️", font=FONT, font_size=16, color=FAIL_CLR),
            Text("基于: 椭圆曲线", font=FONT, font_size=16, color=WHITE),
            Text("抗量子: ✗", font=FONT, font_size=16, color=FAIL_CLR),
            Text("证明大小: 极小", font=FONT, font_size=16, color=OK_CLR),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to(snark_col[1])

        stark_items = VGroup(
            Text("可信设置: 不需要 ✓", font=FONT, font_size=16, color=OK_CLR),
            Text("基于: 哈希函数", font=FONT, font_size=16, color=WHITE),
            Text("抗量子: ✓", font=FONT, font_size=16, color=OK_CLR),
            Text("证明大小: 较大", font=FONT, font_size=16, color=SECONDARY),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to(stark_col[1])

        self.play(FadeIn(cols), run_time=0.6)

        self.show_sub(
            "最关键的区别是：SNARKs需要一个可信设置。"
            "在初始化时，需要生成一些秘密参数，然后销毁。"
            "如果有人偷偷保留了这些参数，整个系统的安全性就崩溃了。"
        )
        self.play(FadeIn(snark_items, lag_ratio=0.2), run_time=1.5)

        self.show_sub(
            "而STARKs完全不需要可信设置。它只依赖哈希函数。"
            "所有参数都是公开透明的，没有任何秘密。"
        )
        self.play(FadeIn(stark_items, lag_ratio=0.2), run_time=1.5)

        self.show_sub(
            "还有一个重要优势：STARKs是抗量子的。"
            "因为它基于哈希函数，而不是椭圆曲线。"
            "即使未来量子计算机出现，STARKs依然安全。"
        )
        shield = VGroup(
            Polygon(
                UP * 0.6, LEFT * 0.45 + UP * 0.3, LEFT * 0.45 + DOWN * 0.15,
                DOWN * 0.45, RIGHT * 0.45 + DOWN * 0.15, RIGHT * 0.45 + UP * 0.3,
                fill_color=OK_CLR, fill_opacity=0.3,
                stroke_color=OK_CLR, stroke_width=2,
            ),
            Text("Q", font_size=20, color=OK_CLR),
        )
        shield.next_to(stark_col, DOWN, buff=0.2)
        self.play(FadeIn(shield, scale=1.3), run_time=0.6)

        self.clear_all()


# ═════════════════════════════════════════════════════════════════════════════
# Part 4 · 合 — Putting It Together
# ═════════════════════════════════════════════════════════════════════════════

class S11_FullPipelineScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("让我们把整条流水线串起来。")
        sec = Text("STARK 全流程", font=FONT, font_size=36, color=WHITE)
        self.play(Write(sec), run_time=0.6)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3), run_time=0.4)

        stages = [
            ("计算", PROVER_CLR),
            ("执行轨迹", SECONDARY),
            ("多项式约束", POLY_CLR),
            ("FRI 证明", FIELD_CLR),
            ("验证", OK_CLR),
        ]
        boxes = VGroup()
        for label, clr in stages:
            r = RoundedRectangle(width=1.8, height=0.8, corner_radius=0.12,
                                 fill_color=CARD_BG, fill_opacity=0.9,
                                 stroke_color=clr, stroke_width=2)
            t = Text(label, font=FONT, font_size=16, color=clr)
            t.move_to(r)
            boxes.add(VGroup(r, t))
        boxes.arrange(RIGHT, buff=0.4).shift(UP * 0.5)
        arrows = VGroup()
        for i in range(len(boxes) - 1):
            a = Arrow(boxes[i].get_right(), boxes[i + 1].get_left(),
                      buff=0.08, color=MUTED, stroke_width=2,
                      max_tip_length_to_length_ratio=0.15)
            arrows.add(a)

        self.show_sub(
            "首先，你有一个计算任务。把它的执行轨迹记录下来。"
        )
        self.play(FadeIn(boxes[0], shift=UP * 0.3), run_time=0.5)
        self.play(GrowArrow(arrows[0]), FadeIn(boxes[1], shift=UP * 0.3), run_time=0.5)

        self.show_sub("然后，通过算术化，把轨迹编码成多项式和约束。")
        self.play(GrowArrow(arrows[1]), FadeIn(boxes[2], shift=UP * 0.3), run_time=0.5)

        self.show_sub("接着，用FRI协议证明这个多项式是低次的。")
        self.play(GrowArrow(arrows[2]), FadeIn(boxes[3], shift=UP * 0.3), run_time=0.5)

        self.show_sub(
            "最终生成一个简短的证明。"
            "证明者可能花了几分钟生成证明，"
            "但验证者只需要几毫秒就能验证。"
        )
        self.play(GrowArrow(arrows[3]), FadeIn(boxes[4], shift=UP * 0.3), run_time=0.5)

        time_comp = VGroup(
            VGroup(
                Text("证明者", font=FONT, font_size=18, color=PROVER_CLR),
                Text("~ 分钟", font=FONT, font_size=18, color=PROVER_CLR),
            ).arrange(RIGHT, buff=0.3),
            VGroup(
                Text("验证者", font=FONT, font_size=18, color=VERIFIER_CLR),
                Text("~ 毫秒 ⚡", font=FONT, font_size=18, color=VERIFIER_CLR),
            ).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, buff=0.3).shift(DOWN * 1.5)
        self.play(FadeIn(time_comp, shift=UP * 0.2), run_time=0.8)

        self.show_sub(
            "而且证明的大小是对数级的——"
            "计算量翻10倍，证明只长了一点点。"
        )
        log_eq = MathTex(
            r"\text{proof size} = O(\log^2 n)",
            font_size=26, color=ACCENT,
        ).shift(DOWN * 2.8)
        self.play(Write(log_eq), run_time=0.8)

        self.clear_all()


class S12_ApplicationScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("应用", font=FONT, font_size=38, color=WHITE)
        self.play(Write(sec), run_time=0.6)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3), run_time=0.4)

        self.show_sub("ZK-STARKs已经在改变真实世界了。")

        apps = [
            ("StarkNet", "以太坊 L2 扩展\n数千笔交易压缩成一个证明", PROVER_CLR),
            ("Cairo 语言", "可证明程序\n每步执行自动生成证明", SECONDARY),
            ("可验证计算", "AI 推理 · 科学模拟 · 选举\n任何需要信任的计算", ACCENT),
        ]
        cards = VGroup()
        for name, desc, clr in apps:
            card = RoundedRectangle(width=3.2, height=2.8, corner_radius=0.15,
                                    fill_color=CARD_BG, fill_opacity=0.9,
                                    stroke_color=clr, stroke_width=2)
            n = Text(name, font_size=22, color=clr)
            d = Text(desc, font=FONT, font_size=14, color=WHITE, line_spacing=1.3)
            VGroup(n, d).arrange(DOWN, buff=0.35).move_to(card)
            cards.add(VGroup(card, n, d))
        cards.arrange(RIGHT, buff=0.35).next_to(sec, DOWN, buff=0.6)

        self.show_sub(
            "在以太坊生态中，StarkNet用STARKs把数千笔交易"
            "压缩成一个证明，提交到主链。"
            "这让以太坊的吞吐量提升了几百倍，而安全性丝毫不减。"
        )
        self.play(FadeIn(cards[0], shift=UP * 0.4), run_time=0.8)

        self.show_sub(
            "Starkware开发了一门叫Cairo的编程语言。"
            "用Cairo写的程序，每一步执行都自动生成STARK证明。"
        )
        self.play(FadeIn(cards[1], shift=UP * 0.4), run_time=0.8)

        self.show_sub(
            "更远的未来，可验证计算可以应用到AI推理、科学模拟、甚至选举计票。"
            "任何需要信任的计算都可以被证明。"
        )
        self.play(FadeIn(cards[2], shift=UP * 0.4), run_time=0.8)

        self.clear_all()


class S13_OutroScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("让我们回到开头那个场景。")
        auditor = VGroup(
            Circle(radius=0.3, color=VERIFIER_CLR, stroke_width=3),
            Text("审计官", font=FONT, font_size=14, color=VERIFIER_CLR),
        ).arrange(DOWN, buff=0.1).shift(LEFT * 3)
        server = RoundedRectangle(
            width=1.8, height=1.2, corner_radius=0.12,
            fill_color=CARD_BG, fill_opacity=0.9,
            stroke_color=PROVER_CLR, stroke_width=2,
        ).shift(RIGHT * 3)
        srv_t = Text("超级计算机", font=FONT, font_size=14, color=PROVER_CLR)
        srv_t.next_to(server, UP, buff=0.1)
        self.play(FadeIn(auditor), FadeIn(server, srv_t), run_time=0.8)

        self.show_sub(
            "超级计算机说它检查了100亿笔交易。"
            "现在你不需要盲目信任它。"
        )
        proof_box = RoundedRectangle(
            width=1.2, height=0.5, corner_radius=0.08,
            fill_color=ACCENT, fill_opacity=0.2,
            stroke_color=ACCENT, stroke_width=2,
        )
        proof_t = Text("STARK 证明", font=FONT, font_size=12, color=ACCENT)
        proof_t.move_to(proof_box)
        proof_grp = VGroup(proof_box, proof_t)
        proof_grp.next_to(server, DOWN, buff=0.3)
        arrow = Arrow(proof_grp.get_left(), auditor.get_right(), buff=0.15,
                      color=ACCENT, stroke_width=2)
        self.play(FadeIn(proof_grp), GrowArrow(arrow), run_time=1)

        self.show_sub(
            "它只需要附上一个STARK证明。"
            "你在几毫秒内就能验证这个证明——"
            "如果验证通过，数学保证了计算一定是正确的。"
        )
        check = Text("✓ 验证通过", font=FONT, font_size=24, color=OK_CLR)
        check.next_to(auditor, DOWN, buff=0.4)
        self.play(FadeIn(check, scale=1.3), run_time=0.6)

        self.show_sub("不需要信任任何人，不需要任何秘密。")
        self.play(FadeOut(auditor, server, srv_t, proof_grp, arrow, check), run_time=0.6)

        self.show_sub(
            "ZK-STARKs让我们第一次拥有了这样的能力："
            "用数学取代信任，用证明取代权威。"
        )
        final = Text(
            "用数学取代信任\n用证明取代权威",
            font=FONT, font_size=40, color=ACCENT, line_spacing=1.6,
        )
        self.play(Write(final), run_time=2)
        self.wait(2)

        self.hide_sub()
        coda = Text("这就是可验证计算的美。", font=FONT, font_size=28, color=MUTED)
        coda.next_to(final, DOWN, buff=0.6)
        self.play(FadeIn(coda, shift=UP * 0.2), run_time=1)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=2)
        self._save_stamps()
