"""Lattice Cryptography Pop-Sci Animation (v2 -- optimized).

Key improvements over v1:
  - Step-by-step numerical examples for LWE and encryption (3B1B style)
  - 3D lattice visualization with camera rotation (ThreeDScene)
  - Progressive formula derivation with TransformMatchingTex
  - Concrete calculations: s=(3,1), mod-13 encryption walkthrough
"""

from manim import *
import numpy as np
from base import (
    SubtitleMixin, BG, ACCENT, OK_CLR, FAIL_CLR, MUTED, CARD_BG, FONT,
)

LATTICE_CLR = "#3498db"
QUANTUM_CLR = "#9b59b6"
KEY_CLR = "#e67e22"
NOISE_CLR = "#e74c3c"
SUB_BG = "#0d0d1a"


# ── Lightweight 3D projection helper (avoids ThreeDScene perf issues) ────

def _proj(x, y, z, phi=0.55, theta=-0.7):
    """Oblique projection from 3D to 2D screen coords."""
    cp, sp = np.cos(phi), np.sin(phi)
    ct, st = np.cos(theta), np.sin(theta)
    sx = x * ct - y * st
    sy = x * st * sp + y * ct * sp + z * cp
    return np.array([sx * 0.65, sy * 0.65, 0])


# ═══════════════════════════════════════════════════════════════════════════
#  S01  Hook -- quantum threat
# ═══════════════════════════════════════════════════════════════════════════

class S01_HookScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        # --- seg 1: quantum threat ---
        self.show_sub("量子计算机的出现，正在让加密体系面临前所未有的威胁")
        locks = VGroup()
        for _ in range(5):
            body = RoundedRectangle(width=0.8, height=0.6, corner_radius=0.08,
                                    fill_color=CARD_BG, fill_opacity=0.9,
                                    stroke_color=LATTICE_CLR, stroke_width=2)
            arc = Arc(radius=0.2, start_angle=0, angle=PI,
                      color=LATTICE_CLR, stroke_width=2)
            arc.next_to(body, UP, buff=-0.03)
            locks.add(VGroup(body, arc))
        locks.arrange(RIGHT, buff=0.5).shift(UP * 0.5)
        chain = VGroup(*[Line(locks[i].get_right(), locks[i+1].get_left(),
                              color=LATTICE_CLR, stroke_width=2) for i in range(4)])
        self.play(LaggedStart(*[FadeIn(l, shift=UP*0.3) for l in locks], lag_ratio=0.12))
        self.play(Create(chain, run_time=0.8))
        beam = Line(LEFT*7, RIGHT*7, color=QUANTUM_CLR, stroke_width=4).shift(UP*0.5)
        self.play(Create(beam, run_time=0.4))
        self.play(*[l[0].animate.set_stroke(color=FAIL_CLR) for l in locks],
                  *[l[1].animate.set_color(FAIL_CLR) for l in locks],
                  chain.animate.set_color(FAIL_CLR).set_opacity(0.3), run_time=0.8)
        self.pad_segment()

        # --- seg 2: RSA broken ---
        self.show_sub("RSA和椭圆曲线加密，将被量子计算机在多项式时间内攻破")
        self.play(FadeOut(VGroup(locks, chain, beam), run_time=0.4))
        rsa = MathTex("n","=","p",r"\times","q", font_size=56)
        rsa[0].set_color(ACCENT); rsa[2].set_color(LATTICE_CLR); rsa[4].set_color(LATTICE_CLR)
        rsa_l = Text("RSA", font_size=20, color=MUTED).next_to(rsa, UP, buff=0.3)
        self.play(Write(rsa), FadeIn(rsa_l, shift=DOWN*0.2))
        self.wait(0.3)
        qbox = VGroup(
            RoundedRectangle(width=1.6, height=1.2, corner_radius=0.15,
                             fill_color=QUANTUM_CLR, fill_opacity=0.25,
                             stroke_color=QUANTUM_CLR),
            Text("Q", font_size=48, color=QUANTUM_CLR, weight=BOLD))
        qbox[1].move_to(qbox[0]); qbox.shift(RIGHT*4)
        self.play(FadeIn(qbox, shift=LEFT*0.5))
        x = VGroup(Line(rsa.get_corner(UL), rsa.get_corner(DR), color=FAIL_CLR, stroke_width=3),
                   Line(rsa.get_corner(DL), rsa.get_corner(UR), color=FAIL_CLR, stroke_width=3))
        self.play(rsa.animate.set_opacity(0.2), rsa_l.animate.set_opacity(0.2),
                  Create(x, run_time=0.5))
        self.pad_segment()

        # --- seg 3: lattice teaser ---
        self.show_sub("答案就藏在一个优雅的数学结构里——格")
        self.play(FadeOut(VGroup(rsa, rsa_l, x, qbox), run_time=0.4))
        q = Text("?", font_size=120, color=ACCENT)
        self.play(FadeIn(q, scale=0.5)); self.wait(0.4)
        dots = VGroup(*[Dot([i*0.8, j*0.8, 0], radius=0.06,
                            color=LATTICE_CLR, fill_opacity=0)
                        for i in range(-4,5) for j in range(-2,3)])
        self.play(FadeOut(q), *[d.animate.set_fill(opacity=0.7) for d in dots], run_time=1.2)
        self.clear_all()


# ═══════════════════════════════════════════════════════════════════════════
#  S02  Title + roadmap
# ═══════════════════════════════════════════════════════════════════════════

class S02_TitleScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("格密码学，后量子时代的安全基石")
        bg = VGroup(*[Dot([i*0.9,j*0.8,0], radius=0.03,
                          color=LATTICE_CLR, fill_opacity=0.12)
                      for i in range(-8,9) for j in range(-5,6)])
        self.play(FadeIn(bg, run_time=0.6))
        t = Text("格密码学", font=FONT, font_size=72, color=WHITE, weight=BOLD)
        s = Text("后量子时代的安全基石", font=FONT, font_size=36, color=ACCENT)
        VGroup(t, s).arrange(DOWN, buff=0.4)
        glow = Circle(radius=2.5, fill_color=LATTICE_CLR, fill_opacity=0.07, stroke_width=0)
        self.play(FadeIn(glow)); self.play(Write(t, run_time=1.5))
        self.play(FadeIn(s, shift=UP*0.2)); self.pad_segment()

        self.show_sub("从基础概念到量子抗性，一步步揭开格密码学的面纱")
        self.play(FadeOut(VGroup(t, s, glow), run_time=0.4))
        items = [("01","什么是格",LATTICE_CLR),("02","三维空间中的格",QUANTUM_CLR),
                 ("03","困难问题",FAIL_CLR),("04","LWE构造",ACCENT),
                 ("05","加密方案",OK_CLR),("06","前沿应用",KEY_CLR)]
        rm = VGroup()
        for n,l,c in items:
            rm.add(VGroup(Text(n, font_size=28, color=c, weight=BOLD),
                          Text(l, font=FONT, font_size=24, color=WHITE)).arrange(RIGHT, buff=0.3))
        rm.arrange(DOWN, buff=0.3, aligned_edge=LEFT).shift(LEFT*0.5)
        for it in rm:
            self.play(FadeIn(it, shift=RIGHT*0.3), run_time=0.2)
        self.wait(0.3); self.clear_all()


