"""Euler's Identity -- 5-minute pop-sci Manim animation (polished)."""

from manim import *
import numpy as np
from base import (
    SubtitleMixin, BG, ACCENT, OK_CLR, FAIL_CLR, MUTED, CARD_BG, FONT,
)

# Scene-specific palette
E_CLR = "#e74c3c"
I_CLR = "#3498db"
PI_CLR = "#2ecc71"
ONE_CLR = "#e67e22"
ZERO_CLR = "#9b59b6"
GRID_CLR = "#2c3e50"


class S01_HookScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("数学家们投票选出了人类历史上最美丽的公式。\n获胜的不是什么复杂的定理，而是一个极其简洁的等式。")

        # Cinematic text reveal with glow
        top = Text("人类历史上", font=FONT, font_size=28, color=MUTED)
        title = Text("最美丽的公式", font=FONT, font_size=56, color=ACCENT)
        grp = VGroup(top, title).arrange(DOWN, buff=0.3).shift(UP * 0.5)
        self.play(FadeIn(top, shift=DOWN * 0.2), run_time=0.8)
        self.play(Write(title), run_time=1.5)
        # Soft glow ring
        glow = Circle(radius=2.5, color=ACCENT, stroke_width=1, stroke_opacity=0.3)
        self.play(Create(glow), run_time=1)
        self.pad_segment()

        self.show_sub("它只用了五个数字和三种运算，\n却把数学中最重要的五个常数联系在了一起。")
        self.play(FadeOut(top, glow), title.animate.scale(0.5).to_edge(UP, buff=0.5), run_time=0.8)

        # Five constants with staggered entrance + underline
        data = [("e", E_CLR), ("i", I_CLR), (r"\pi", PI_CLR), ("1", ONE_CLR), ("0", ZERO_CLR)]
        consts = VGroup()
        for sym, clr in data:
            m = MathTex(sym, font_size=64, color=clr)
            line = Line(LEFT * 0.3, RIGHT * 0.3, color=clr, stroke_width=2).next_to(m, DOWN, buff=0.1)
            consts.add(VGroup(m, line))
        consts.arrange(RIGHT, buff=1.0)

        for i, c in enumerate(consts):
            self.play(FadeIn(c, shift=UP * 0.4, scale=0.7), run_time=0.35)
        self.pad_segment()

        self.clear_all()


class S02_TitleScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("这就是欧拉恒等式。")
        # Formula with color-coded parts
        eq = MathTex("e", "^{", "i", r"\pi", "}", "+", "1", "=", "0", font_size=80)
        eq[0].set_color(E_CLR)      # e
        eq[2].set_color(I_CLR)      # i
        eq[3].set_color(PI_CLR)     # pi
        eq[6].set_color(ONE_CLR)    # 1
        eq[8].set_color(ZERO_CLR)   # 0
        self.play(Write(eq), run_time=2.5)

        # Decorative frame
        frame = SurroundingRectangle(eq, color=ACCENT, buff=0.4, corner_radius=0.15, stroke_width=1.5)
        self.play(Create(frame), run_time=0.8)
        self.pad_segment()

        self.clear_all()


