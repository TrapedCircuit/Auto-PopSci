"""Transformer -- 5-minute pop-sci Manim animation."""

from manim import *
import numpy as np
from base import (
    SubtitleMixin, BG, ACCENT, OK_CLR, FAIL_CLR, MUTED, CARD_BG, FONT,
)

Q_CLR = "#3498db"
K_CLR = "#e67e22"
V_CLR = "#2ecc71"
ATT_CLR = "#e74c3c"
ENC_CLR = "#3498db"
DEC_CLR = "#e67e22"
EMBED_CLR = "#9b59b6"
POS_CLR = "#1abc9c"


class S01_HookScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("你有没有想过，ChatGPT是怎么理解你的问题，\n并给出流畅回答的？\n这一切的秘密，来自2017年的一篇论文。")

        user_bubble = RoundedRectangle(
            width=5.5, height=0.9, corner_radius=0.2,
            fill_color="#2c3e50", fill_opacity=0.9,
            stroke_color=Q_CLR, stroke_width=1.5,
        ).shift(UP * 1.5 + LEFT * 0.8)
        user_text = Text("什么是量子计算？", font=FONT, font_size=22, color=WHITE)
        user_text.move_to(user_bubble)
        user_icon = Circle(
            radius=0.22, color=Q_CLR, fill_opacity=0.8, stroke_width=0,
        ).next_to(user_bubble, LEFT, buff=0.3)
        user_lbl = Text("U", font_size=16, color=WHITE).move_to(user_icon)
        self.play(
            FadeIn(user_icon, user_lbl),
            FadeIn(user_bubble), Write(user_text), run_time=1.0,
        )

        ai_bubble = RoundedRectangle(
            width=6.5, height=1.2, corner_radius=0.2,
            fill_color="#1a3a2e", fill_opacity=0.9,
            stroke_color=V_CLR, stroke_width=1.5,
        ).shift(DOWN * 0.3 + RIGHT * 0.3)
        ai_text = Text(
            "量子计算利用量子力学原理，\n通过叠加和纠缠来处理信息……",
            font=FONT, font_size=18, color=WHITE,
        )
        ai_text.move_to(ai_bubble)
        ai_icon = Circle(
            radius=0.22, color=V_CLR, fill_opacity=0.8, stroke_width=0,
        ).next_to(ai_bubble, LEFT, buff=0.3)
        ai_lbl = Text("AI", font_size=12, color=WHITE).move_to(ai_icon)
        self.play(
            FadeIn(ai_icon, ai_lbl),
            FadeIn(ai_bubble), Write(ai_text), run_time=1.5,
        )
        self.pad_segment()

        self.show_sub("这篇论文的标题只有五个英文单词：\nAttention Is All You Need。\n它提出了一个全新的模型架构。")
        self.play(
            FadeOut(user_bubble, user_text, user_icon, user_lbl,
                    ai_bubble, ai_text, ai_icon, ai_lbl),
            run_time=0.5,
        )

        paper_title = Text("Attention Is All You Need", font_size=36, color=ACCENT)
        paper_sub = Text("Vaswani et al., 2017", font_size=18, color=MUTED)
        paper_grp = VGroup(paper_title, paper_sub).arrange(DOWN, buff=0.3)
        paper_frame = SurroundingRectangle(
            paper_grp, color=ACCENT, buff=0.5,
            corner_radius=0.15, stroke_width=1.5,
        )
        self.play(Write(paper_title), run_time=1.5)
        self.play(FadeIn(paper_sub), Create(paper_frame), run_time=0.8)
        self.pad_segment()

        self.show_sub("这个架构的名字叫做Transformer。\n今天，我们就来揭开它的神秘面纱。")
        self.play(FadeOut(paper_grp, paper_frame), run_time=0.5)

        title = Text("TRANSFORMER", font_size=68, color=ACCENT)
        glow = Circle(
            radius=3, color=ACCENT, stroke_width=1, stroke_opacity=0.2,
            fill_opacity=0.03, fill_color=ACCENT,
        )
        self.play(FadeIn(glow), run_time=0.5)
        self.play(Write(title), run_time=2.0)
        self.pad_segment()

        self.clear_all()