# ═══════════════════════════════════════════════════════════════════════════
#  S03  Lattice basics -- step-by-step point generation
# ═══════════════════════════════════════════════════════════════════════════

class S03_LatticeBasicsScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG
        sec = Text("01  什么是格", font=FONT, font_size=20, color=MUTED)
        sec.to_corner(UL, buff=0.4)
        self.play(FadeIn(sec, shift=DOWN*0.15))

        # --- seg 1: define lattice with basis vectors ---
        self.show_sub("给定两个基向量，格就是所有整数线性组合的点集")

        axes = Axes(x_range=[-4,4], y_range=[-3,3], x_length=9, y_length=6.5,
                    tips=False, axis_config={"stroke_color": MUTED, "stroke_width": 0.5})
        self.play(Create(axes, run_time=0.5))
        origin = Dot(axes.c2p(0,0), radius=0.1, color=ACCENT)
        self.play(FadeIn(origin))

        b1 = Arrow(axes.c2p(0,0), axes.c2p(1,0), color=OK_CLR, buff=0, stroke_width=3)
        b2 = Arrow(axes.c2p(0,0), axes.c2p(0,1), color=KEY_CLR, buff=0, stroke_width=3)
        b1l = MathTex(r"\vec{b}_1=(1,0)", font_size=22, color=OK_CLR).next_to(b1, DOWN, buff=0.12)
        b2l = MathTex(r"\vec{b}_2=(0,1)", font_size=22, color=KEY_CLR).next_to(b2, LEFT, buff=0.12)
        self.play(GrowArrow(b1), GrowArrow(b2))
        self.play(FadeIn(b1l), FadeIn(b2l))

        formula = MathTex(r"\mathcal{L}","=",r"\{","n_1",r"\vec{b}_1","+","n_2",r"\vec{b}_2",
                          r"\mid","n_i",r"\in",r"\mathbb{Z}",r"\}", font_size=28)
        formula.to_edge(UP, buff=0.5)
        formula[0].set_color(ACCENT)
        formula[3].set_color(MUTED); formula[4].set_color(OK_CLR)
        formula[6].set_color(MUTED); formula[7].set_color(KEY_CLR)
        self.play(Write(formula, run_time=1.2))
        self.pad_segment()

        # --- seg 2: step-by-step generation (3B1B style) ---
        self.show_sub("让我们一步步生成格点：每个整数组合对应一个格点")

        self.play(FadeOut(VGroup(b1l, b2l, formula), run_time=0.3))

        calc = VGroup()  # calculation display at top
        combos = [(1,0),(0,1),(1,1),(2,1),(-1,1)]
        generated = VGroup()

        for n1, n2 in combos:
            # Build the combination label
            parts = []
            if n1 != 0:
                parts.append(f"{n1}" + r"\vec{b}_1")
            if n2 != 0:
                sign = "+" if (n2 > 0 and n1 != 0) else ""
                parts.append(sign + f"{n2}" + r"\vec{b}_2")
            expr = "".join(parts)
            label = MathTex(expr, "=", f"({n1},{n2})", font_size=24)
            label[0].set_color(WHITE)
            label[-1].set_color(ACCENT)
            label.to_edge(UP, buff=0.6)

            pt = Dot(axes.c2p(n1, n2), radius=0.1, color=ACCENT)

            # Animate: show combo, flash arrow, place dot
            if calc:
                self.play(FadeOut(calc, run_time=0.15))
            calc = label
            self.play(Write(calc, run_time=0.35), FadeIn(pt, scale=0.5, run_time=0.35))
            generated.add(pt)
            self.wait(0.2)

        self.play(FadeOut(calc, run_time=0.2))

        # Fill remaining lattice
        remaining = VGroup(*[
            Dot(axes.c2p(i,j), radius=0.05, color=LATTICE_CLR)
            for i in range(-4,5) for j in range(-3,4)
            if (i,j) not in combos and (i,j) != (0,0)
        ])
        self.play(FadeIn(remaining, run_time=0.8))
        self.pad_segment()

        # --- seg 3: good basis vs bad basis (animated transform) ---
        self.show_sub("同一个格可以有不同的基：好基整齐，坏基倾斜")

        self.play(FadeOut(VGroup(axes, origin, b1, b2, generated, remaining), run_time=0.4))

        def make_lat(cx, cy):
            return VGroup(*[Dot([cx + i*0.55 + j*0.0, cy + j*0.55, 0],
                               radius=0.04, color=LATTICE_CLR)
                           for i in range(-3,4) for j in range(-3,4)
                           if abs(cx + i*0.55) < 4.5 and abs(cy + j*0.55) < 2.8])

        # Left: good basis
        gl = Text("好基", font=FONT, font_size=24, color=OK_CLR).move_to([-3.2, 2.8, 0])
        gpts = make_lat(-3.2, 0)
        ga1 = Arrow([-3.2,0,0],[-2.65,0,0], color=OK_CLR, buff=0, stroke_width=3)
        ga2 = Arrow([-3.2,0,0],[-3.2,0.55,0], color=OK_CLR, buff=0, stroke_width=3)

        # Right: bad basis (same lattice, skewed basis)
        bl = Text("坏基", font=FONT, font_size=24, color=FAIL_CLR).move_to([3.2, 2.8, 0])
        bpts = make_lat(3.2, 0)
        ba1 = Arrow([3.2,0,0],[3.75,0.495,0], color=FAIL_CLR, buff=0, stroke_width=3)
        ba2 = Arrow([3.2,0,0],[3.73,0.55,0], color=FAIL_CLR, buff=0, stroke_width=3)

        div = DashedLine(UP*3, DOWN*3, color=MUTED, stroke_width=1)

        self.play(FadeIn(gpts), FadeIn(bpts), FadeIn(gl, shift=DOWN*0.15),
                  FadeIn(bl, shift=DOWN*0.15), Create(div), run_time=0.7)
        self.play(GrowArrow(ga1), GrowArrow(ga2), GrowArrow(ba1), GrowArrow(ba2), run_time=0.7)

        easy = VGroup(MathTex(r"\checkmark", font_size=36, color=OK_CLR),
                      Text("容易计算", font=FONT, font_size=18, color=OK_CLR)
                      ).arrange(DOWN, buff=0.1).move_to([-3.2,-2.2,0])
        hard = VGroup(MathTex(r"\times", font_size=36, color=FAIL_CLR),
                      Text("极其困难", font=FONT, font_size=18, color=FAIL_CLR)
                      ).arrange(DOWN, buff=0.1).move_to([3.2,-2.2,0])
        self.play(FadeIn(easy, scale=0.7), FadeIn(hard, scale=0.7))
        self.pad_segment()

        # --- seg 4: asymmetry = security ---
        self.show_sub("这种不对称性，正是格密码学安全性的根基")

        arr = Arrow(RIGHT*1.2, LEFT*1.2, color=ACCENT, stroke_width=3).shift(DOWN*2.7)
        qm = Text("?", font_size=32, color=ACCENT).next_to(arr, UP, buff=0.1)
        self.play(GrowArrow(arr), FadeIn(qm))

        self.clear_all()