class S03_IngredientsScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("让我们先认识一下这五位主角。\n零，加法的起点。一，乘法的起点。\n圆周率π，圆的灵魂。自然常数e，增长的本质。\n虚数单位i，它满足i的平方等于负一。")

        cards_data = [
            ("0", "加法的起点", ZERO_CLR, "算术"),
            ("1", "乘法的起点", ONE_CLR, "算术"),
            (r"\pi", "圆的灵魂", PI_CLR, "几何"),
            ("e", "增长的本质", E_CLR, "分析"),
            ("i", "代数的扩展", I_CLR, "代数"),
        ]
        cards = VGroup()
        for sym, desc, clr, field in cards_data:
            card = RoundedRectangle(
                width=2.2, height=3.0, corner_radius=0.18,
                fill_color=CARD_BG, fill_opacity=0.95,
                stroke_color=clr, stroke_width=2,
            )
            # Top: field tag
            tag = Text(field, font=FONT, font_size=12, color=clr)
            tag_bg = RoundedRectangle(
                width=tag.width + 0.3, height=tag.height + 0.15, corner_radius=0.06,
                fill_color=clr, fill_opacity=0.12, stroke_width=0,
            )
            tag.move_to(tag_bg)
            tag_grp = VGroup(tag_bg, tag)
            # Symbol
            s = MathTex(sym, font_size=52, color=clr)
            # Description
            d = Text(desc, font=FONT, font_size=13, color=MUTED)
            # Separator line
            sep = Line(LEFT * 0.6, RIGHT * 0.6, color=clr, stroke_width=1, stroke_opacity=0.4)
            content = VGroup(tag_grp, s, sep, d).arrange(DOWN, buff=0.25)
            content.move_to(card)
            cards.add(VGroup(card, content))

        cards.arrange(RIGHT, buff=0.2).scale_to_fit_width(13)

        for card in cards:
            self.play(FadeIn(card, shift=UP * 0.4), run_time=0.45)
        self.pad_segment()

        self.show_sub("这五个数分别来自数学的不同分支，看似毫无关联。\n欧拉恒等式说的是：它们之间存在一个惊人的等式。")
        self.play(cards.animate.scale(0.4).to_edge(UP, buff=0.4), run_time=1)

        eq = MathTex("e", "^{", "i", r"\pi", "}", "+", "1", "=", "0", font_size=56)
        eq[0].set_color(E_CLR)
        eq[2].set_color(I_CLR)
        eq[3].set_color(PI_CLR)
        eq[6].set_color(ONE_CLR)
        eq[8].set_color(ZERO_CLR)
        self.play(Write(eq), run_time=1.5)
        self.pad_segment()

        self.clear_all()


