"""Euler's Identity -- 5-minute pop-sci Manim animation."""

from manim import *
import numpy as np
from base import (
    SubtitleMixin, BG, ACCENT, OK_CLR, FAIL_CLR, MUTED, CARD_BG, FONT,
)


class S01_HookScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("数学家们投票选出了人类历史上最美丽的公式。\n获胜的不是什么复杂的定理，而是一个极其简洁的等式。")
        title = Text("最美丽的公式", font=FONT, font_size=48, color=ACCENT)
        self.play(Write(title), run_time=1.5)

        self.show_sub("它只用了五个数字和三种运算，\n却把数学中最重要的五个常数联系在了一起。")
        consts = VGroup(*[
            MathTex(s, font_size=52, color=c)
            for s, c in [("e", "#e74c3c"), ("i", "#3498db"), (r"\pi", "#2ecc71"), ("1", "#e67e22"), ("0", "#9b59b6")]
        ]).arrange(RIGHT, buff=0.8)
        self.play(FadeOut(title), run_time=0.5)
        for c in consts:
            self.play(FadeIn(c, scale=1.5), run_time=0.4)

        self.clear_all()


class S02_TitleScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("这就是欧拉恒等式。")
        eq = MathTex(r"e^{i\pi} + 1 = 0", font_size=72, color=ACCENT)
        self.play(Write(eq), run_time=2.5)
        self.wait(1)

        self.clear_all()


class S03_IngredientsScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("让我们先认识一下这五位主角。\n零，加法的起点。一，乘法的起点。\n圆周率π，圆的灵魂。自然常数e，增长的本质。\n虚数单位i，它满足i的平方等于负一。")

        cards_data = [
            ("0", "加法的起点", "#9b59b6"),
            ("1", "乘法的起点", "#e67e22"),
            (r"\pi", "圆的灵魂", "#2ecc71"),
            ("e", "增长的本质", "#e74c3c"),
            ("i", "代数的扩展", "#3498db"),
        ]
        cards = VGroup()
        for sym, desc, clr in cards_data:
            card = RoundedRectangle(width=2.0, height=2.5, corner_radius=0.15,
                                    fill_color=CARD_BG, fill_opacity=0.9,
                                    stroke_color=clr, stroke_width=2)
            s = MathTex(sym, font_size=44, color=clr)
            d = Text(desc, font=FONT, font_size=14, color=MUTED)
            VGroup(s, d).arrange(DOWN, buff=0.4).move_to(card)
            cards.add(VGroup(card, s, d))
        cards.arrange(RIGHT, buff=0.25).scale_to_fit_width(12)

        for card in cards:
            self.play(FadeIn(card, shift=UP * 0.3), run_time=0.5)

        self.show_sub("这五个数分别来自数学的不同分支，看似毫无关联。\n欧拉恒等式说的是：它们之间存在一个惊人的等式。")
        self.play(cards.animate.scale(0.5).shift(UP * 2), run_time=1)
        eq = MathTex(r"e^{i\pi} + 1 = 0", font_size=48, color=ACCENT)
        self.play(Write(eq), run_time=1.5)

        self.clear_all()


class S04_ComplexPlaneScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("要理解这个等式，我们先要理解虚数i到底意味着什么。")
        plane = NumberPlane(
            x_range=[-3, 3], y_range=[-3, 3],
            x_length=6, y_length=6,
            background_line_style={"stroke_color": MUTED, "stroke_opacity": 0.3},
        )
        x_label = MathTex(r"\text{Re}", font_size=22, color=MUTED).next_to(plane.x_axis, RIGHT)
        y_label = MathTex(r"\text{Im}", font_size=22, color=MUTED).next_to(plane.y_axis, UP)
        self.play(Create(plane), Write(x_label), Write(y_label), run_time=1.5)

        self.show_sub("乘以负一意味着翻转方向。\n乘以i呢？i的平方等于负一，所以乘两次i等于翻转。\n那乘一次i就是旋转九十度。")
        dot1 = Dot(plane.c2p(1, 0), color="#e74c3c", radius=0.12)
        lbl1 = MathTex("1", font_size=22, color="#e74c3c").next_to(dot1, DR, buff=0.1)
        self.play(FadeIn(dot1, lbl1), run_time=0.5)

        dot_i = Dot(plane.c2p(0, 1), color="#3498db", radius=0.12)
        lbl_i = MathTex("i", font_size=22, color="#3498db").next_to(dot_i, UL, buff=0.1)
        arc1 = Arc(radius=1.0 * plane.x_length / 6, start_angle=0, angle=PI / 2,
                    color=ACCENT, stroke_width=2).move_arc_center_to(plane.c2p(0, 0))
        self.play(Create(arc1), FadeIn(dot_i, lbl_i), run_time=1)

        dot_neg = Dot(plane.c2p(-1, 0), color="#e67e22", radius=0.12)
        lbl_neg = MathTex("-1", font_size=22, color="#e67e22").next_to(dot_neg, DL, buff=0.1)
        arc2 = Arc(radius=1.0 * plane.x_length / 6, start_angle=PI / 2, angle=PI / 2,
                    color=ACCENT, stroke_width=2).move_arc_center_to(plane.c2p(0, 0))
        self.play(Create(arc2), FadeIn(dot_neg, lbl_neg), run_time=1)

        self.show_sub("这就是复平面：横轴是实数，纵轴是虚数。\n乘以i就是逆时针旋转九十度。")
        rotate_label = Text("× i = 旋转 90°", font=FONT, font_size=24, color=ACCENT)
        rotate_label.to_edge(DOWN, buff=1.5)
        self.play(Write(rotate_label), run_time=1)

        self.clear_all()