# ═══════════════════════════════════════════════════════════════════════════
#  S04  3D lattice visualization (ThreeDScene)
# ═══════════════════════════════════════════════════════════════════════════

class S04_Lattice3DScene(SubtitleMixin, Scene):
    """Fake-3D lattice using oblique projection -- fast Cairo render."""

    def construct(self):
        self.camera.background_color = BG

        # --- seg 1: transition to 3D ---
        self.show_sub("真实的格存在于高维空间，让我们先看看三维的格")

        # Projected 3D axes
        o = _proj(0, 0, 0)
        ax_x = Arrow(o, _proj(3, 0, 0), color=OK_CLR, stroke_width=2, buff=0)
        ax_y = Arrow(o, _proj(0, 3, 0), color=KEY_CLR, stroke_width=2, buff=0)
        ax_z = Arrow(o, _proj(0, 0, 3), color=NOISE_CLR, stroke_width=2, buff=0)
        lx = MathTex("x", font_size=20, color=OK_CLR).next_to(ax_x, RIGHT, buff=0.08)
        ly = MathTex("y", font_size=20, color=KEY_CLR).next_to(ax_y, LEFT, buff=0.08)
        lz = MathTex("z", font_size=20, color=NOISE_CLR).next_to(ax_z, UP, buff=0.08)
        axes_grp = VGroup(ax_x, ax_y, ax_z, lx, ly, lz)
        self.play(Create(axes_grp, run_time=0.6))

        # Lattice points via projection
        pts = VGroup()
        for i in range(-2, 3):
            for j in range(-2, 3):
                for k in range(-1, 2):
                    p = _proj(i, j, k)
                    depth = (i**2 + j**2 + k**2) ** 0.5
                    opacity = max(0.25, 1.0 - depth / 5)
                    pts.add(Dot(p, radius=0.055, color=LATTICE_CLR, fill_opacity=opacity))

        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in pts],
                               lag_ratio=0.006, run_time=1.5))

        # Basis vectors (bold)
        bv1 = Arrow(o, _proj(1, 0, 0), color=OK_CLR, stroke_width=4, buff=0)
        bv2 = Arrow(o, _proj(0, 1, 0), color=KEY_CLR, stroke_width=4, buff=0)
        bv3 = Arrow(o, _proj(0, 0, 1), color=NOISE_CLR, stroke_width=4, buff=0)
        bl1 = MathTex(r"\vec{b}_1", font_size=22, color=OK_CLR).next_to(bv1.get_end(), DR, buff=0.06)
        bl2 = MathTex(r"\vec{b}_2", font_size=22, color=KEY_CLR).next_to(bv2.get_end(), UL, buff=0.06)
        bl3 = MathTex(r"\vec{b}_3", font_size=22, color=NOISE_CLR).next_to(bv3.get_end(), UR, buff=0.06)
        self.play(GrowArrow(bv1), GrowArrow(bv2), GrowArrow(bv3),
                  FadeIn(bl1), FadeIn(bl2), FadeIn(bl3), run_time=0.6)
        self.pad_segment()

        # --- seg 2: "rotate" by morphing to a different projection angle ---
        self.show_sub("旋转视角，感受三维格的空间结构")

        # Animate to new angle
        new_pts = VGroup()
        for i in range(-2, 3):
            for j in range(-2, 3):
                for k in range(-1, 2):
                    p = _proj(i, j, k, phi=0.45, theta=-1.2)
                    depth = (i**2 + j**2 + k**2) ** 0.5
                    opacity = max(0.25, 1.0 - depth / 5)
                    new_pts.add(Dot(p, radius=0.055, color=LATTICE_CLR, fill_opacity=opacity))

        self.play(Transform(pts, new_pts, run_time=2.5, rate_func=smooth))

        # Update axes/basis to new angle
        o2 = _proj(0, 0, 0, phi=0.45, theta=-1.2)
        new_axes = VGroup(
            Arrow(o2, _proj(3, 0, 0, phi=0.45, theta=-1.2), color=OK_CLR, stroke_width=2, buff=0),
            Arrow(o2, _proj(0, 3, 0, phi=0.45, theta=-1.2), color=KEY_CLR, stroke_width=2, buff=0),
            Arrow(o2, _proj(0, 0, 3, phi=0.45, theta=-1.2), color=NOISE_CLR, stroke_width=2, buff=0),
        )
        self.play(Transform(axes_grp, VGroup(*new_axes, lx.copy(), ly.copy(), lz.copy())),
                  FadeOut(VGroup(bv1, bv2, bv3, bl1, bl2, bl3)),
                  run_time=1.5)
        self.pad_segment()

        # --- seg 3: high-dim impossibility ---
        self.show_sub("格密码学工作在数百维，搜索空间呈指数爆炸")

        self.play(pts.animate.set_opacity(0.12), axes_grp.animate.set_opacity(0.15),
                  run_time=0.5)

        dim_texts = VGroup()
        for d, c in [("3D", OK_CLR), ("256D", ACCENT), ("1024D", FAIL_CLR)]:
            dim_texts.add(Text(d, font_size=36, color=c, weight=BOLD))
        dim_texts.arrange(RIGHT, buff=1.5).shift(UP * 0.5)
        self.play(LaggedStart(*[FadeIn(t, shift=UP*0.3) for t in dim_texts], lag_ratio=0.2))

        exp = MathTex(r"2^{\Theta(n)}", font_size=48, color=FAIL_CLR).shift(DOWN * 1)
        self.play(Write(exp))

        self.clear_all()


# ═══════════════════════════════════════════════════════════════════════════
#  S05  Hard problems -- SVP & CVP
# ═══════════════════════════════════════════════════════════════════════════