class S04_ComplexPlaneScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("要理解这个等式，我们先要理解虚数i到底意味着什么。")

        # Elegant complex plane
        plane = NumberPlane(
            x_range=[-2.5, 2.5, 1], y_range=[-2.5, 2.5, 1],
            x_length=7, y_length=7,
            background_line_style={"stroke_color": GRID_CLR, "stroke_opacity": 0.4, "stroke_width": 1},
            axis_config={"color": MUTED, "stroke_width": 2, "include_numbers": True,
                         "font_size": 18, "numbers_to_exclude": [0]},
        ).shift(RIGHT * 0.5)
        re_lbl = Text("Re", font_size=20, color=MUTED).next_to(plane.x_axis, DR, buff=0.1)
        im_lbl = Text("Im", font_size=20, color=MUTED).next_to(plane.y_axis, UL, buff=0.1)
        origin_lbl = MathTex("0", font_size=18, color=MUTED).next_to(plane.c2p(0, 0), DL, buff=0.1)
        self.play(Create(plane, run_time=1.5), Write(re_lbl), Write(im_lbl), FadeIn(origin_lbl))
        self.pad_segment()

        self.show_sub("乘以负一意味着翻转方向。\n乘以i呢？i的平方等于负一，所以乘两次i等于翻转。\n那乘一次i就是旋转九十度。")

        unit = plane.x_length / 5  # 1 unit in screen coords
        # Dot at 1
        d1 = Dot(plane.c2p(1, 0), color=E_CLR, radius=0.1, z_index=5)
        l1 = MathTex("1", font_size=24, color=E_CLR).next_to(d1, DR, buff=0.12)
        self.play(FadeIn(d1, l1, scale=1.3), run_time=0.5)

        # Rotate to i (90 degrees)
        d_i = Dot(plane.c2p(0, 1), color=I_CLR, radius=0.1, z_index=5)
        l_i = MathTex("i", font_size=24, color=I_CLR).next_to(d_i, UL, buff=0.12)
        arc1 = Arc(radius=unit, start_angle=0, angle=PI / 2, color=ACCENT,
                    stroke_width=2.5, arc_center=plane.c2p(0, 0))
        lbl_x_i = MathTex(r"\times i", font_size=18, color=ACCENT).move_to(
            plane.c2p(0, 0) + 1.4 * unit * np.array([np.cos(PI / 4), np.sin(PI / 4), 0]))
        self.play(Create(arc1), FadeIn(d_i, l_i), Write(lbl_x_i), run_time=1.2)

        # Rotate to -1 (another 90 degrees)
        d_neg = Dot(plane.c2p(-1, 0), color=ONE_CLR, radius=0.1, z_index=5)
        l_neg = MathTex("-1", font_size=24, color=ONE_CLR).next_to(d_neg, DL, buff=0.12)
        arc2 = Arc(radius=unit, start_angle=PI / 2, angle=PI / 2, color=ACCENT,
                    stroke_width=2.5, arc_center=plane.c2p(0, 0))
        lbl_x_i2 = MathTex(r"\times i", font_size=18, color=ACCENT).move_to(
            plane.c2p(0, 0) + 1.4 * unit * np.array([np.cos(3 * PI / 4), np.sin(3 * PI / 4), 0]))
        self.play(Create(arc2), FadeIn(d_neg, l_neg), Write(lbl_x_i2), run_time=1.2)

        # Rotate to -i (another 90)
        d_ni = Dot(plane.c2p(0, -1), color=PI_CLR, radius=0.1, z_index=5)
        l_ni = MathTex("-i", font_size=24, color=PI_CLR).next_to(d_ni, DR, buff=0.12)
        arc3 = Arc(radius=unit, start_angle=PI, angle=PI / 2, color=ACCENT,
                    stroke_width=2.5, arc_center=plane.c2p(0, 0))
        self.play(Create(arc3), FadeIn(d_ni, l_ni), run_time=0.8)
        self.pad_segment()

        self.show_sub("这就是复平面：横轴是实数，纵轴是虚数。\n乘以i就是逆时针旋转九十度。")
        # Summary badge
        badge = VGroup(
            RoundedRectangle(width=3.5, height=0.7, corner_radius=0.12,
                             fill_color=CARD_BG, fill_opacity=0.9,
                             stroke_color=ACCENT, stroke_width=1.5),
            MathTex(r"\times\, i \;=\; ", font_size=24, color=WHITE),
            Text("逆时针旋转 90°", font=FONT, font_size=18, color=ACCENT),
        )
        badge[1:].arrange(RIGHT, buff=0.15).move_to(badge[0])
        badge.to_corner(UL, buff=0.5)
        self.play(FadeIn(badge, shift=DOWN * 0.2), run_time=0.8)
        self.pad_segment()

        self.clear_all()