class S02_OverviewScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("Transformer最初为机器翻译设计。\n核心结构分为编码器和解码器。\n编码器理解输入，解码器生成输出。")

        sec = Text("架构总览", font=FONT, font_size=24, color=MUTED)
        sec.to_edge(UP, buff=0.4)
        self.play(FadeIn(sec, shift=DOWN * 0.15), run_time=0.4)

        enc_box = RoundedRectangle(
            width=3.5, height=4, corner_radius=0.2,
            fill_color="#0d2137", fill_opacity=0.9,
            stroke_color=ENC_CLR, stroke_width=2,
        ).shift(LEFT * 2.5 + DOWN * 0.3)
        enc_label = Text("编码器", font=FONT, font_size=22, color=ENC_CLR)
        enc_label.next_to(enc_box, UP, buff=0.15)
        enc_en = Text("Encoder", font_size=14, color=MUTED)
        enc_en.next_to(enc_label, DOWN, buff=0.05)

        dec_box = RoundedRectangle(
            width=3.5, height=4, corner_radius=0.2,
            fill_color="#2d1a0d", fill_opacity=0.9,
            stroke_color=DEC_CLR, stroke_width=2,
        ).shift(RIGHT * 2.5 + DOWN * 0.3)
        dec_label = Text("解码器", font=FONT, font_size=22, color=DEC_CLR)
        dec_label.next_to(dec_box, UP, buff=0.15)
        dec_en = Text("Decoder", font_size=14, color=MUTED)
        dec_en.next_to(dec_label, DOWN, buff=0.05)

        arrow = Arrow(
            enc_box.get_right(), dec_box.get_left(),
            color=ACCENT, buff=0.15, stroke_width=2,
        )

        def _sublayer(text, color, pos):
            r = RoundedRectangle(
                width=2.8, height=0.7, corner_radius=0.1,
                fill_color=CARD_BG, fill_opacity=0.8,
                stroke_color=color, stroke_width=1,
            ).move_to(pos)
            t = Text(text, font=FONT, font_size=14, color=color).move_to(r)
            return VGroup(r, t)

        enc_sa = _sublayer("自注意力", ENC_CLR, enc_box.get_center() + UP * 0.8)
        enc_ff = _sublayer("前馈网络", ENC_CLR, enc_box.get_center() + DOWN * 0.5)
        dec_sa = _sublayer("自注意力", DEC_CLR, dec_box.get_center() + UP * 1.0)
        dec_ca = _sublayer("交叉注意力", DEC_CLR, dec_box.get_center())
        dec_ff = _sublayer("前馈网络", DEC_CLR, dec_box.get_center() + DOWN * 1.0)

        inp_arrow = Arrow(
            enc_box.get_bottom() + DOWN * 0.8, enc_box.get_bottom(),
            color=MUTED, buff=0.1, stroke_width=1.5,
        )
        inp_label = Text("输入", font=FONT, font_size=14, color=MUTED)
        inp_label.next_to(inp_arrow, DOWN, buff=0.05)
        out_arrow = Arrow(
            dec_box.get_top(), dec_box.get_top() + UP * 0.8,
            color=MUTED, buff=0.1, stroke_width=1.5,
        )
        out_label = Text("输出", font=FONT, font_size=14, color=MUTED)
        out_label.next_to(out_arrow, UP, buff=0.05)

        self.play(
            FadeIn(enc_box), Write(enc_label), FadeIn(enc_en),
            FadeIn(dec_box), Write(dec_label), FadeIn(dec_en),
            run_time=1.2,
        )
        self.play(
            Create(arrow),
            FadeIn(enc_sa), FadeIn(enc_ff),
            FadeIn(dec_sa), FadeIn(dec_ca), FadeIn(dec_ff),
            FadeIn(inp_arrow, inp_label),
            FadeIn(out_arrow, out_label),
            run_time=1.5,
        )
        self.pad_segment()

        self.show_sub("但它最革命性的创新，不在结构本身，\n而是一种叫做自注意力的机制。\n让我们一步步来理解它。")

        hl1 = SurroundingRectangle(
            enc_sa, color=ACCENT, buff=0.08,
            corner_radius=0.08, stroke_width=2.5,
        )
        hl2 = SurroundingRectangle(
            dec_sa, color=ACCENT, buff=0.08,
            corner_radius=0.08, stroke_width=2.5,
        )
        self.play(Create(hl1), Create(hl2), run_time=1)
        sa_label = Text("Self-Attention", font_size=20, color=ACCENT)
        sa_label.to_edge(DOWN, buff=1.5)
        self.play(Write(sa_label), run_time=0.8)
        self.pad_segment()

        self.clear_all()