class S05_HardProblemsScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG
        sec = Text("02  格上的困难问题", font=FONT, font_size=20, color=MUTED)
        sec.to_corner(UL, buff=0.4)
        self.play(FadeIn(sec, shift=DOWN*0.15))

        # --- seg 1: SVP with expanding sphere ---
        self.show_sub("SVP：找到距离原点最近的非零格点")

        lat = VGroup(*[Dot([i*0.7, j*0.7, 0], radius=0.05,
                           color=LATTICE_CLR, fill_opacity=0.5)
                       for i in range(-5,6) for j in range(-3,4)
                       if not (i==0 and j==0)])
        orig = Dot(ORIGIN, radius=0.1, color=ACCENT)
        self.play(FadeIn(lat, run_time=0.5), FadeIn(orig))

        # Expanding search circle
        search = Circle(radius=0.1, color=ACCENT, stroke_width=2, stroke_opacity=0.6)
        self.play(Create(search))
        self.play(search.animate.scale(7), run_time=1.5, rate_func=linear)

        # Nearest found
        svp = Arrow(ORIGIN, [0.7,0,0], color=ACCENT, buff=0, stroke_width=4)
        svp_lbl = MathTex(r"\text{SVP}", font_size=22, color=ACCENT).next_to(svp, UP, buff=0.15)
        self.play(GrowArrow(svp), FadeIn(svp_lbl), FadeOut(search))
        self.pad_segment()

        # --- seg 2: CVP ---
        self.show_sub("CVP：给定目标点，找到离它最近的格点")

        self.play(FadeOut(VGroup(svp, svp_lbl), run_time=0.3))

        target = Dot([0.35, 0.4, 0], radius=0.1, color=FAIL_CLR)
        t_lbl = Text("目标", font=FONT, font_size=16, color=FAIL_CLR).next_to(target, UR, buff=0.06)
        self.play(FadeIn(target, scale=0.5), FadeIn(t_lbl))

        # Try wrong candidates
        for cx, cy in [(1, 0), (0, 1)]:
            trial = DashedLine(target.get_center(), [cx*0.7, cy*0.7, 0],
                               color=MUTED, stroke_width=1.5)
            x_mark = MathTex(r"\times", font_size=20, color=FAIL_CLR).move_to(
                [cx*0.7, cy*0.7, 0] + np.array([0.15, 0.15, 0]))
            self.play(Create(trial, run_time=0.3), FadeIn(x_mark, run_time=0.2))
            self.wait(0.15)
            self.play(FadeOut(VGroup(trial, x_mark), run_time=0.2))

        # Correct nearest
        nn = Dot(ORIGIN, radius=0.1, color=ACCENT)
        nn_line = DashedLine(target.get_center(), ORIGIN, color=ACCENT, stroke_width=2)
        check = MathTex(r"\checkmark", font_size=24, color=OK_CLR).next_to(nn, DL, buff=0.08)
        self.play(FadeIn(nn), Create(nn_line), FadeIn(check))
        self.pad_segment()

        # --- seg 3: quantum-resistant ---
        self.show_sub("这两个问题连量子计算机也无法高效求解，是格密码学的基石")

        self.play(FadeOut(VGroup(lat, orig, target, t_lbl, nn, nn_line, check), run_time=0.4))

        cards = VGroup()
        for name, desc, clr in [("SVP", "最短向量问题", ACCENT),
                                 ("CVP", "最近向量问题", FAIL_CLR)]:
            c = VGroup(
                RoundedRectangle(width=3, height=2, corner_radius=0.15,
                                 fill_color=CARD_BG, fill_opacity=0.9,
                                 stroke_color=clr, stroke_width=2),
                Text(name, font_size=36, color=clr, weight=BOLD),
                Text(desc, font=FONT, font_size=18, color=WHITE))
            c[1].move_to(c[0]).shift(UP*0.3)
            c[2].move_to(c[0]).shift(DOWN*0.3)
            cards.add(c)
        cards.arrange(RIGHT, buff=1)
        self.play(LaggedStart(*[FadeIn(c, shift=UP*0.3) for c in cards], lag_ratio=0.15))

        badge = VGroup(
            RoundedRectangle(width=4.2, height=0.65, corner_radius=0.1,
                             fill_color=OK_CLR, fill_opacity=0.2,
                             stroke_color=OK_CLR, stroke_width=2),
            Text("抗量子攻击", font=FONT, font_size=22, color=OK_CLR, weight=BOLD))
        badge[1].move_to(badge[0])
        badge.next_to(cards, DOWN, buff=0.5)
        self.play(FadeIn(badge, shift=UP*0.2))
        self.clear_all()


# ═══════════════════════════════════════════════════════════════════════════
#  S06  LWE -- step-by-step numerical example (CORE IMPROVEMENT)
# ═══════════════════════════════════════════════════════════════════════════