class S05_EulerFormulaScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("现在登场的是欧拉公式：\ne的iθ次方等于cosθ加上i乘以sinθ。")

        # Title bar
        title = Text("欧拉公式", font=FONT, font_size=28, color=MUTED).to_edge(UP, buff=0.4)
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.4)

        formula = MathTex(r"e^{i\theta}", "=", r"\cos\theta", "+", r"i\sin\theta", font_size=48)
        formula[0].set_color(ACCENT)
        formula[2].set_color(E_CLR)
        formula[4].set_color(I_CLR)
        formula.next_to(title, DOWN, buff=0.5)
        self.play(Write(formula), run_time=2)
        self.pad_segment()

        self.show_sub("当θ从零开始增大，\ne的iθ次方在复平面的单位圆上移动。\nθ就是旋转的角度。")

        # Unit circle with tracing dot
        plane_grp = VGroup()
        circle = Circle(radius=2.0, color=MUTED, stroke_width=1.5).shift(DOWN * 0.3)
        axes_h = Line(LEFT * 2.3, RIGHT * 2.3, color=MUTED, stroke_width=1, stroke_opacity=0.5).shift(DOWN * 0.3)
        axes_v = Line(DOWN * 2.3, UP * 2.3, color=MUTED, stroke_width=1, stroke_opacity=0.5).shift(DOWN * 0.3)
        center = circle.get_center()
        plane_grp.add(axes_h, axes_v, circle)
        self.play(Create(plane_grp), run_time=1)

        dot = Dot(color=ACCENT, radius=0.1, z_index=5)
        dot.move_to(center + RIGHT * 2)
        trace = TracedPath(dot.get_center, stroke_color=ACCENT, stroke_width=2.5, stroke_opacity=0.6)
        self.add(trace)
        self.play(FadeIn(dot), run_time=0.3)

        angle = ValueTracker(0)
        # Radius line + angle arc
        radius_line = always_redraw(lambda: Line(
            center, center + 2 * np.array([np.cos(angle.get_value()), np.sin(angle.get_value()), 0]),
            color=ACCENT, stroke_width=1.5, stroke_opacity=0.6,
        ))
        # Cos/sin projections
        cos_line = always_redraw(lambda: DashedLine(
            center + 2 * np.array([np.cos(angle.get_value()), np.sin(angle.get_value()), 0]),
            center + 2 * np.array([np.cos(angle.get_value()), 0, 0]),
            color=E_CLR, stroke_width=1.5, dash_length=0.08,
        ))
        sin_line = always_redraw(lambda: DashedLine(
            center + 2 * np.array([np.cos(angle.get_value()), np.sin(angle.get_value()), 0]),
            center + 2 * np.array([0, np.sin(angle.get_value()), 0]),
            color=I_CLR, stroke_width=1.5, dash_length=0.08,
        ))
        self.add(radius_line, cos_line, sin_line)

        dot.add_updater(lambda d: d.move_to(
            center + 2 * np.array([np.cos(angle.get_value()), np.sin(angle.get_value()), 0])))

        self.play(angle.animate.set_value(TAU), run_time=4, rate_func=linear)
        dot.clear_updaters()
        self.remove(trace, radius_line, cos_line, sin_line)
        self.pad_segment()

        self.show_sub("欧拉公式把指数函数和三角函数，\n通过虚数i，完美地统一在了一起。")
        box = SurroundingRectangle(formula, color=ACCENT, buff=0.25, corner_radius=0.12, stroke_width=2)
        self.play(Create(box), run_time=0.8)
        self.pad_segment()

        self.clear_all()


class S06_PlugInPiScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("现在让我们把θ设为π。\ncosπ等于负一，sinπ等于零。")

        # Step-by-step derivation with alignment
        step_label = Text("代入 θ = π", font=FONT, font_size=22, color=MUTED).to_edge(UP, buff=0.5)
        self.play(FadeIn(step_label), run_time=0.4)

        eq1 = MathTex(r"e^{i\pi}", "=", r"\cos\pi", "+", r"i\sin\pi", font_size=42)
        eq1[0].set_color(ACCENT)
        eq2 = MathTex(r"e^{i\pi}", "=", r"(-1)", "+", r"i \cdot 0", font_size=42)
        eq2[0].set_color(ACCENT)
        eq2[2].set_color(E_CLR)
        eq3 = MathTex(r"e^{i\pi}", "=", "-1", font_size=42)
        eq3[0].set_color(ACCENT)
        eq3[2].set_color(E_CLR)

        for eq in [eq1, eq2, eq3]:
            eq.shift(UP * 0.3)

        self.play(Write(eq1), run_time=1.5)
        self.wait(0.8)
        self.play(TransformMatchingTex(eq1, eq2), run_time=1)
        self.wait(0.6)
        self.play(TransformMatchingTex(eq2, eq3), run_time=0.8)
        self.pad_segment()

        self.show_sub("所以e的iπ次方等于负一。\n两边加一，就得到了欧拉恒等式。")
        self.play(FadeOut(step_label, eq3), run_time=0.5)

        final = MathTex("e", "^{", "i", r"\pi", "}", "+", "1", "=", "0", font_size=72)
        final[0].set_color(E_CLR)
        final[2].set_color(I_CLR)
        final[3].set_color(PI_CLR)
        final[6].set_color(ONE_CLR)
        final[8].set_color(ZERO_CLR)
        self.play(Write(final), run_time=2)

        # Elegant double frame
        inner = SurroundingRectangle(final, color=OK_CLR, buff=0.3, corner_radius=0.12, stroke_width=2)
        outer = SurroundingRectangle(final, color=OK_CLR, buff=0.5, corner_radius=0.18, stroke_width=1, stroke_opacity=0.4)
        self.play(Create(inner), Create(outer), run_time=0.8)
        self.pad_segment()

        self.clear_all()