class S03_EmbeddingScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("文字不能直接输入模型。\n每个词被映射成一个高维向量，这叫词嵌入。\n语义相近的词，在向量空间中距离更近。")

        sec = Text("输入表示", font=FONT, font_size=24, color=MUTED)
        sec.to_edge(UP, buff=0.4)
        self.play(FadeIn(sec, shift=DOWN * 0.15), run_time=0.3)

        words = ["我", "喜欢", "深度", "学习"]
        word_texts = VGroup(*[
            Text(w, font=FONT, font_size=28, color=WHITE) for w in words
        ]).arrange(RIGHT, buff=0.8).shift(UP * 1.5)
        self.play(FadeIn(word_texts, lag_ratio=0.2), run_time=1)

        arrows = VGroup(*[
            Arrow(
                wt.get_bottom(), wt.get_bottom() + DOWN * 1,
                color=EMBED_CLR, buff=0.1, stroke_width=1.5,
            )
            for wt in word_texts
        ])
        self.play(Create(arrows, lag_ratio=0.2), run_time=0.8)

        vecs = VGroup()
        for i, wt in enumerate(word_texts):
            bars = VGroup()
            np.random.seed(i + 42)
            for j in range(6):
                val = np.random.uniform(0.2, 1.0)
                bar = Rectangle(
                    width=0.25, height=val * 0.8,
                    fill_color=EMBED_CLR, fill_opacity=val * 0.8,
                    stroke_width=0.5, stroke_color=EMBED_CLR,
                )
                bars.add(bar)
            bars.arrange(RIGHT, buff=0.02, aligned_edge=DOWN)
            bars.next_to(arrows[i], DOWN, buff=0.15)
            vecs.add(bars)

        vec_labels = VGroup(*[
            MathTex(f"\\vec{{x}}_{{{i+1}}}", font_size=20, color=EMBED_CLR)
            .next_to(v, DOWN, buff=0.15)
            for i, v in enumerate(vecs)
        ])
        self.play(
            FadeIn(vecs, lag_ratio=0.15),
            FadeIn(vec_labels, lag_ratio=0.15),
            run_time=1.2,
        )
        self.pad_segment()

        self.show_sub("但仅有词嵌入不够。词的顺序至关重要。\n所以Transformer加入了位置编码，\n把位置信息编码进向量中。")

        pos_label = Text("+ 位置编码", font=FONT, font_size=18, color=POS_CLR)
        pos_label.next_to(vecs, DOWN, buff=0.7)

        pos_waves = VGroup()
        for i, v in enumerate(vecs):
            wave = VGroup()
            for j in range(6):
                val = 0.3 + 0.5 * abs(np.sin(i * 0.5 + j * 1.2))
                bar = Rectangle(
                    width=0.25, height=val * 0.5,
                    fill_color=POS_CLR, fill_opacity=0.7,
                    stroke_width=0.5, stroke_color=POS_CLR,
                )
                wave.add(bar)
            wave.arrange(RIGHT, buff=0.02, aligned_edge=DOWN)
            wave.move_to(v.get_center() + DOWN * 1.8)
            pos_waves.add(wave)

        self.play(Write(pos_label), FadeIn(pos_waves, lag_ratio=0.15), run_time=1.2)

        eq_sign = MathTex("=", font_size=28, color=ACCENT)
        eq_sign.next_to(pos_waves, DOWN, buff=0.4)
        final_label = Text("最终输入向量", font=FONT, font_size=16, color=ACCENT)
        final_label.next_to(eq_sign, DOWN, buff=0.2)
        self.play(Write(eq_sign), FadeIn(final_label), run_time=0.8)
        self.pad_segment()

        self.clear_all()