class S06_LWEScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG
        sec = Text("03  LWE：带错误学习问题", font=FONT, font_size=20, color=MUTED)
        sec.to_corner(UL, buff=0.4)
        self.play(FadeIn(sec, shift=DOWN*0.15))

        # --- seg 1: what is LWE ---
        self.show_sub("LWE的核心思想：给出秘密的近似线索，但无法还原秘密")

        t1 = Text("Learning With Errors", font_size=38, color=ACCENT, weight=BOLD)
        t2 = Text("带错误学习问题", font=FONT, font_size=26, color=WHITE)
        VGroup(t1, t2).arrange(DOWN, buff=0.3)
        glow = Circle(radius=2, fill_color=ACCENT, fill_opacity=0.06, stroke_width=0)
        self.play(FadeIn(glow), Write(t1, run_time=1.2))
        self.play(FadeIn(t2, shift=UP*0.2))
        self.pad_segment()

        # --- seg 2: concrete example step-by-step ---
        self.show_sub("假设秘密s=(3,1)，取随机向量，逐步计算内积")

        self.play(FadeOut(VGroup(t1, t2, glow), run_time=0.4))

        # Secret vector (fixed reference)
        s_disp = MathTex(r"\vec{s}","=","(","3",",","1",")", font_size=32)
        s_disp[0].set_color(ACCENT); s_disp[3].set_color(ACCENT); s_disp[5].set_color(ACCENT)
        s_box = SurroundingRectangle(s_disp, corner_radius=0.1, color=ACCENT,
                                     stroke_width=2, buff=0.12,
                                     fill_color=CARD_BG, fill_opacity=0.8)
        s_grp = VGroup(s_box, s_disp).to_corner(UR, buff=0.4)
        s_label = Text("秘密", font=FONT, font_size=14, color=ACCENT).next_to(s_grp, DOWN, buff=0.08)
        self.play(FadeIn(s_grp), FadeIn(s_label))

        # === Round 1: a₁ = (2, 5) ===
        r1_title = Text("第1组:", font=FONT, font_size=18, color=MUTED).move_to([-5.5, 2.2, 0])
        a1 = MathTex(r"\vec{a}_1","=","(","2",",","5",")", font_size=28)
        a1[0].set_color(LATTICE_CLR); a1[3].set_color(LATTICE_CLR); a1[5].set_color(LATTICE_CLR)
        a1.next_to(r1_title, RIGHT, buff=0.3)
        self.play(FadeIn(r1_title), Write(a1, run_time=0.4))

        # Step-by-step inner product
        step1 = MathTex(r"\vec{a}_1",r"\cdot",r"\vec{s}","=",
                        "2",r"\times","3","+","5",r"\times","1",
                        font_size=28).shift(LEFT*1 + UP*1.2)
        step1[0].set_color(LATTICE_CLR); step1[2].set_color(ACCENT)
        step1[4].set_color(LATTICE_CLR); step1[6].set_color(ACCENT)
        step1[8].set_color(LATTICE_CLR); step1[10].set_color(ACCENT)

        self.play(Write(step1[:4], run_time=0.3))  # a₁·s =
        self.play(Write(step1[4:7], run_time=0.4))  # 2×3
        self.play(Write(step1[7:], run_time=0.4))    # +5×1

        # Resolve
        step2 = MathTex("=","6","+","5","=","11", font_size=28).next_to(step1, DOWN, aligned_edge=LEFT, buff=0.2)
        self.play(Write(step2[:4], run_time=0.3))
        self.play(Write(step2[4:], run_time=0.3))

        # Highlight 11
        h11 = SurroundingRectangle(step2[5], corner_radius=0.05, color=WHITE,
                                    stroke_width=1.5, buff=0.06)
        self.play(Create(h11, run_time=0.2))
        self.pad_segment()

        # --- seg 3: add noise, show all equations ---
        self.show_sub("每一步加上随机小噪声，得到近似等式")

        # Noise for round 1
        noise1 = MathTex("+","e_1","=","+1", font_size=28, color=NOISE_CLR)
        noise1.next_to(step2, RIGHT, buff=0.3)
        result1 = MathTex(r"\Rightarrow","b_1","=","12", font_size=28)
        result1[1].set_color(MUTED); result1[3].set_color(WHITE)
        result1.next_to(noise1, RIGHT, buff=0.3)
        self.play(Write(noise1, run_time=0.4), FadeOut(h11))
        self.play(Write(result1, run_time=0.3))

        # === Rounds 2 & 3 (faster) ===
        r2 = MathTex(r"\vec{a}_2","=","(4,1)",r"\quad",r"\vec{a}_2 \cdot \vec{s}","=","13",
                     r"\quad","+e_2=-1",r"\quad",r"\Rightarrow b_2=12", font_size=22)
        r2[0].set_color(LATTICE_CLR); r2[4].set_color(LATTICE_CLR)
        r2[6].set_color(WHITE); r2[8].set_color(NOISE_CLR)
        r2.shift(LEFT*0.5 + DOWN*0.5)

        r3 = MathTex(r"\vec{a}_3","=","(1,6)",r"\quad",r"\vec{a}_3 \cdot \vec{s}","=","9",
                     r"\quad","+e_3=+2",r"\quad",r"\Rightarrow b_3=11", font_size=22)
        r3[0].set_color(LATTICE_CLR); r3[4].set_color(LATTICE_CLR)
        r3[6].set_color(WHITE); r3[8].set_color(NOISE_CLR)
        r3.next_to(r2, DOWN, aligned_edge=LEFT, buff=0.25)

        self.play(Write(r2, run_time=0.8))
        self.play(Write(r3, run_time=0.8))
        self.pad_segment()

        # --- seg 4: without noise = easy (Gaussian elimination) ---
        self.show_sub("没有噪声？两个方程就能用高斯消元轻松求解")

        self.play(FadeOut(VGroup(r1_title, a1, step1, step2, noise1, result1, r2, r3), run_time=0.4))

        exact_title = Text("无噪声", font=FONT, font_size=22, color=OK_CLR).shift(UP*2.8 + LEFT*3)

        eq1 = MathTex("2x","+","5y","=","11", font_size=30, color=OK_CLR).shift(UP*2 + LEFT*3)
        eq2 = MathTex("4x","+","y","=","13", font_size=30, color=OK_CLR).next_to(eq1, DOWN, buff=0.2)

        self.play(FadeIn(exact_title, shift=DOWN*0.1))
        self.play(Write(eq1, run_time=0.4), Write(eq2, run_time=0.4))

        # Derivation steps
        d1 = MathTex(r"y = 13 - 4x", font_size=26, color=WHITE).next_to(eq2, DOWN, buff=0.4)
        self.play(Write(d1, run_time=0.4))

        d2 = MathTex(r"2x + 5(13-4x) = 11", font_size=26, color=WHITE).next_to(d1, DOWN, buff=0.2)
        self.play(Write(d2, run_time=0.5))

        d3 = MathTex(r"-18x = -54", font_size=26, color=WHITE).next_to(d2, DOWN, buff=0.2)
        self.play(Write(d3, run_time=0.3))

        d4 = MathTex(r"x = 3, \quad y = 1", font_size=30, color=OK_CLR).next_to(d3, DOWN, buff=0.3)
        d4_box = SurroundingRectangle(d4, corner_radius=0.08, color=OK_CLR, stroke_width=2, buff=0.12)
        self.play(Write(d4, run_time=0.4), Create(d4_box))

        check = MathTex(r"\vec{s}=(3,1)\;\checkmark", font_size=28, color=OK_CLR).next_to(d4_box, DOWN, buff=0.2)
        self.play(FadeIn(check, scale=0.7))
        self.pad_segment()

        # --- seg 5: with noise = wrong answer ---
        self.show_sub("加入噪声后，同样的方法得到完全错误的答案！")

        noisy_title = Text("有噪声", font=FONT, font_size=22, color=NOISE_CLR).shift(UP*2.8 + RIGHT*3)

        neq1 = MathTex("2x","+","5y","=","12", font_size=30, color=NOISE_CLR).shift(UP*2 + RIGHT*3)
        neq2 = MathTex("4x","+","y","=","12", font_size=30, color=NOISE_CLR).next_to(neq1, DOWN, buff=0.2)

        self.play(FadeIn(noisy_title, shift=DOWN*0.1))
        self.play(Write(neq1, run_time=0.4), Write(neq2, run_time=0.4))

        nd1 = MathTex(r"y = 12 - 4x", font_size=26, color=WHITE).next_to(neq2, DOWN, buff=0.4)
        self.play(Write(nd1, run_time=0.4))

        nd2 = MathTex(r"-18x = -48", font_size=26, color=WHITE).next_to(nd1, DOWN, buff=0.2)
        self.play(Write(nd2, run_time=0.3))

        nd3 = MathTex(r"x \approx 2.67, \quad y \approx 1.33", font_size=30,
                      color=NOISE_CLR).next_to(nd2, DOWN, buff=0.3)
        nd3_box = SurroundingRectangle(nd3, corner_radius=0.08, color=NOISE_CLR, stroke_width=2, buff=0.12)
        self.play(Write(nd3, run_time=0.4), Create(nd3_box))

        wrong = MathTex(r"\neq (3,1) \quad \times", font_size=28, color=FAIL_CLR).next_to(nd3_box, DOWN, buff=0.2)
        self.play(FadeIn(wrong, scale=0.7))

        self.clear_all()