class S07_BeautyScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("为什么说它是最美丽的等式？\n因为它用了五个最基本的常数和三种最基本的运算，\n一个等式，把整个数学大厦的地基连在了一起。")

        # Structured layout: constants on top row, operations middle, result bottom
        sec = Text("为什么它是最美的？", font=FONT, font_size=28, color=MUTED).to_edge(UP, buff=0.5)
        self.play(FadeIn(sec, shift=DOWN * 0.15), run_time=0.4)

        items = [("e", "分析", E_CLR), ("i", "代数", I_CLR), (r"\pi", "几何", PI_CLR),
                 ("1", "算术", ONE_CLR), ("0", "基础", ZERO_CLR)]
        const_row = VGroup()
        for sym, field, clr in items:
            s = MathTex(sym, font_size=48, color=clr)
            f = Text(field, font=FONT, font_size=14, color=MUTED)
            pill = RoundedRectangle(width=1.6, height=1.5, corner_radius=0.12,
                                    fill_color=CARD_BG, fill_opacity=0.8,
                                    stroke_color=clr, stroke_width=1.5)
            VGroup(s, f).arrange(DOWN, buff=0.15).move_to(pill)
            const_row.add(VGroup(pill, s, f))
        const_row.arrange(RIGHT, buff=0.3).next_to(sec, DOWN, buff=0.5)
        self.play(FadeIn(const_row, lag_ratio=0.15), run_time=1.5)

        # Operations row
        ops_data = [("+", "加法"), (r"\times", "乘法"), (r"\wedge", "乘方")]
        ops_row = VGroup()
        for sym, label in ops_data:
            s = MathTex(sym, font_size=36, color=ACCENT)
            l = Text(label, font=FONT, font_size=12, color=MUTED)
            VGroup(s, l).arrange(DOWN, buff=0.1)
            ops_row.add(VGroup(s, l))
        ops_row.arrange(RIGHT, buff=1.2).next_to(const_row, DOWN, buff=0.5)
        self.play(FadeIn(ops_row, shift=UP * 0.2), run_time=0.8)

        # Result
        arrow = MathTex(r"\Downarrow", font_size=36, color=ACCENT).next_to(ops_row, DOWN, buff=0.3)
        result = MathTex("e^{i\\pi} + 1 = 0", font_size=44, color=ACCENT).next_to(arrow, DOWN, buff=0.3)
        self.play(Write(arrow), run_time=0.4)
        self.play(Write(result), run_time=1)
        self.pad_segment()

        self.clear_all()


class S08_OutroScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("简洁即美。\n在数学的世界里，最深刻的真理往往藏在最简单的形式之中。")

        # Centered formula with soft glow
        eq = MathTex("e", "^{", "i", r"\pi", "}", "+", "1", "=", "0", font_size=88)
        eq[0].set_color(E_CLR)
        eq[2].set_color(I_CLR)
        eq[3].set_color(PI_CLR)
        eq[6].set_color(ONE_CLR)
        eq[8].set_color(ZERO_CLR)

        glow1 = Circle(radius=3, color=ACCENT, stroke_width=0.5, stroke_opacity=0.15, fill_opacity=0.02, fill_color=ACCENT)
        glow2 = Circle(radius=4, color=ACCENT, stroke_width=0.3, stroke_opacity=0.08, fill_opacity=0.01, fill_color=ACCENT)
        self.play(FadeIn(glow2, glow1), run_time=0.8)
        self.play(Write(eq), run_time=2.5)
        self.pad_segment()

        self.show_sub("这就是欧拉恒等式的美。")
        quote = Text("简  洁  即  美", font=FONT, font_size=24, color=MUTED)
        quote.next_to(eq, DOWN, buff=1)
        self.play(FadeIn(quote, shift=UP * 0.15), run_time=1)
        self.pad_segment()

        self.play(*[FadeOut(m, run_time=2.5) for m in self.mobjects])
        self._save_stamps()