class S04_SelfAttentionScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("自注意力的核心思想是：\n一个词的含义取决于周围的词。\n比如「苹果」在不同语境中含义完全不同。")

        sec = Text("自注意力机制", font=FONT, font_size=24, color=MUTED)
        sec.to_edge(UP, buff=0.4)
        self.play(FadeIn(sec, shift=DOWN * 0.15), run_time=0.3)

        grp1 = VGroup(
            Text("我 吃了 一个 ", font=FONT, font_size=24, color=MUTED),
            Text("苹果", font=FONT, font_size=24, color=V_CLR),
        ).arrange(RIGHT, buff=0.05).shift(UP * 0.8)
        label1 = Text("  水果", font=FONT, font_size=18, color=V_CLR)
        label1.next_to(grp1, RIGHT, buff=0.3)

        grp2 = VGroup(
            Text("苹果", font=FONT, font_size=24, color=ATT_CLR),
            Text(" 发布了 新 手机", font=FONT, font_size=24, color=MUTED),
        ).arrange(RIGHT, buff=0.05).shift(DOWN * 0.5)
        label2 = Text("  公司", font=FONT, font_size=18, color=ATT_CLR)
        label2.next_to(grp2, RIGHT, buff=0.3)

        self.play(Write(grp1), run_time=1)
        self.play(Write(grp2), run_time=1)

        box1 = SurroundingRectangle(
            grp1[1], color=V_CLR, buff=0.08,
            corner_radius=0.05, stroke_width=2,
        )
        box2 = SurroundingRectangle(
            grp2[0], color=ATT_CLR, buff=0.08,
            corner_radius=0.05, stroke_width=2,
        )
        self.play(Create(box1), Create(box2), run_time=0.6)
        self.play(FadeIn(label1), FadeIn(label2), run_time=0.5)
        self.pad_segment()

        self.show_sub("每个词的向量经过三次线性变换，\n得到查询Q、键K和值V三个向量。\nQ代表在问什么，K代表能提供什么，V是实际内容。")
        self.play(
            FadeOut(grp1, grp2, box1, box2, label1, label2),
            run_time=0.5,
        )

        inp_vec = RoundedRectangle(
            width=1.2, height=2, corner_radius=0.1,
            fill_color=CARD_BG, fill_opacity=0.9,
            stroke_color=MUTED, stroke_width=1.5,
        ).shift(LEFT * 4)
        inp_label = MathTex("\\vec{x}", font_size=28, color=WHITE).move_to(inp_vec)

        q_box = RoundedRectangle(
            width=1.2, height=1.4, corner_radius=0.1,
            fill_color="#0d2137", fill_opacity=0.9,
            stroke_color=Q_CLR, stroke_width=2,
        ).shift(UP * 2)
        q_label = MathTex("Q", font_size=32, color=Q_CLR).move_to(q_box)
        q_desc = Text("查询", font=FONT, font_size=12, color=Q_CLR)
        q_desc.next_to(q_box, DOWN, buff=0.1)

        k_box = RoundedRectangle(
            width=1.2, height=1.4, corner_radius=0.1,
            fill_color="#2d1a0d", fill_opacity=0.9,
            stroke_color=K_CLR, stroke_width=2,
        )
        k_label = MathTex("K", font_size=32, color=K_CLR).move_to(k_box)
        k_desc = Text("键", font=FONT, font_size=12, color=K_CLR)
        k_desc.next_to(k_box, DOWN, buff=0.1)

        v_box = RoundedRectangle(
            width=1.2, height=1.4, corner_radius=0.1,
            fill_color="#0d2d1a", fill_opacity=0.9,
            stroke_color=V_CLR, stroke_width=2,
        ).shift(DOWN * 2)
        v_label = MathTex("V", font_size=32, color=V_CLR).move_to(v_box)
        v_desc = Text("值", font=FONT, font_size=12, color=V_CLR)
        v_desc.next_to(v_box, DOWN, buff=0.1)

        arr_q = Arrow(
            inp_vec.get_right(), q_box.get_left(),
            color=Q_CLR, buff=0.15, stroke_width=1.5,
        )
        arr_k = Arrow(
            inp_vec.get_right(), k_box.get_left(),
            color=K_CLR, buff=0.15, stroke_width=1.5,
        )
        arr_v = Arrow(
            inp_vec.get_right(), v_box.get_left(),
            color=V_CLR, buff=0.15, stroke_width=1.5,
        )

        wq = MathTex("W_Q", font_size=18, color=Q_CLR).next_to(arr_q, UP, buff=0.05)
        wk = MathTex("W_K", font_size=18, color=K_CLR).next_to(arr_k, UP, buff=0.05)
        wv = MathTex("W_V", font_size=18, color=V_CLR).next_to(arr_v, DOWN, buff=0.05)

        self.play(FadeIn(inp_vec, inp_label), run_time=0.5)
        self.play(Create(arr_q), FadeIn(q_box, q_label, q_desc), Write(wq), run_time=0.6)
        self.play(Create(arr_k), FadeIn(k_box, k_label, k_desc), Write(wk), run_time=0.6)
        self.play(Create(arr_v), FadeIn(v_box, v_label, v_desc), Write(wv), run_time=0.6)

        formula = MathTex(
            r"\mathrm{Attention}(Q,K,V)", "=",
            r"\mathrm{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}}\right)", "V",
            font_size=26,
        ).shift(RIGHT * 3.5)
        formula[0].set_color(ACCENT)
        formula[2].set_color(ATT_CLR)
        formula[3].set_color(V_CLR)
        self.play(Write(formula), run_time=2)
        self.pad_segment()

        self.show_sub("Q和K做点积，除以缩放因子，\n经过softmax得到权重。\n用权重对V加权求和，融合上下文信息。")
        self.play(
            FadeOut(inp_vec, inp_label, arr_q, arr_k, arr_v,
                    wq, wk, wv, q_box, q_label, q_desc,
                    k_box, k_label, k_desc, v_box, v_label, v_desc),
            run_time=0.5,
        )
        self.play(formula.animate.to_edge(UP, buff=0.8), run_time=0.5)

        words_list = ["我", "喜欢", "深度", "学习"]
        n = len(words_list)
        grid = VGroup()
        for r in range(n):
            for c in range(n):
                np.random.seed(r * 10 + c + 7)
                val = np.random.uniform(0.1, 0.6)
                if r == c:
                    val = 0.8 + np.random.uniform(0, 0.2)
                cell = Square(
                    side_length=0.7,
                    fill_color=ATT_CLR, fill_opacity=val * 0.8,
                    stroke_color=MUTED, stroke_width=0.5,
                )
                cell.move_to(
                    RIGHT * (c - 1.5) * 0.75 + DOWN * (r - 1.5) * 0.75,
                )
                grid.add(cell)

        row_labels = VGroup(*[
            Text(w, font=FONT, font_size=16, color=WHITE)
            .move_to(LEFT * 3.2 + DOWN * (i - 1.5) * 0.75)
            for i, w in enumerate(words_list)
        ])
        col_labels = VGroup(*[
            Text(w, font=FONT, font_size=16, color=WHITE)
            .move_to(RIGHT * (i - 1.5) * 0.75 + UP * 1.8)
            for i, w in enumerate(words_list)
        ])

        att_title = Text("注意力权重", font=FONT, font_size=16, color=ATT_CLR)
        att_title.next_to(grid, DOWN, buff=0.4)
        self.play(
            FadeIn(grid, lag_ratio=0.03),
            FadeIn(row_labels), FadeIn(col_labels),
            run_time=1.5,
        )
        self.play(Write(att_title), run_time=0.5)

        out_arrow = Arrow(
            grid.get_right() + RIGHT * 0.3,
            grid.get_right() + RIGHT * 1.5,
            color=ACCENT, stroke_width=2,
        )
        out_lbl = Text("上下文向量", font=FONT, font_size=16, color=ACCENT)
        out_lbl.next_to(out_arrow, RIGHT, buff=0.15)
        self.play(Create(out_arrow), Write(out_lbl), run_time=0.8)
        self.pad_segment()

        self.clear_all()