# ═══════════════════════════════════════════════════════════════════════════
#  S07  Encryption -- concrete mod-13 example (CORE IMPROVEMENT)
# ═══════════════════════════════════════════════════════════════════════════

class S07_EncryptionScene(SubtitleMixin, Scene):
    """Step-by-step LWE encryption with concrete numbers (1D, mod 13)."""

    def construct(self):
        self.camera.background_color = BG
        sec = Text("04  LWE加密方案", font=FONT, font_size=20, color=MUTED)
        sec.to_corner(UL, buff=0.4)
        self.play(FadeIn(sec, shift=DOWN*0.15))

        # --- seg 1: key generation with concrete numbers ---
        self.show_sub("Alice选择私钥s=3，在模13下生成公钥")

        # Parameters
        params_math = MathTex(r"q = 13, \quad s = 3", font_size=28)
        params_label = Text("（私钥）", font=FONT, font_size=18, color=MUTED)
        params_label.next_to(params_math, RIGHT, buff=0.15)
        params_grp = VGroup(params_math, params_label).to_edge(UP, buff=0.6)
        self.play(Write(params_math, run_time=0.5), FadeIn(params_label))

        # Public key table: (a, b = a*s + e mod q)
        header = VGroup(
            Text("a", font_size=22, color=LATTICE_CLR),
            Text("a*s", font_size=22, color=MUTED),
            Text("e", font_size=22, color=NOISE_CLR),
            Text("b = a*s+e mod 13", font_size=22, color=WHITE),
        ).arrange(RIGHT, buff=1.0).shift(UP*1.5)

        data = [(4, 3, 1, 0), (5, 3, -1, 1), (2, 3, 1, 7), (7, 3, -1, 9)]
        rows = VGroup()
        for a, s, e, b in data:
            a_s = a * s
            e_str = f"+{e}" if e > 0 else str(e)
            row = VGroup(
                MathTex(str(a), font_size=26, color=LATTICE_CLR),
                MathTex(f"{a}\\times 3 = {a_s}", font_size=22, color=MUTED),
                MathTex(e_str, font_size=26, color=NOISE_CLR),
                MathTex(f"{(a_s + e) % 13}", font_size=26, color=WHITE),
            ).arrange(RIGHT, buff=1.0)
            rows.add(row)
        rows.arrange(DOWN, buff=0.3).next_to(header, DOWN, buff=0.3)

        self.play(Write(header, run_time=0.4))
        for row in rows:
            self.play(Write(row, run_time=0.35))

        pk_label = Text("公钥：(a, b) 对", font=FONT, font_size=18,
                        color=LATTICE_CLR).next_to(rows, DOWN, buff=0.3)
        self.play(FadeIn(pk_label))
        self.pad_segment()

        # --- seg 2: Bob encrypts m=1 ---
        self.show_sub("Bob要加密消息m=1：选第1、3行求和，再加上⌊q/2⌋")

        self.play(FadeOut(VGroup(header, pk_label, params_grp), run_time=0.3))

        # Highlight selected rows (1st and 3rd)
        hl1 = SurroundingRectangle(rows[0], color=KEY_CLR, stroke_width=2, buff=0.08)
        hl3 = SurroundingRectangle(rows[2], color=KEY_CLR, stroke_width=2, buff=0.08)
        sel_label = Text("选第1,3行", font=FONT, font_size=16, color=KEY_CLR).next_to(hl1, LEFT, buff=0.2)
        self.play(Create(hl1), Create(hl3), FadeIn(sel_label))

        # Sum computation
        self.play(rows.animate.shift(UP*0.8), hl1.animate.shift(UP*0.8),
                  hl3.animate.shift(UP*0.8), sel_label.animate.shift(UP*0.8), run_time=0.3)

        comp = VGroup()
        c1 = MathTex(r"u = a_1 + a_3 = 4 + 2 = 6", font_size=26, color=KEY_CLR)
        c2 = MathTex(r"v = b_1 + b_3 = 0 + 7 = 7", font_size=26, color=KEY_CLR)
        c3 = MathTex(r"c = v + \lfloor q/2 \rfloor \cdot m = 7 + 6 \times 1 = 13 \equiv 0",
                     font_size=26, color=KEY_CLR)
        c4 = MathTex(r"\pmod{13}", font_size=22, color=MUTED)
        comp = VGroup(c1, c2, VGroup(c3, c4).arrange(RIGHT, buff=0.1))
        comp.arrange(DOWN, buff=0.2, aligned_edge=LEFT).shift(DOWN*1.2)

        self.play(Write(c1, run_time=0.5))
        self.play(Write(c2, run_time=0.5))
        self.play(Write(c3, run_time=0.6), FadeIn(c4))

        cipher_box = SurroundingRectangle(VGroup(c1, c2, c3), corner_radius=0.1,
                                          color=QUANTUM_CLR, stroke_width=2, buff=0.15)
        cl = Text("密文 (u=6, c=0)", font=FONT, font_size=16, color=QUANTUM_CLR)
        cl.next_to(cipher_box, RIGHT, buff=0.2)
        self.play(Create(cipher_box), FadeIn(cl))
        self.pad_segment()

        # --- seg 3: Alice decrypts ---
        self.show_sub("Alice解密：c - u*s mod 13，看结果更接近0还是⌊q/2⌋")

        self.play(FadeOut(VGroup(rows, hl1, hl3, sel_label, comp, c4, cipher_box, cl), run_time=0.4))

        dec_title = Text("Alice 解密", font=FONT, font_size=24, color=OK_CLR).shift(UP*2.5)
        self.play(FadeIn(dec_title, shift=DOWN*0.15))

        # Step-by-step decryption
        ds1 = MathTex(r"c - u \cdot s", "=", r"0 - 6 \times 3", "=", r"-18", font_size=30)
        ds1[0].set_color(QUANTUM_CLR)
        ds1.shift(UP*1.5)
        self.play(Write(ds1, run_time=0.6))

        ds2 = MathTex(r"-18 \bmod 13", "=", "8", font_size=30).next_to(ds1, DOWN, buff=0.3)
        ds2[2].set_color(ACCENT)
        self.play(Write(ds2, run_time=0.5))

        # Number line visualization
        nl = NumberLine(x_range=[0, 12, 1], length=10, include_numbers=True,
                        font_size=16, color=MUTED).shift(DOWN*0.5)
        self.play(Create(nl, run_time=0.5))

        # Mark 0 and ⌊q/2⌋=6
        mark0 = Dot(nl.n2p(0), radius=0.1, color=OK_CLR)
        mark6 = Dot(nl.n2p(6), radius=0.1, color=KEY_CLR)
        l0 = MathTex("0", font_size=20, color=OK_CLR).next_to(mark0, UP, buff=0.15)
        l6 = MathTex(r"\lfloor q/2 \rfloor = 6", font_size=18, color=KEY_CLR).next_to(mark6, UP, buff=0.15)
        self.play(FadeIn(mark0), FadeIn(l0), FadeIn(mark6), FadeIn(l6))

        # Mark result = 8
        mark8 = Dot(nl.n2p(8), radius=0.12, color=ACCENT)
        l8 = MathTex("8", font_size=22, color=ACCENT).next_to(mark8, DOWN, buff=0.15)
        self.play(FadeIn(mark8, scale=0.5), FadeIn(l8))

        # Distance arrows
        dist0 = DoubleArrow(nl.n2p(0) + DOWN*0.4, nl.n2p(5) + DOWN*0.4,
                            color=FAIL_CLR, stroke_width=2, buff=0)
        dist0_l = MathTex(r"\text{dist}=5", font_size=16, color=FAIL_CLR).next_to(dist0, DOWN, buff=0.08)
        dist6 = DoubleArrow(nl.n2p(6) + DOWN*0.4, nl.n2p(8) + DOWN*0.4,
                            color=OK_CLR, stroke_width=2, buff=0)
        dist6_l = MathTex(r"\text{dist}=2", font_size=16, color=OK_CLR).next_to(dist6, DOWN, buff=0.08)

        self.play(GrowArrow(dist0), FadeIn(dist0_l))
        self.play(GrowArrow(dist6), FadeIn(dist6_l))

        # Conclusion
        conclusion = MathTex(r"2 < 5 \;\Rightarrow\; m = 1 \;\checkmark",
                             font_size=32, color=OK_CLR).shift(DOWN*2.3)
        c_box = SurroundingRectangle(conclusion, corner_radius=0.1, color=OK_CLR,
                                     stroke_width=2, buff=0.15)
        self.play(Write(conclusion), Create(c_box))
        self.pad_segment()

        # --- seg 4: security–correctness balance ---
        self.show_sub("噪声让攻击者无法破解，又足够小让合法者正确解密——精妙的平衡")

        self.play(FadeOut(VGroup(
            dec_title, ds1, ds2, nl, mark0, mark6, mark8,
            l0, l6, l8, dist0, dist0_l, dist6, dist6_l, conclusion, c_box,
        ), run_time=0.4))

        beam = Line(LEFT*3, RIGHT*3, color=WHITE, stroke_width=3)
        tri = Triangle(fill_color=MUTED, fill_opacity=0.5, stroke_width=0).scale(0.2).shift(DOWN*0.2)

        lp = VGroup(
            RoundedRectangle(width=2.5, height=1.5, corner_radius=0.12,
                             fill_color=CARD_BG, fill_opacity=0.9,
                             stroke_color=OK_CLR, stroke_width=2),
            Text("安全性", font=FONT, font_size=22, color=OK_CLR),
            Text("噪声要大", font=FONT, font_size=16, color=MUTED))
        lp[1].move_to(lp[0]).shift(UP*0.2); lp[2].move_to(lp[0]).shift(DOWN*0.3)
        lp.shift(LEFT*3 + DOWN*1.2)

        rp = VGroup(
            RoundedRectangle(width=2.5, height=1.5, corner_radius=0.12,
                             fill_color=CARD_BG, fill_opacity=0.9,
                             stroke_color=ACCENT, stroke_width=2),
            Text("正确性", font=FONT, font_size=22, color=ACCENT),
            Text("噪声要小", font=FONT, font_size=16, color=MUTED))
        rp[1].move_to(rp[0]).shift(UP*0.2); rp[2].move_to(rp[0]).shift(DOWN*0.3)
        rp.shift(RIGHT*3 + DOWN*1.2)

        ll = Line(beam.get_left(), lp.get_top(), color=MUTED, stroke_width=1.5)
        rl = Line(beam.get_right(), rp.get_top(), color=MUTED, stroke_width=1.5)
        bl = Text("精妙的平衡", font=FONT, font_size=26, color=WHITE).shift(UP*1.5)

        self.play(Create(beam), FadeIn(tri),
                  FadeIn(lp, shift=UP*0.3), FadeIn(rp, shift=UP*0.3),
                  Create(ll), Create(rl), run_time=0.8)
        self.play(FadeIn(bl, shift=DOWN*0.2))
        self.clear_all()