class S05_EulerFormulaScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("现在登场的是欧拉公式：\ne的iθ次方等于cosθ加上i乘以sinθ。")
        formula = MathTex(r"e^{i\theta} = \cos\theta + i\sin\theta", font_size=44, color=WHITE)
        formula.to_edge(UP, buff=1)
        self.play(Write(formula), run_time=2)

        self.show_sub("当θ从零开始增大，\ne的iθ次方在复平面的单位圆上移动。\nθ就是旋转的角度。")
        circle = Circle(radius=2, color=MUTED, stroke_width=2)
        dot = Dot(color=ACCENT, radius=0.1).move_to(RIGHT * 2)
        angle = ValueTracker(0)

        def dot_updater(d):
            a = angle.get_value()
            d.move_to(2 * np.array([np.cos(a), np.sin(a), 0]))

        dot.add_updater(dot_updater)
        self.play(Create(circle), FadeIn(dot), run_time=1)
        self.play(angle.animate.set_value(TAU), run_time=4, rate_func=linear)
        dot.remove_updater(dot_updater)

        self.show_sub("欧拉公式把指数函数和三角函数，\n通过虚数i，完美地统一在了一起。")
        box = SurroundingRectangle(formula, color=ACCENT, buff=0.2, corner_radius=0.1)
        self.play(Create(box), run_time=0.8)

        self.clear_all()


class S06_PlugInPiScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("现在让我们把θ设为π。\ncosπ等于负一，sinπ等于零。")
        eq1 = MathTex(r"e^{i\pi} = \cos\pi + i\sin\pi", font_size=40, color=WHITE)
        eq2 = MathTex(r"= -1 + i \cdot 0", font_size=40, color=WHITE)
        eq3 = MathTex(r"= -1", font_size=40, color=ACCENT)
        eqs = VGroup(eq1, eq2, eq3).arrange(DOWN, buff=0.5).center()

        self.play(Write(eq1), run_time=1.5)
        self.play(Write(eq2), run_time=1)
        self.play(Write(eq3), run_time=0.8)

        self.show_sub("所以e的iπ次方等于负一。\n两边加一，就得到了欧拉恒等式。")
        final = MathTex(r"e^{i\pi} + 1 = 0", font_size=64, color=ACCENT)
        self.play(FadeOut(eqs), run_time=0.5)
        self.play(Write(final), run_time=2)
        box = SurroundingRectangle(final, color=OK_CLR, buff=0.25, corner_radius=0.12)
        self.play(Create(box), run_time=0.8)

        self.clear_all()


class S07_BeautyScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("为什么说它是最美丽的等式？\n因为它用了五个最基本的常数和三种最基本的运算，\n一个等式，把整个数学大厦的地基连在了一起。")

        items = [
            ("e", "分析", "#e74c3c"), ("i", "代数", "#3498db"), (r"\pi", "几何", "#2ecc71"),
            ("1", "算术", "#e67e22"), ("0", "基础", "#9b59b6"),
        ]
        consts = VGroup()
        for sym, field, clr in items:
            s = MathTex(sym, font_size=40, color=clr)
            f = Text(field, font=FONT, font_size=16, color=MUTED)
            VGroup(s, f).arrange(DOWN, buff=0.2)
            consts.add(VGroup(s, f))
        consts.arrange(RIGHT, buff=0.8).shift(UP * 1)
        self.play(FadeIn(consts, lag_ratio=0.2), run_time=2)

        ops = Text("+ , × , ^    →    = 0", font_size=28, color=ACCENT)
        ops.next_to(consts, DOWN, buff=0.8)
        self.play(Write(ops), run_time=1)

        self.clear_all()


class S08_OutroScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("简洁即美。\n在数学的世界里，最深刻的真理往往藏在最简单的形式之中。")
        eq = MathTex(r"e^{i\pi} + 1 = 0", font_size=80, color=ACCENT)
        self.play(Write(eq), run_time=2.5)

        self.show_sub("这就是欧拉恒等式的美。")
        self.wait(1)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=2)
        self._save_stamps()