class S05_MultiHeadScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("只用一组注意力可能不够全面。\n词与词之间有语法、语义、指代等\n多维度的关系。")

        sec = Text("多头注意力", font=FONT, font_size=24, color=MUTED)
        sec.to_edge(UP, buff=0.4)
        self.play(FadeIn(sec, shift=DOWN * 0.15), run_time=0.3)

        single_box = RoundedRectangle(
            width=3, height=2, corner_radius=0.15,
            fill_color=CARD_BG, fill_opacity=0.9,
            stroke_color=ATT_CLR, stroke_width=2,
        )
        single_label = Text("单头注意力", font=FONT, font_size=18, color=ATT_CLR)
        single_label.move_to(single_box.get_top() + DOWN * 0.35)
        single_desc = Text("只能关注一种关系", font=FONT, font_size=14, color=MUTED)
        single_desc.move_to(single_box.get_center() + DOWN * 0.3)
        self.play(FadeIn(single_box, single_label, single_desc), run_time=0.8)

        cross = MathTex(r"\times", font_size=48, color=FAIL_CLR)
        cross.next_to(single_box, RIGHT, buff=0.5)
        self.play(FadeIn(cross, scale=0.5), run_time=0.4)
        self.pad_segment()

        self.show_sub("所以Transformer用多头注意力：\n同时运行多组独立的注意力计算，\n每组关注不同关系模式，最后拼接融合。")
        self.play(FadeOut(single_box, single_label, single_desc, cross), run_time=0.5)

        head_colors = [
            "#3498db", "#e74c3c", "#2ecc71", "#f1c40f",
            "#9b59b6", "#e67e22", "#1abc9c", "#e91e63",
        ]
        head_types = ["语法", "语义", "指代", "位置", "主题", "时态", "搭配", "逻辑"]

        heads = VGroup()
        for i in range(8):
            box = RoundedRectangle(
                width=1.3, height=1.6, corner_radius=0.1,
                fill_color=CARD_BG, fill_opacity=0.85,
                stroke_color=head_colors[i], stroke_width=1.5,
            )
            h_label = Text(f"H{i+1}", font_size=16, color=head_colors[i])
            h_type = Text(head_types[i], font=FONT, font_size=10, color=MUTED)
            VGroup(h_label, h_type).arrange(DOWN, buff=0.15).move_to(box)
            heads.add(VGroup(box, h_label, h_type))

        heads.arrange(RIGHT, buff=0.12).shift(UP * 0.3)

        for h in heads:
            self.play(FadeIn(h, shift=UP * 0.3, scale=0.7), run_time=0.18)

        concat_arrow = Arrow(
            heads.get_bottom() + DOWN * 0.3,
            heads.get_bottom() + DOWN * 1.2,
            color=ACCENT, stroke_width=2,
        )
        concat_label = Text("拼接 + 线性变换", font=FONT, font_size=16, color=ACCENT)
        concat_label.next_to(concat_arrow, DOWN, buff=0.15)
        result_box = RoundedRectangle(
            width=6, height=0.7, corner_radius=0.1,
            fill_color=CARD_BG, fill_opacity=0.9,
            stroke_color=ACCENT, stroke_width=2,
        ).next_to(concat_label, DOWN, buff=0.2)
        result_label = Text("多头注意力输出", font=FONT, font_size=16, color=ACCENT)
        result_label.move_to(result_box)

        self.play(Create(concat_arrow), Write(concat_label), run_time=0.8)
        self.play(FadeIn(result_box, result_label), run_time=0.6)
        self.pad_segment()

        self.clear_all()