# ═══════════════════════════════════════════════════════════════════════════
#  S08  Applications
# ═══════════════════════════════════════════════════════════════════════════

class S08_ApplicationsScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG
        sec = Text("05  前沿应用", font=FONT, font_size=20, color=MUTED)
        sec.to_corner(UL, buff=0.4)
        self.play(FadeIn(sec, shift=DOWN*0.15))

        # --- seg 1 ---
        self.show_sub("格密码学正在改变整个密码学的格局")
        landscape = Text("从理论到实践", font=FONT, font_size=40, color=ACCENT)
        self.play(Write(landscape, run_time=1.0)); self.pad_segment()

        # --- seg 2: NIST ---
        self.show_sub("NIST选定Kyber和Dilithium作为首批后量子密码标准")
        self.play(FadeOut(landscape, run_time=0.4))
        nist = VGroup(
            RoundedRectangle(width=6, height=0.8, corner_radius=0.1,
                             fill_color=LATTICE_CLR, fill_opacity=0.2,
                             stroke_color=LATTICE_CLR, stroke_width=2),
            Text("NIST 后量子密码标准 (2022)", font=FONT, font_size=22, color=LATTICE_CLR))
        nist[1].move_to(nist[0]); nist.shift(UP*2.5)
        cards = VGroup()
        for n, d, c in [("CRYSTALS-Kyber","密钥封装",OK_CLR),("CRYSTALS-Dilithium","数字签名",KEY_CLR)]:
            card = VGroup(
                RoundedRectangle(width=4.5, height=1.8, corner_radius=0.15,
                                 fill_color=CARD_BG, fill_opacity=0.9, stroke_color=c, stroke_width=2),
                Text(n, font_size=22, color=c, weight=BOLD),
                Text(d, font=FONT, font_size=16, color=WHITE),
                Text("基于格密码学", font=FONT, font_size=14, color=MUTED))
            card[1].move_to(card[0]).shift(UP*0.35)
            card[2].move_to(card[0]).shift(DOWN*0.1)
            card[3].move_to(card[0]).shift(DOWN*0.5)
            cards.add(card)
        cards.arrange(RIGHT, buff=0.6).shift(UP*0.5)
        self.play(FadeIn(nist, shift=DOWN*0.2))
        self.play(LaggedStart(*[FadeIn(c, shift=UP*0.3) for c in cards], lag_ratio=0.15))
        self.pad_segment()

        # --- seg 3: FHE ---
        self.show_sub("全同态加密：在不解密的情况下对密文进行任意计算")
        self.play(FadeOut(VGroup(nist, cards), run_time=0.4))
        fhe_t = Text("全同态加密 (FHE)", font=FONT, font_size=28, color=ACCENT).shift(UP*2.5)
        enc = VGroup(RoundedRectangle(width=2, height=1, corner_radius=0.1,
                                      fill_color=CARD_BG, fill_opacity=0.9,
                                      stroke_color=QUANTUM_CLR, stroke_width=2),
                     Text("密文", font=FONT, font_size=18, color=QUANTUM_CLR))
        enc[1].move_to(enc[0]); enc.shift(LEFT*4)
        comp = VGroup(RoundedRectangle(width=2.5, height=1.5, corner_radius=0.1,
                                       fill_color=CARD_BG, fill_opacity=0.9,
                                       stroke_color=OK_CLR, stroke_width=2),
                      MathTex("+",r"\times", font_size=36, color=OK_CLR),
                      Text("密文上计算", font=FONT, font_size=14, color=MUTED))
        comp[1].move_to(comp[0]).shift(UP*0.15); comp[2].move_to(comp[0]).shift(DOWN*0.4)
        res = VGroup(RoundedRectangle(width=2, height=1, corner_radius=0.1,
                                      fill_color=CARD_BG, fill_opacity=0.9,
                                      stroke_color=ACCENT, stroke_width=2),
                     Text("密文结果", font=FONT, font_size=18, color=ACCENT))
        res[1].move_to(res[0]); res.shift(RIGHT*4)
        a1 = Arrow(enc.get_right(), comp.get_left(), color=MUTED, stroke_width=2)
        a2 = Arrow(comp.get_right(), res.get_left(), color=MUTED, stroke_width=2)
        priv = Text("服务器全程不知道数据内容！", font=FONT, font_size=20, color=OK_CLR).shift(DOWN*1.8)
        pf = SurroundingRectangle(priv, corner_radius=0.1, color=OK_CLR, stroke_width=1.5, buff=0.15)
        self.play(FadeIn(fhe_t, shift=DOWN*0.15))
        self.play(FadeIn(enc, shift=RIGHT*0.3))
        self.play(GrowArrow(a1), FadeIn(comp, shift=RIGHT*0.2))
        self.play(GrowArrow(a2), FadeIn(res, shift=RIGHT*0.2))
        self.play(FadeIn(priv), Create(pf)); self.pad_segment()

        # --- seg 4: ZKP ---
        self.show_sub("格还为区块链和数字身份提供后量子安全的零知识证明")
        self.play(FadeOut(VGroup(fhe_t, enc, comp, res, a1, a2, priv, pf), run_time=0.4))
        zkp = VGroup(RoundedRectangle(width=4, height=2, corner_radius=0.15,
                                       fill_color=CARD_BG, fill_opacity=0.9,
                                       stroke_color=QUANTUM_CLR, stroke_width=2),
                     Text("零知识证明", font=FONT, font_size=24, color=QUANTUM_CLR),
                     Text("证明知道秘密，不泄露信息", font=FONT, font_size=14, color=MUTED))
        zkp[1].move_to(zkp[0]).shift(UP*0.3); zkp[2].move_to(zkp[0]).shift(DOWN*0.3)
        zkp.shift(LEFT*3)
        bc = VGroup(RoundedRectangle(width=4, height=2, corner_radius=0.15,
                                      fill_color=CARD_BG, fill_opacity=0.9,
                                      stroke_color=KEY_CLR, stroke_width=2),
                    Text("区块链安全", font=FONT, font_size=24, color=KEY_CLR),
                    Text("后量子数字身份保障", font=FONT, font_size=14, color=MUTED))
        bc[1].move_to(bc[0]).shift(UP*0.3); bc[2].move_to(bc[0]).shift(DOWN*0.3)
        bc.shift(RIGHT*3)
        plus = Text("+", font_size=36, color=WHITE)
        lb = VGroup(RoundedRectangle(width=5, height=0.7, corner_radius=0.1,
                                      fill_color=LATTICE_CLR, fill_opacity=0.2,
                                      stroke_color=LATTICE_CLR, stroke_width=2),
                    Text("均基于格密码学", font=FONT, font_size=20, color=LATTICE_CLR))
        lb[1].move_to(lb[0]); lb.shift(DOWN*2)
        self.play(FadeIn(zkp, shift=UP*0.3), FadeIn(plus), FadeIn(bc, shift=UP*0.3), run_time=0.7)
        self.play(FadeIn(lb, shift=UP*0.2))
        self.clear_all()