class S06_TransformerBlockScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("注意力之后，输出要经过前馈神经网络\n做进一步处理。\n每步都有残差连接和层归一化来稳定训练。")

        sec = Text("Transformer 块", font=FONT, font_size=24, color=MUTED)
        sec.to_edge(UP, buff=0.4)
        self.play(FadeIn(sec, shift=DOWN * 0.15), run_time=0.3)

        def make_layer_box(text, color, w=4.5, h=0.7):
            box = RoundedRectangle(
                width=w, height=h, corner_radius=0.12,
                fill_color=CARD_BG, fill_opacity=0.9,
                stroke_color=color, stroke_width=1.5,
            )
            lbl = Text(text, font=FONT, font_size=16, color=color).move_to(box)
            return VGroup(box, lbl)

        attention = make_layer_box("多头自注意力", ACCENT)
        add_norm1 = make_layer_box("Add & Norm (+ 残差)", OK_CLR, h=0.5)
        ffn = make_layer_box("前馈神经网络", Q_CLR)
        add_norm2 = make_layer_box("Add & Norm (+ 残差)", OK_CLR, h=0.5)

        block = VGroup(attention, add_norm1, ffn, add_norm2)
        block.arrange(DOWN, buff=0.25).shift(LEFT * 0.5)

        conn_arrows = VGroup(*[
            Arrow(
                block[i].get_bottom(), block[i + 1].get_top(),
                color=MUTED, buff=0.05, stroke_width=1,
            )
            for i in range(3)
        ])

        inp = Arrow(
            attention.get_top() + UP * 0.6, attention.get_top(),
            color=MUTED, buff=0.05, stroke_width=1.5,
        )
        inp_label = Text("输入", font=FONT, font_size=14, color=MUTED)
        inp_label.next_to(inp, UP, buff=0.05)
        out = Arrow(
            add_norm2.get_bottom(), add_norm2.get_bottom() + DOWN * 0.6,
            color=MUTED, buff=0.05, stroke_width=1.5,
        )
        out_label = Text("输出", font=FONT, font_size=14, color=MUTED)
        out_label.next_to(out, DOWN, buff=0.05)

        self.play(
            FadeIn(attention, shift=UP * 0.2),
            FadeIn(add_norm1, shift=UP * 0.2),
            FadeIn(ffn, shift=UP * 0.2),
            FadeIn(add_norm2, shift=UP * 0.2),
            Create(conn_arrows, lag_ratio=0.3),
            FadeIn(inp, inp_label),
            FadeIn(out, out_label),
            run_time=1.5,
        )
        self.pad_segment()

        self.show_sub("一个注意力加前馈网络的组合构成\n一个Transformer块。\n把多个块堆叠起来，学习更抽象的特征。")

        block_frame = SurroundingRectangle(
            block, color=ACCENT, buff=0.2,
            corner_radius=0.15, stroke_width=1.5,
        )
        times_n = Text("  N", font_size=24, color=ACCENT)
        times_n.next_to(block_frame, RIGHT, buff=0.15)
        self.play(Create(block_frame), Write(times_n), run_time=0.8)

        stacked = VGroup()
        for i in range(6):
            clr = ACCENT if i < 3 else DEC_CLR
            mini = RoundedRectangle(
                width=1.5, height=0.5, corner_radius=0.08,
                fill_color=CARD_BG, fill_opacity=0.8,
                stroke_color=clr, stroke_width=1,
            )
            layer_num = Text(f"Layer {i + 1}", font_size=10, color=clr)
            layer_num.move_to(mini)
            stacked.add(VGroup(mini, layer_num))
        stacked.arrange(DOWN, buff=0.08).to_edge(RIGHT, buff=1)

        stack_title = Text("堆叠", font=FONT, font_size=14, color=ACCENT)
        stack_title.next_to(stacked, UP, buff=0.2)
        self.play(
            FadeIn(stacked, lag_ratio=0.1), Write(stack_title), run_time=1.5,
        )
        self.pad_segment()

        self.clear_all()


class S07_ApplicationScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("Transformer的影响远超机器翻译。\nGPT用解码器生成文本，\nBERT用编码器理解语义。")

        sec = Text("Transformer 家族", font=FONT, font_size=24, color=MUTED)
        sec.to_edge(UP, buff=0.4)
        self.play(FadeIn(sec, shift=DOWN * 0.15), run_time=0.3)

        apps = [
            ("GPT", "解码器", "文本生成", "#2ecc71", "GPT-4, ChatGPT"),
            ("BERT", "编码器", "语义理解", "#3498db", "搜索, 分类"),
            ("ViT", "编码器", "图像识别", "#e67e22", "视觉理解"),
        ]

        cards = VGroup()
        for name, arch, task, clr, examples in apps:
            card = RoundedRectangle(
                width=3.5, height=3.2, corner_radius=0.18,
                fill_color=CARD_BG, fill_opacity=0.95,
                stroke_color=clr, stroke_width=2,
            )
            n_txt = Text(name, font_size=36, color=clr)
            arch_tag = RoundedRectangle(
                width=1.8, height=0.35, corner_radius=0.06,
                fill_color=clr, fill_opacity=0.15, stroke_width=0,
            )
            arch_text = Text(arch, font=FONT, font_size=12, color=clr)
            arch_text.move_to(arch_tag)
            arch_grp = VGroup(arch_tag, arch_text)
            t_txt = Text(task, font=FONT, font_size=16, color=WHITE)
            sep = Line(
                LEFT * 1, RIGHT * 1, color=clr,
                stroke_width=1, stroke_opacity=0.4,
            )
            ex_txt = Text(examples, font=FONT, font_size=12, color=MUTED)
            content = VGroup(n_txt, arch_grp, t_txt, sep, ex_txt)
            content.arrange(DOWN, buff=0.2).move_to(card)
            cards.add(VGroup(card, content))

        cards.arrange(RIGHT, buff=0.3)
        for card in cards:
            self.play(FadeIn(card, shift=UP * 0.4, scale=0.7), run_time=0.5)
        self.pad_segment()

        self.show_sub("Vision Transformer证明了\n注意力不只适用于文字。\n如今Transformer已成为深度学习的通用架构。")

        self.play(
            cards[0].animate.set_opacity(0.3),
            cards[1].animate.set_opacity(0.3),
            run_time=0.5,
        )

        badge = RoundedRectangle(
            width=8, height=0.8, corner_radius=0.12,
            fill_color=CARD_BG, fill_opacity=0.9,
            stroke_color=ACCENT, stroke_width=2,
        ).to_edge(DOWN, buff=1.2)
        badge_text = Text("深度学习的通用架构", font=FONT, font_size=22, color=ACCENT)
        badge_text.move_to(badge)
        self.play(FadeIn(badge, badge_text, shift=UP * 0.2), run_time=0.8)
        self.pad_segment()

        self.clear_all()