# ═══════════════════════════════════════════════════════════════════════════
#  S09  Outro
# ═══════════════════════════════════════════════════════════════════════════

class S09_OutroScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("格密码学：从优雅的数学到守护人类数字安全的最前沿武器")

        dots = VGroup(*[
            Dot([i*0.6, j*0.6, 0], radius=0.04, color=LATTICE_CLR,
                fill_opacity=max(0.1, 1.0 - (i**2 + j**2)**0.5 / 8))
            for i in range(-6,7) for j in range(-4,5)])
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots],
                               lag_ratio=0.004, run_time=1.8))

        shield = Polygon([0,2,0],[-1.5,0.8,0],[-1.2,-1.2,0],
                         [0,-2,0],[1.2,-1.2,0],[1.5,0.8,0],
                         fill_color=LATTICE_CLR, fill_opacity=0.15,
                         stroke_color=ACCENT, stroke_width=3)
        shield_txt = Text("格", font=FONT, font_size=48, color=ACCENT, weight=BOLD)
        self.play(dots.animate.set_opacity(0.12), FadeIn(shield, scale=0.7),
                  Write(shield_txt, run_time=0.8), run_time=1.2)

        final = Text("数学之美，守护未来", font=FONT, font_size=32, color=WHITE).shift(DOWN*2.8)
        self.play(FadeIn(final, shift=UP*0.2))
        self.wait(1.0)

        self.pad_segment()
        self._save_stamps()