class S08_OutroScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("从一篇论文到改变整个人工智能领域，\nTransformer用简洁优雅的思想，\n重新定义了机器理解世界的方式。")

        line = Line(LEFT * 5, RIGHT * 5, color=MUTED, stroke_width=1.5)
        line.shift(UP * 0.5)
        self.play(Create(line), run_time=0.8)

        dot_2017 = Dot(LEFT * 4 + UP * 0.5, color=ACCENT, radius=0.1)
        lbl_2017 = Text("2017", font_size=18, color=ACCENT)
        lbl_2017.next_to(dot_2017, DOWN, buff=0.2)
        paper = Text("Attention Is\nAll You Need", font_size=12, color=MUTED)
        paper.next_to(dot_2017, UP, buff=0.2)
        self.play(FadeIn(dot_2017, lbl_2017, paper), run_time=0.6)

        milestones = [
            (LEFT * 1.5, "2018", "GPT & BERT"),
            (RIGHT * 0.5, "2020", "GPT-3"),
            (RIGHT * 2.5, "2022", "ChatGPT"),
            (RIGHT * 4, "2024", "GPT-4o"),
        ]
        for pos_x, year, name in milestones:
            pos = pos_x + UP * 0.5
            d = Dot(pos, color=ACCENT, radius=0.06)
            y = Text(year, font_size=14, color=ACCENT).next_to(d, DOWN, buff=0.15)
            n = Text(name, font_size=11, color=MUTED).next_to(d, UP, buff=0.15)
            self.play(FadeIn(d, y, n), run_time=0.35)
        self.pad_segment()

        self.show_sub("注意力，就是你所需要的一切。")
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

        final = Text("Attention Is All You Need", font_size=44, color=ACCENT)
        glow = Circle(
            radius=3.5, color=ACCENT, stroke_width=0.5, stroke_opacity=0.15,
            fill_opacity=0.02, fill_color=ACCENT,
        )
        self.play(FadeIn(glow), run_time=0.5)
        self.play(Write(final), run_time=2)
        self.pad_segment()

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=2)
        self._save_stamps()
