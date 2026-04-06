"""
Simplex Consensus Algorithm — 10-minute science-popularization Manim animation.
Narration-first design: each scene carries subtitle text matching script.md.
Audio sync via timestamp logging + ffmpeg post-merge.
"""

from manim import *
import numpy as np
from base import (
    SubtitleMixin, BG, PROVER_CLR, VERIFIER_CLR,
    OK_CLR, FAIL_CLR, ACCENT, MUTED, CARD_BG, FONT,
)

LEADER_CLR = "#3498db"
NODE_CLR = "#2ecc71"
EVIL_CLR = "#e74c3c"
DUMMY_CLR = "#9b59b6"
FINALIZE_CLR = "#f39c12"


def make_node(label, color, pos, radius=0.35):
    c = Circle(radius=radius, color=color, stroke_width=3, fill_color=color, fill_opacity=0.15)
    t = Text(label, font_size=22, color=color)
    g = VGroup(c, t).move_to(pos)
    return g


def make_server(pos, color=MUTED, label=""):
    body = RoundedRectangle(
        width=0.7, height=0.9, corner_radius=0.08,
        fill_color=CARD_BG, fill_opacity=0.9,
        stroke_color=color, stroke_width=2,
    )
    lights = VGroup(*[
        Dot(radius=0.04, color=color).shift(UP * 0.25 + LEFT * 0.15 + RIGHT * i * 0.15)
        for i in range(3)
    ])
    g = VGroup(body, lights).move_to(pos)
    if label:
        lbl = Text(label, font_size=14, color=color).next_to(g, DOWN, buff=0.1)
        g.add(lbl)
    return g


# ═════════════════════════════════════════════════════════════════════════════
# Part 1 · 起 — Hook & Title
# ═════════════════════════════════════════════════════════════════════════════

class S01_HookScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("你在手机上转了一笔账。银行的服务器收到了请求——但不是一台服务器，而是几十台。它们必须对这笔交易的结果达成一致。")

        phone = RoundedRectangle(
            width=0.8, height=1.4, corner_radius=0.12,
            fill_color="#2c3e50", fill_opacity=0.9,
            stroke_color=MUTED, stroke_width=2,
        ).shift(LEFT * 4.5)
        phone_screen = RoundedRectangle(
            width=0.6, height=1.0, corner_radius=0.06,
            fill_color="#34495e", fill_opacity=0.8, stroke_width=0,
        ).move_to(phone).shift(UP * 0.05)
        phone_txt = Text("¥", font_size=20, color=ACCENT).move_to(phone_screen)
        phone_grp = VGroup(phone, phone_screen, phone_txt)

        servers = VGroup(*[
            make_server(RIGHT * (i * 1.1 - 0.5) + UP * (0.8 if i % 2 == 0 else -0.8), color=NODE_CLR)
            for i in range(6)
        ])

        self.play(FadeIn(phone_grp, shift=UP * 0.3), run_time=0.6)
        arrows = VGroup(*[
            Arrow(phone.get_right(), s[0].get_left(), buff=0.15, color=ACCENT, stroke_width=2, max_tip_length_to_length_ratio=0.1)
            for s in servers
        ])
        self.play(FadeIn(servers, lag_ratio=0.1), run_time=1)
        self.play(*[GrowArrow(a) for a in arrows], run_time=0.8)
        self.pad_segment()

        self.show_sub("现在想象一下：如果其中有几台服务器被黑客入侵了呢？它们可能故意发送虚假消息，对不同的伙伴说不同的话，试图搅乱整个系统。")

        evil_indices = [1, 4]
        evil_anims = []
        for idx in evil_indices:
            evil_anims.append(servers[idx][0].animate.set_stroke(color=EVIL_CLR))
            evil_anims.append(servers[idx][1].animate.set_color(EVIL_CLR))
        self.play(*evil_anims, run_time=0.6)

        evil_msgs = VGroup()
        for idx in evil_indices:
            for target in [0, 2, 3, 5]:
                if target != idx:
                    msg = Arrow(
                        servers[idx][0].get_center(),
                        servers[target][0].get_center(),
                        buff=0.4, color=EVIL_CLR, stroke_width=1.5,
                        max_tip_length_to_length_ratio=0.12,
                    )
                    evil_msgs.add(msg)
        self.play(FadeIn(evil_msgs, lag_ratio=0.05), run_time=1.5)
        self.pad_segment()

        self.show_sub("在不可信的网络中，如何让诚实的节点达成一致？这个问题困扰了计算机科学家四十年。")
        self.play(FadeOut(phone_grp, arrows, servers, evil_msgs), run_time=0.6)
        q = Text("?", font_size=120, color=ACCENT)
        self.play(FadeIn(q, scale=0.3), run_time=0.8)
        self.wait(1)

        self.clear_all()


class S02_TitleScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("2023 年，康奈尔大学的 Benjamin Chan 和 Rafael Pass 发表了一篇论文。")

        paper = RoundedRectangle(
            width=4, height=5, corner_radius=0.12,
            fill_color="#f5f5f5", fill_opacity=0.95,
            stroke_color=MUTED, stroke_width=2,
        )
        ptitle = Text("Simplex Consensus:\nA Simple and Fast\nConsensus Protocol", font_size=18, color="#1a1a2e", line_spacing=1.3)
        authors = Text("Benjamin Chan, Rafael Pass\nCornell University, 2023", font_size=12, color=MUTED, line_spacing=1.2)
        ptitle.move_to(paper).shift(UP * 0.6)
        authors.next_to(ptitle, DOWN, buff=0.6)
        paper_grp = VGroup(paper, ptitle, authors)
        self.play(FadeIn(paper_grp, shift=UP * 0.5), run_time=1.2)
        self.pad_segment()

        self.show_sub("他们的协议叫做 Simplex——名字本身就是一个宣言：共识可以很简单。")
        self.play(paper_grp.animate.scale(0.4).to_edge(UL, buff=0.5), run_time=0.8)

        title_cn = Text("Simplex 共识算法", font=FONT, font_size=52, color=WHITE)
        title_en = Text("Simple and Fast Consensus", font_size=28, color=ACCENT)
        titles = VGroup(title_cn, title_en).arrange(DOWN, buff=0.35)
        self.play(Write(title_cn), run_time=1.2)
        self.play(FadeIn(title_en, shift=UP * 0.3), run_time=0.6)
        self.pad_segment()

        self.show_sub("今天我们就来拆解这个算法。我们会先聊一些必要的预备知识，然后一步步看 Simplex 到底是怎么工作的。")

        roadmap_items = [
            ("1. 拜占庭将军问题", EVIL_CLR),
            ("2. 共识协议基础", NODE_CLR),
            ("3. Simplex 协议详解", LEADER_CLR),
            ("4. 安全性与活性", ACCENT),
        ]
        roadmap = VGroup()
        for txt, clr in roadmap_items:
            item = Text(txt, font=FONT, font_size=22, color=clr)
            roadmap.add(item)
        roadmap.arrange(DOWN, aligned_edge=LEFT, buff=0.3).shift(DOWN * 0.8)
        for item in roadmap:
            self.play(FadeIn(item, shift=RIGHT * 0.3), run_time=0.4)

        self.clear_all()


# ═════════════════════════════════════════════════════════════════════════════
# Part 2 · 承 — Build
# ═════════════════════════════════════════════════════════════════════════════

class S03_ByzantineScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("拜占庭将军问题", font=FONT, font_size=42, color=WHITE)
        self.play(Write(sec), run_time=0.6)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3))

        self.show_sub("先来认识一个经典问题。公元前的拜占庭帝国，几位将军围攻一座城池。他们需要统一行动：要么全体进攻，要么全体撤退。")

        castle = RoundedRectangle(
            width=1.5, height=2, corner_radius=0.1,
            fill_color="#4a4a6a", fill_opacity=0.8,
            stroke_color=MUTED, stroke_width=3,
        )
        castle_top = Triangle(fill_color="#4a4a6a", fill_opacity=0.8, stroke_color=MUTED, stroke_width=3)
        castle_top.scale(0.5).next_to(castle, UP, buff=-0.05)
        castle_lbl = Text("城池", font=FONT, font_size=16, color=MUTED).move_to(castle)
        castle_grp = VGroup(castle, castle_top, castle_lbl)

        generals = VGroup()
        n_gen = 5
        for i in range(n_gen):
            angle = PI / 2 + i * 2 * PI / n_gen
            pos = np.array([2.5 * np.cos(angle), 2.5 * np.sin(angle), 0])
            color = EVIL_CLR if i == 2 else NODE_CLR
            label = f"G{i+1}"
            g = make_node(label, color, pos, radius=0.3)
            generals.add(g)

        self.play(FadeIn(castle_grp), run_time=0.6)
        self.play(FadeIn(generals, lag_ratio=0.15), run_time=1)
        self.pad_segment()

        self.show_sub("但问题是——其中可能有叛徒。叛徒会对不同的将军发送矛盾的命令，试图让他们行动不一致。")

        traitor = generals[2]
        traitor_label = Text("叛徒!", font=FONT, font_size=16, color=EVIL_CLR).next_to(traitor, DOWN, buff=0.15)
        self.play(FadeIn(traitor_label), run_time=0.4)

        msg_a = Text("进攻!", font=FONT, font_size=14, color=EVIL_CLR)
        msg_b = Text("撤退!", font=FONT, font_size=14, color=EVIL_CLR)
        msg_a.next_to(traitor, UL, buff=0.3)
        msg_b.next_to(traitor, UR, buff=0.3)
        arr_a = Arrow(traitor[0].get_center(), generals[1][0].get_center(), buff=0.35, color=EVIL_CLR, stroke_width=2)
        arr_b = Arrow(traitor[0].get_center(), generals[3][0].get_center(), buff=0.35, color=EVIL_CLR, stroke_width=2)
        self.play(GrowArrow(arr_a), FadeIn(msg_a), run_time=0.5)
        self.play(GrowArrow(arr_b), FadeIn(msg_b), run_time=0.5)
        self.wait(1)
        self.pad_segment()

        self.show_sub("这就是著名的「拜占庭将军问题」。翻译成计算机语言就是：n 个节点中，最多 f 个是恶意的。")
        self.play(FadeOut(castle_grp, traitor_label, msg_a, msg_b, arr_a, arr_b), run_time=0.5)

        nodes = VGroup()
        for i in range(n_gen):
            angle = PI / 2 + i * 2 * PI / n_gen
            pos = np.array([2 * np.cos(angle), 2 * np.sin(angle), 0]) + DOWN * 0.3
            color = EVIL_CLR if i == 2 else NODE_CLR
            label = f"N{i+1}"
            n_mob = make_node(label, color, pos, radius=0.28)
            nodes.add(n_mob)

        self.play(ReplacementTransform(generals, nodes), run_time=1)
        n_label = MathTex(r"n = 5", font_size=32, color=WHITE).shift(RIGHT * 4 + UP * 1)
        f_label = MathTex(r"f = 1", font_size=32, color=EVIL_CLR).next_to(n_label, DOWN, buff=0.3)
        self.play(Write(n_label), Write(f_label), run_time=0.6)
        self.pad_segment()

        self.show_sub("数学家证明了一个关键结论：要容忍 f 个拜占庭节点，我们至少需要 n 大于 3f。换句话说，恶意节点必须少于总数的三分之一。")

        formula = MathTex(r"n", r">", r"3f", font_size=48)
        formula[0].set_color(NODE_CLR)
        formula[2].set_color(EVIL_CLR)
        formula.shift(RIGHT * 4 + DOWN * 0.5)
        box = SurroundingRectangle(formula, color=ACCENT, buff=0.15, corner_radius=0.08)
        self.play(Write(formula), Create(box), run_time=1)
        self.pad_segment()

        self.show_sub("而且做决定时，我们需要至少三分之二的票数——也就是所谓的法定人数，quorum。这样即使恶意节点同时给两边投票，两个矛盾的决定也不可能同时凑齐法定人数。")

        self.play(FadeOut(nodes, n_label, f_label, formula, box), run_time=0.5)

        big_circle = Circle(radius=2, color=WHITE, stroke_width=2).shift(DOWN * 0.3)
        big_label = MathTex("n", font_size=28, color=WHITE).next_to(big_circle, UP, buff=0.1)

        q1 = Arc(radius=2, start_angle=PI * 0.1, angle=PI * 0.9, color=LEADER_CLR, stroke_width=6).shift(DOWN * 0.3)
        q1_label = Text("Quorum A", font_size=16, color=LEADER_CLR).shift(LEFT * 1.5 + DOWN * 0.3)
        q2 = Arc(radius=2, start_angle=PI * 1.0, angle=PI * 0.9, color=FINALIZE_CLR, stroke_width=6).shift(DOWN * 0.3)
        q2_label = Text("Quorum B", font_size=16, color=FINALIZE_CLR).shift(RIGHT * 1.5 + DOWN * 0.3)
        overlap = Text("重叠 ≥ 1 诚实节点", font=FONT, font_size=16, color=OK_CLR).shift(DOWN * 2.6)

        self.play(Create(big_circle), Write(big_label), run_time=0.5)
        self.play(Create(q1), Write(q1_label), run_time=0.5)
        self.play(Create(q2), Write(q2_label), run_time=0.5)
        self.play(FadeIn(overlap), run_time=0.4)

        self.clear_all()


class S04_ConsensusBasicsScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("共识协议的两个目标", font=FONT, font_size=36, color=WHITE)
        self.play(Write(sec), run_time=0.5)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3))

        self.show_sub("有了这些基础，我们来看共识协议到底需要保证什么。")
        self.wait(1)
        self.pad_segment()

        self.show_sub("第一，一致性。任何两个诚实节点输出的交易日志，要么相同，要么一个是另一个的前缀。绝对不能出现分叉。")

        card1 = RoundedRectangle(
            width=5.5, height=2.2, corner_radius=0.15,
            fill_color=CARD_BG, fill_opacity=0.9,
            stroke_color=OK_CLR, stroke_width=2,
        ).shift(UP * 0.8)
        c1_title = Text("一致性 Consistency", font=FONT, font_size=24, color=OK_CLR)
        c1_desc = Text("诚实节点的日志不分叉", font=FONT, font_size=18, color=WHITE)

        log_a = VGroup(*[
            RoundedRectangle(width=0.6, height=0.4, corner_radius=0.05, fill_color=OK_CLR, fill_opacity=0.3, stroke_color=OK_CLR, stroke_width=1)
            for _ in range(4)
        ]).arrange(RIGHT, buff=0.08)
        log_b = VGroup(*[
            RoundedRectangle(width=0.6, height=0.4, corner_radius=0.05, fill_color=OK_CLR, fill_opacity=0.3, stroke_color=OK_CLR, stroke_width=1)
            for _ in range(4)
        ]).arrange(RIGHT, buff=0.08)
        log_a_lbl = Text("节点 A:", font=FONT, font_size=14, color=MUTED)
        log_b_lbl = Text("节点 B:", font=FONT, font_size=14, color=MUTED)
        la = VGroup(log_a_lbl, log_a).arrange(RIGHT, buff=0.15)
        lb = VGroup(log_b_lbl, log_b).arrange(RIGHT, buff=0.15)
        logs = VGroup(la, lb).arrange(DOWN, buff=0.15)
        c1_content = VGroup(c1_title, c1_desc, logs).arrange(DOWN, buff=0.2).move_to(card1)

        fork_x = Text("✗ 分叉", font=FONT, font_size=18, color=FAIL_CLR).next_to(card1, RIGHT, buff=0.3)

        self.play(FadeIn(card1), run_time=0.3)
        self.play(Write(c1_title), Write(c1_desc), run_time=0.5)
        self.play(FadeIn(logs), run_time=0.5)
        self.play(FadeIn(fork_x), run_time=0.3)
        self.pad_segment()

        self.show_sub("第二，活性。在网络状况良好的时候，新的交易必须能在有限时间内被确认。系统不能卡死。")

        card2 = RoundedRectangle(
            width=5.5, height=2.0, corner_radius=0.15,
            fill_color=CARD_BG, fill_opacity=0.9,
            stroke_color=ACCENT, stroke_width=2,
        ).shift(DOWN * 1.5)
        c2_title = Text("活性 Liveness", font=FONT, font_size=24, color=ACCENT)
        c2_desc = Text("网络正常时，交易必须被确认", font=FONT, font_size=18, color=WHITE)

        tx_box = RoundedRectangle(width=0.8, height=0.4, corner_radius=0.05, fill_color=ACCENT, fill_opacity=0.3, stroke_color=ACCENT, stroke_width=1)
        tx_txt = Text("tx", font_size=14, color=ACCENT).move_to(tx_box)
        check = Text("✓", font_size=28, color=OK_CLR).next_to(tx_box, RIGHT, buff=0.3)
        tx_grp = VGroup(tx_box, tx_txt, check)
        c2_content = VGroup(c2_title, c2_desc, tx_grp).arrange(DOWN, buff=0.2).move_to(card2)

        self.play(FadeIn(card2), Write(c2_title), Write(c2_desc), run_time=0.5)
        self.play(FadeIn(tx_grp), run_time=0.4)
        self.pad_segment()

        self.show_sub("还有一个关键假设：部分同步网络。好的时候，消息在 Δ 秒内送达；坏的时候，完全没保证。我们要求：好的时候能推进，坏的时候至少不能出错。")

        self.play(FadeOut(card1, c1_content, fork_x, card2, c2_content), run_time=0.5)

        net_good = VGroup(
            Text("好网络", font=FONT, font_size=20, color=OK_CLR),
            MathTex(r"\text{delay} \leq \Delta", font_size=24, color=OK_CLR),
        ).arrange(DOWN, buff=0.15).shift(LEFT * 3)
        net_bad = VGroup(
            Text("坏网络", font=FONT, font_size=20, color=FAIL_CLR),
            Text("无保证", font=FONT, font_size=18, color=FAIL_CLR),
        ).arrange(DOWN, buff=0.15).shift(RIGHT * 3)
        arrow_mid = Arrow(LEFT * 1, RIGHT * 1, color=MUTED, stroke_width=2)
        delta_label = MathTex(r"\Delta", font_size=36, color=ACCENT).shift(UP * 1.5)

        self.play(FadeIn(net_good), FadeIn(net_bad), GrowArrow(arrow_mid), Write(delta_label), run_time=1)

        req = VGroup(
            Text("好网络 → 推进", font=FONT, font_size=20, color=OK_CLR),
            Text("坏网络 → 不出错", font=FONT, font_size=20, color=FAIL_CLR),
        ).arrange(DOWN, buff=0.2).shift(DOWN * 1.5)
        self.play(FadeIn(req, shift=UP * 0.2), run_time=0.6)

        self.clear_all()


class S05_PriorWorkScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("前人的探索", font=FONT, font_size=36, color=WHITE)
        self.play(Write(sec), run_time=0.5)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3))

        self.show_sub("这些问题并不新鲜。1999 年的 PBFT 协议是开山之作，但它的协议流程极其复杂，光是论文就有几十页。")

        pbft_card = RoundedRectangle(
            width=4.5, height=3, corner_radius=0.15,
            fill_color=CARD_BG, fill_opacity=0.9,
            stroke_color=MUTED, stroke_width=2,
        ).shift(LEFT * 3)
        pbft_title = Text("PBFT (1999)", font_size=22, color=MUTED)
        pbft_lines = VGroup(*[
            Line(LEFT * 1.5, RIGHT * 1.5, color=MUTED, stroke_width=1).shift(DOWN * i * 0.25)
            for i in range(8)
        ]).scale(0.7)
        pbft_label = Text("复杂!", font=FONT, font_size=20, color=FAIL_CLR)
        pbft_content = VGroup(pbft_title, pbft_lines, pbft_label).arrange(DOWN, buff=0.2).move_to(pbft_card)
        self.play(FadeIn(pbft_card, pbft_content), run_time=0.8)
        self.pad_segment()

        self.show_sub("后来的 Tendermint 更简洁，但有一个效率瓶颈：每轮的 leader 需要先等待 2Δ 时间来收集信息，超时设为 6Δ。一个恶意 leader 可以浪费整整 6Δ 的时间。")

        tend_card = RoundedRectangle(
            width=4.5, height=3, corner_radius=0.15,
            fill_color=CARD_BG, fill_opacity=0.9,
            stroke_color=VERIFIER_CLR, stroke_width=2,
        ).shift(RIGHT * 3)
        tend_title = Text("Tendermint", font_size=22, color=VERIFIER_CLR)

        timeline = Line(LEFT * 1.5, RIGHT * 1.5, color=MUTED, stroke_width=2)
        wait_bar = Rectangle(width=0.8, height=0.25, fill_color=VERIFIER_CLR, fill_opacity=0.3, stroke_color=VERIFIER_CLR, stroke_width=1)
        wait_bar.align_to(timeline, LEFT).shift(UP * 0.15)
        wait_lbl = Text("2Δ 等待", font=FONT, font_size=12, color=VERIFIER_CLR).next_to(wait_bar, UP, buff=0.05)
        timeout_lbl = Text("超时: 6Δ", font=FONT, font_size=16, color=FAIL_CLR)

        tend_content = VGroup(tend_title, VGroup(timeline, wait_bar, wait_lbl), timeout_lbl).arrange(DOWN, buff=0.3).move_to(tend_card)
        self.play(FadeIn(tend_card, tend_content), run_time=0.8)
        self.pad_segment()

        self.show_sub("Simplex 的目标很明确：更简单的协议、更短的超时、同样的安全性。")

        self.play(FadeOut(pbft_card, pbft_content, tend_card, tend_content), run_time=0.5)

        headers = VGroup(
            Text("", font_size=1),
            Text("Tendermint", font_size=20, color=VERIFIER_CLR),
            Text("Simplex", font_size=20, color=ACCENT),
        ).arrange(RIGHT, buff=1.5)

        rows_data = [
            ("Leader 等待", "2Δ", "0"),
            ("超时", "6Δ", "3Δ"),
            ("安全性", "✓", "✓"),
        ]
        table = VGroup(headers)
        for label, tend_val, simp_val in rows_data:
            row = VGroup(
                Text(label, font=FONT, font_size=18, color=WHITE),
                Text(tend_val, font_size=18, color=VERIFIER_CLR),
                Text(simp_val, font_size=18, color=ACCENT),
            ).arrange(RIGHT, buff=1.5)
            table.add(row)
        table.arrange(DOWN, buff=0.35)
        for item in table:
            self.play(FadeIn(item, shift=RIGHT * 0.2), run_time=0.3)

        self.clear_all()


# ═════════════════════════════════════════════════════════════════════════════
# Part 3 · 转 — Deepen
# ═════════════════════════════════════════════════════════════════════════════

class S06_SimplexOverviewScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("Simplex 协议总览", font=FONT, font_size=36, color=WHITE)
        self.play(Write(sec), run_time=0.5)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3))

        self.show_sub("现在进入正题。Simplex 的结构非常清晰。")
        self.wait(1)
        self.pad_segment()

        self.show_sub("协议按「迭代」推进，每一轮有一个随机选出的 leader。")

        iters = VGroup()
        for i in range(5):
            box = RoundedRectangle(
                width=2, height=1.2, corner_radius=0.1,
                fill_color=CARD_BG, fill_opacity=0.9,
                stroke_color=LEADER_CLR if i < 4 else MUTED, stroke_width=2,
            )
            h_lbl = MathTex(f"h={i+1}" if i < 4 else r"\cdots", font_size=20, color=WHITE).move_to(box).shift(UP * 0.25)
            l_lbl = Text(f"Leader: N{(i*3) % 5 + 1}" if i < 4 else "", font=FONT, font_size=14, color=LEADER_CLR)
            l_lbl.move_to(box).shift(DOWN * 0.15)
            iters.add(VGroup(box, h_lbl, l_lbl))
        iters.arrange(RIGHT, buff=0.15).scale(0.85).shift(UP * 0.5)

        for it in iters:
            self.play(FadeIn(it, shift=RIGHT * 0.2), run_time=0.3)
        self.pad_segment()

        self.show_sub("每轮的流程只有三步。第一步，leader 提出一个区块提案，广播给所有人。")

        self.play(FadeOut(iters), run_time=0.4)
        step1 = VGroup(
            Text("1", font_size=28, color=LEADER_CLR),
            Text("Leader 提案", font=FONT, font_size=22, color=LEADER_CLR),
        ).arrange(RIGHT, buff=0.3).shift(UP * 2)

        leader = make_node("L", LEADER_CLR, LEFT * 3 + DOWN * 0.3, radius=0.35)
        followers = VGroup(*[
            make_node(f"N{i+1}", NODE_CLR, RIGHT * (i * 1.8 - 0.5) + DOWN * 0.3, radius=0.3)
            for i in range(3)
        ])
        block = RoundedRectangle(
            width=1.2, height=0.6, corner_radius=0.08,
            fill_color=LEADER_CLR, fill_opacity=0.3,
            stroke_color=LEADER_CLR, stroke_width=2,
        ).next_to(leader, UP, buff=0.15)
        block_lbl = Text("Block", font_size=14, color=LEADER_CLR).move_to(block)

        self.play(FadeIn(step1), FadeIn(leader), FadeIn(followers, lag_ratio=0.2), run_time=0.6)
        self.play(FadeIn(block, block_lbl), run_time=0.3)
        broadcast_arrows = VGroup(*[
            Arrow(leader[0].get_center(), f[0].get_center(), buff=0.4, color=LEADER_CLR, stroke_width=2, max_tip_length_to_length_ratio=0.1)
            for f in followers
        ])
        self.play(*[GrowArrow(a) for a in broadcast_arrows], run_time=0.6)
        self.pad_segment()

        self.show_sub("第二步，节点验证提案的合法性，如果通过就投票。当收集到至少三分之二的投票，这个区块就被「公证」了——notarized。")

        step2 = VGroup(
            Text("2", font_size=28, color=NODE_CLR),
            Text("投票 → 公证 (Notarization)", font=FONT, font_size=22, color=NODE_CLR),
        ).arrange(RIGHT, buff=0.3).next_to(step1, DOWN, buff=0.15, aligned_edge=LEFT)

        self.play(FadeOut(broadcast_arrows, block, block_lbl), FadeIn(step2), run_time=0.4)
        votes = VGroup()
        for f in followers:
            v = Text("✓", font_size=22, color=NODE_CLR).next_to(f, UP, buff=0.1)
            votes.add(v)
        leader_vote = Text("✓", font_size=22, color=LEADER_CLR).next_to(leader, RIGHT, buff=0.15)
        self.play(FadeIn(votes, lag_ratio=0.2), FadeIn(leader_vote), run_time=0.6)

        nota_label = Text("Notarized!", font_size=24, color=ACCENT).shift(DOWN * 2)
        nota_box = SurroundingRectangle(nota_label, color=ACCENT, buff=0.12, corner_radius=0.08)
        self.play(Write(nota_label), Create(nota_box), run_time=0.5)
        self.pad_segment()

        self.show_sub("第三步，看到公证区块后，节点进入下一轮，并发送 finalize 消息。如果三分之二的节点都发了 finalize，这一轮就被最终确认了。")

        step3 = VGroup(
            Text("3", font_size=28, color=FINALIZE_CLR),
            Text("Finalize → 最终确认", font=FONT, font_size=22, color=FINALIZE_CLR),
        ).arrange(RIGHT, buff=0.3).next_to(step2, DOWN, buff=0.15, aligned_edge=LEFT)

        self.play(FadeIn(step3), run_time=0.3)
        fin_msgs = VGroup()
        for f in followers:
            fm = Text("fin", font_size=16, color=FINALIZE_CLR).next_to(f, DOWN, buff=0.15)
            fin_msgs.add(fm)
        leader_fin = Text("fin", font_size=16, color=FINALIZE_CLR).next_to(leader, DOWN, buff=0.15)
        self.play(FadeIn(fin_msgs, lag_ratio=0.15), FadeIn(leader_fin), run_time=0.5)
        confirmed = Text("最终确认 ✓", font=FONT, font_size=28, color=OK_CLR).shift(DOWN * 2)
        self.play(ReplacementTransform(VGroup(nota_label, nota_box), confirmed), run_time=0.5)
        self.pad_segment()

        self.show_sub("但如果 leader 是恶意的，迟迟不提案呢？每个节点有一个 3Δ 的计时器。超时后，节点投票给一个「空块」——dummy block，保证协议不会卡死。")

        self.play(FadeOut(step1, step2, step3, leader, followers, votes, leader_vote, fin_msgs, leader_fin, confirmed), run_time=0.5)

        timer = VGroup(
            Text("3Δ", font_size=36, color=DUMMY_CLR),
            Text("超时!", font=FONT, font_size=22, color=DUMMY_CLR),
        ).arrange(DOWN, buff=0.2).shift(LEFT * 2)

        dummy = RoundedRectangle(
            width=2, height=0.8, corner_radius=0.1,
            fill_color=DUMMY_CLR, fill_opacity=0.2,
            stroke_color=DUMMY_CLR, stroke_width=2,
        ).shift(RIGHT * 2)
        dummy_lbl = Text("Dummy Block", font_size=18, color=DUMMY_CLR).move_to(dummy)
        arrow = Arrow(timer.get_right(), dummy.get_left(), buff=0.3, color=DUMMY_CLR, stroke_width=2)

        self.play(FadeIn(timer), run_time=0.5)
        self.play(GrowArrow(arrow), FadeIn(dummy, dummy_lbl), run_time=0.6)

        self.clear_all()


class S07_ProtocolDetailScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("完整流程演示", font=FONT, font_size=36, color=WHITE)
        self.play(Write(sec), run_time=0.5)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3))

        self.show_sub("让我们用一个具体例子来走一遍完整流程。假设有四个节点，其中一个是恶意的。")

        node_positions = [LEFT * 4 + DOWN * 0.5, LEFT * 1.3 + DOWN * 0.5, RIGHT * 1.3 + DOWN * 0.5, RIGHT * 4 + DOWN * 0.5]
        node_labels = ["A", "B", "C", "D"]
        node_colors = [LEADER_CLR, NODE_CLR, NODE_CLR, EVIL_CLR]

        nodes = VGroup()
        for i in range(4):
            n = make_node(node_labels[i], node_colors[i], node_positions[i], radius=0.35)
            nodes.add(n)

        role_labels = VGroup(
            Text("Leader", font_size=14, color=LEADER_CLR).next_to(nodes[0], DOWN, buff=0.15),
            Text("诚实", font=FONT, font_size=14, color=NODE_CLR).next_to(nodes[1], DOWN, buff=0.15),
            Text("诚实", font=FONT, font_size=14, color=NODE_CLR).next_to(nodes[2], DOWN, buff=0.15),
            Text("恶意", font=FONT, font_size=14, color=EVIL_CLR).next_to(nodes[3], DOWN, buff=0.15),
        )

        n_eq = MathTex(r"n=4,\; f=1", font_size=24, color=MUTED).to_edge(UR, buff=0.5)
        self.play(FadeIn(nodes, lag_ratio=0.15), FadeIn(role_labels, lag_ratio=0.15), Write(n_eq), run_time=1)
        self.pad_segment()

        self.show_sub("第一轮，节点 A 被选为 leader。A 打包交易，生成一个新区块，广播给 B、C、D。")

        block = RoundedRectangle(
            width=1.5, height=0.6, corner_radius=0.08,
            fill_color=LEADER_CLR, fill_opacity=0.3,
            stroke_color=LEADER_CLR, stroke_width=2,
        ).next_to(nodes[0], UP, buff=0.2)
        block_txt = Text("Block h=1", font_size=14, color=LEADER_CLR).move_to(block)

        self.play(FadeIn(block, block_txt, shift=UP * 0.2), run_time=0.4)

        prop_arrows = VGroup(*[
            Arrow(nodes[0][0].get_center(), nodes[i][0].get_center(), buff=0.4, color=LEADER_CLR, stroke_width=2, max_tip_length_to_length_ratio=0.1)
            for i in [1, 2, 3]
        ])
        self.play(*[GrowArrow(a) for a in prop_arrows], run_time=0.6)
        self.pad_segment()

        self.show_sub("B、C、D 收到提案后验证区块的合法性：交易是否有效？父链是否已公证？如果一切合格，它们各自投票。")

        self.play(FadeOut(prop_arrows), run_time=0.3)
        check_marks = VGroup()
        for i in [1, 2]:
            cm = Text("✓ 验证通过", font=FONT, font_size=12, color=OK_CLR).next_to(nodes[i], UP, buff=0.2)
            check_marks.add(cm)
        evil_q = Text("?", font_size=20, color=EVIL_CLR).next_to(nodes[3], UP, buff=0.2)
        self.play(FadeIn(check_marks, lag_ratio=0.3), FadeIn(evil_q), run_time=0.6)

        vote_arrows = VGroup()
        for i in [1, 2]:
            va = Arrow(nodes[i][0].get_center(), nodes[i][0].get_center() + UP * 0.8, buff=0.1, color=NODE_CLR, stroke_width=2, max_tip_length_to_length_ratio=0.15)
            vt = Text("vote", font_size=12, color=NODE_CLR).next_to(va, RIGHT, buff=0.05)
            vote_arrows.add(VGroup(va, vt))
        self.play(FadeIn(vote_arrows, lag_ratio=0.2), run_time=0.5)
        self.pad_segment()

        self.show_sub("A 也给自己投票。现在我们有了来自 A、B、C 三个诚实节点的投票——三票！大于等于三分之二乘以四，也就是三票——区块被公证了。")

        self.play(FadeOut(check_marks, evil_q, vote_arrows), run_time=0.3)

        vote_count = VGroup(
            MathTex(r"\text{votes} = 3", font_size=28, color=NODE_CLR),
            MathTex(r"\geq \lceil 2n/3 \rceil = \lceil 8/3 \rceil = 3", font_size=24, color=ACCENT),
        ).arrange(DOWN, buff=0.15).shift(DOWN * 2.2)

        nota = Text("Notarized!", font_size=28, color=ACCENT).shift(DOWN * 3.2)
        nota_box = SurroundingRectangle(nota, color=ACCENT, buff=0.1, corner_radius=0.08)

        self.play(Write(vote_count), run_time=0.8)
        self.play(Write(nota), Create(nota_box), run_time=0.5)
        self.pad_segment()

        self.show_sub("恶意节点 D 可能投了票也可能没投，但这不影响结果。公证达成后，A、B、C 发送 finalize 消息并进入第二轮。")

        self.play(FadeOut(block, block_txt, vote_count, nota, nota_box), run_time=0.4)

        fin_labels = VGroup()
        for i in [0, 1, 2]:
            fl = Text("finalize", font_size=14, color=FINALIZE_CLR).next_to(nodes[i], UP, buff=0.2)
            fin_labels.add(fl)
        self.play(FadeIn(fin_labels, lag_ratio=0.15), run_time=0.5)
        self.pad_segment()

        self.show_sub("三个 finalize 达到法定人数——第一轮被最终确认。交易正式写入账本。")

        final_banner = VGroup(
            Text("Round 1: 最终确认 ✓", font=FONT, font_size=26, color=OK_CLR),
        ).shift(DOWN * 2.5)
        final_box = SurroundingRectangle(final_banner, color=OK_CLR, buff=0.15, corner_radius=0.1)
        self.play(FadeIn(final_banner), Create(final_box), run_time=0.6)

        chain = VGroup()
        for i in range(3):
            cb = RoundedRectangle(
                width=1, height=0.5, corner_radius=0.05,
                fill_color=OK_CLR if i == 0 else MUTED, fill_opacity=0.2,
                stroke_color=OK_CLR if i == 0 else MUTED, stroke_width=1.5,
            )
            ct = Text(f"B{i}" if i > 0 else "B1 ✓", font_size=12, color=OK_CLR if i == 0 else MUTED).move_to(cb)
            chain.add(VGroup(cb, ct))
        chain.arrange(RIGHT, buff=0.05).shift(DOWN * 3.5)
        self.play(FadeIn(chain), run_time=0.5)

        self.clear_all()


class S08_KeyInsightScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("核心创新", font=FONT, font_size=42, color=ACCENT)
        self.play(Write(sec), run_time=0.6)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3))

        self.show_sub("现在来看 Simplex 最精妙的设计。")
        self.wait(1.5)
        self.pad_segment()

        self.show_sub("还记得超时后节点会投 dummy block 吗？关键观察是：一个诚实节点，要么发 finalize 消息，要么投 dummy block，但绝不会两者都做。")

        fin_box = RoundedRectangle(
            width=3.5, height=1.5, corner_radius=0.15,
            fill_color=CARD_BG, fill_opacity=0.9,
            stroke_color=FINALIZE_CLR, stroke_width=2,
        ).shift(LEFT * 3)
        fin_title = Text("Finalize", font_size=24, color=FINALIZE_CLR)
        fin_desc = Text("超时前看到公证\n→ 进入下一轮", font=FONT, font_size=16, color=WHITE, line_spacing=1.3)
        VGroup(fin_title, fin_desc).arrange(DOWN, buff=0.15).move_to(fin_box)

        dummy_box = RoundedRectangle(
            width=3.5, height=1.5, corner_radius=0.15,
            fill_color=CARD_BG, fill_opacity=0.9,
            stroke_color=DUMMY_CLR, stroke_width=2,
        ).shift(RIGHT * 3)
        dummy_title = Text("Dummy Vote", font_size=24, color=DUMMY_CLR)
        dummy_desc = Text("3Δ 超时\n→ 投空块", font=FONT, font_size=16, color=WHITE, line_spacing=1.3)
        VGroup(dummy_title, dummy_desc).arrange(DOWN, buff=0.15).move_to(dummy_box)

        vs_txt = Text("互斥!", font=FONT, font_size=28, color=FAIL_CLR)
        cross = VGroup(
            Line(UL * 0.3, DR * 0.3, color=FAIL_CLR, stroke_width=4),
            Line(UR * 0.3, DL * 0.3, color=FAIL_CLR, stroke_width=4),
        )
        vs_grp = VGroup(vs_txt, cross).arrange(DOWN, buff=0.1)

        self.play(FadeIn(fin_box, fin_title, fin_desc), FadeIn(dummy_box, dummy_title, dummy_desc), run_time=0.8)
        self.play(FadeIn(vs_grp, scale=1.3), run_time=0.5)
        self.pad_segment()

        self.show_sub("为什么？因为发 finalize 说明节点在超时前就看到了公证区块，已经进入下一轮。而投 dummy block 说明超时了还没看到公证区块。这两件事不可能同时发生。")

        self.play(FadeOut(fin_box, fin_title, fin_desc, dummy_box, dummy_title, dummy_desc, vs_grp), run_time=0.4)

        timeline = Line(LEFT * 5.5, RIGHT * 5.5, color=MUTED, stroke_width=2).shift(DOWN * 0.3)
        start_dot = Dot(LEFT * 5.5 + DOWN * 0.3, color=WHITE, radius=0.06)
        start_lbl = Text("进入迭代 h", font=FONT, font_size=14, color=MUTED).next_to(start_dot, DOWN, buff=0.1)

        timeout_dot = Dot(RIGHT * 2 + DOWN * 0.3, color=DUMMY_CLR, radius=0.06)
        timeout_lbl = Text("3Δ 超时", font=FONT, font_size=14, color=DUMMY_CLR).next_to(timeout_dot, DOWN, buff=0.1)

        nota_dot = Dot(LEFT * 1 + DOWN * 0.3, color=FINALIZE_CLR, radius=0.08)
        nota_lbl = Text("看到公证", font=FONT, font_size=14, color=FINALIZE_CLR).next_to(nota_dot, UP, buff=0.1)

        path_a = Arrow(nota_dot.get_center() + UP * 0.3, nota_dot.get_center() + UP * 1.2 + RIGHT * 1, buff=0, color=FINALIZE_CLR, stroke_width=2)
        path_a_lbl = Text("→ finalize + 下一轮", font=FONT, font_size=14, color=FINALIZE_CLR).next_to(path_a, UP, buff=0.05)

        path_b = Arrow(timeout_dot.get_center() + DOWN * 0.3, timeout_dot.get_center() + DOWN * 1.2 + RIGHT * 1, buff=0, color=DUMMY_CLR, stroke_width=2)
        path_b_lbl = Text("→ 投 dummy block", font=FONT, font_size=14, color=DUMMY_CLR).next_to(path_b, DOWN, buff=0.05)

        self.play(Create(timeline), FadeIn(start_dot, start_lbl), FadeIn(timeout_dot, timeout_lbl), run_time=0.6)
        self.play(FadeIn(nota_dot, nota_lbl), run_time=0.4)
        self.play(GrowArrow(path_a), FadeIn(path_a_lbl), run_time=0.5)
        self.play(GrowArrow(path_b), FadeIn(path_b_lbl), run_time=0.5)
        self.pad_segment()

        self.show_sub("这意味着什么？三分之二的 finalize 消息和三分之二的 dummy block 投票，不可能同时存在。")

        self.play(FadeOut(timeline, start_dot, start_lbl, timeout_dot, timeout_lbl, nota_dot, nota_lbl, path_a, path_a_lbl, path_b, path_b_lbl), run_time=0.4)

        big_circle = Circle(radius=2.2, color=WHITE, stroke_width=2)
        big_label = MathTex("n", font_size=28, color=WHITE).next_to(big_circle, UP, buff=0.1)

        fin_arc = Arc(radius=2.2, start_angle=PI * 0.6, angle=PI * 0.85, color=FINALIZE_CLR, stroke_width=8)
        fin_arc_lbl = MathTex(r"\geq \frac{2n}{3}", font_size=22, color=FINALIZE_CLR).shift(LEFT * 2.5 + DOWN * 1)
        fin_arc_name = Text("finalize", font_size=16, color=FINALIZE_CLR).next_to(fin_arc_lbl, DOWN, buff=0.05)

        dummy_arc = Arc(radius=2.2, start_angle=-PI * 0.3, angle=PI * 0.85, color=DUMMY_CLR, stroke_width=8)
        dummy_arc_lbl = MathTex(r"\geq \frac{2n}{3}", font_size=22, color=DUMMY_CLR).shift(RIGHT * 2.5 + DOWN * 1)
        dummy_arc_name = Text("dummy vote", font_size=16, color=DUMMY_CLR).next_to(dummy_arc_lbl, DOWN, buff=0.05)

        impossible = Text("不可能同时达到!", font=FONT, font_size=24, color=FAIL_CLR).shift(DOWN * 2.5)
        imp_reason = MathTex(r"\frac{2n}{3} + \frac{2n}{3} > n", font_size=24, color=FAIL_CLR).next_to(impossible, DOWN, buff=0.15)

        self.play(Create(big_circle), Write(big_label), run_time=0.4)
        self.play(Create(fin_arc), Write(fin_arc_lbl), Write(fin_arc_name), run_time=0.5)
        self.play(Create(dummy_arc), Write(dummy_arc_lbl), Write(dummy_arc_name), run_time=0.5)
        self.play(FadeIn(impossible), Write(imp_reason), run_time=0.6)
        self.pad_segment()

        self.show_sub("这就是 Simplex 安全性的核心。如果一个区块被最终确认了——有三分之二的 finalize——那就不可能有三分之二的 dummy vote。所以没有人能看到一个公证的空块来替代这个已确认的区块。")

        self.play(FadeOut(big_circle, big_label, fin_arc, fin_arc_lbl, fin_arc_name, dummy_arc, dummy_arc_lbl, dummy_arc_name, impossible, imp_reason), run_time=0.5)

        claim_b = VGroup(
            Text("定理 B:", font=FONT, font_size=20, color=ACCENT),
            Text("迭代 h 被最终确认 → 不存在公证的空块 h", font=FONT, font_size=18, color=WHITE),
        ).arrange(RIGHT, buff=0.2).shift(UP * 0.5)
        claim_b_box = SurroundingRectangle(claim_b, color=ACCENT, buff=0.15, corner_radius=0.08)
        self.play(Write(claim_b), Create(claim_b_box), run_time=0.8)
        self.pad_segment()

        self.show_sub("再加上之前的 quorum intersection——同一高度不可能有两个不同的非空公证区块——Simplex 的一致性就完美地建立了。")

        claim_a = VGroup(
            Text("定理 A:", font=FONT, font_size=20, color=LEADER_CLR),
            Text("同一高度 ≤ 1 个非空公证区块", font=FONT, font_size=18, color=WHITE),
        ).arrange(RIGHT, buff=0.2).shift(DOWN * 1)
        claim_a_box = SurroundingRectangle(claim_a, color=LEADER_CLR, buff=0.15, corner_radius=0.08)
        self.play(Write(claim_a), Create(claim_a_box), run_time=0.8)

        combined = VGroup(
            Text("A + B", font_size=24, color=OK_CLR),
            Text("→ 一致性 ✓", font=FONT, font_size=24, color=OK_CLR),
        ).arrange(RIGHT, buff=0.2).shift(DOWN * 2.5)
        combined_box = SurroundingRectangle(combined, color=OK_CLR, buff=0.15, corner_radius=0.1)
        self.play(Write(combined), Create(combined_box), run_time=0.6)

        self.clear_all()


class S09_LivenessScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("活性分析", font=FONT, font_size=36, color=WHITE)
        self.play(Write(sec), run_time=0.5)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3))

        self.show_sub("安全性解决了，那活性呢？")
        self.wait(1)
        self.pad_segment()

        self.show_sub("如果 leader 是诚实的，协议推进非常快。Leader 提案，节点投票，公证达成——整个过程只需要 2 倍的实际网络延迟 δ。")

        tl_good = Line(LEFT * 5, RIGHT * 5, color=MUTED, stroke_width=2).shift(UP * 1)
        good_lbl = Text("诚实 Leader", font=FONT, font_size=20, color=OK_CLR).shift(UP * 2 + LEFT * 3)

        steps_good = [
            (LEFT * 4, "提案", LEADER_CLR),
            (LEFT * 1, "投票", NODE_CLR),
            (RIGHT * 2, "公证", ACCENT),
        ]
        good_dots = VGroup()
        good_labels = VGroup()
        for pos_x, label, clr in steps_good:
            d = Dot(pos_x + UP * 1, color=clr, radius=0.08)
            l = Text(label, font=FONT, font_size=14, color=clr).next_to(d, UP, buff=0.1)
            good_dots.add(d)
            good_labels.add(l)

        delta_brace = BraceBetweenPoints(LEFT * 4 + UP * 0.6, RIGHT * 2 + UP * 0.6, color=OK_CLR)
        delta_lbl = MathTex(r"2\delta", font_size=28, color=OK_CLR).next_to(delta_brace, DOWN, buff=0.1)

        self.play(Create(tl_good), FadeIn(good_lbl), run_time=0.4)
        for d, l in zip(good_dots, good_labels):
            self.play(FadeIn(d, l), run_time=0.25)
        self.play(Create(delta_brace), Write(delta_lbl), run_time=0.5)
        self.pad_segment()

        self.show_sub("如果 leader 是恶意的，最坏情况下等 3Δ 超时，投 dummy block，然后进入下一轮。")

        tl_bad = Line(LEFT * 5, RIGHT * 5, color=MUTED, stroke_width=2).shift(DOWN * 1)
        bad_lbl = Text("恶意 Leader", font=FONT, font_size=20, color=FAIL_CLR).shift(DOWN * 0 + LEFT * 3)

        timeout_bar = Rectangle(width=5, height=0.25, fill_color=FAIL_CLR, fill_opacity=0.2, stroke_color=FAIL_CLR, stroke_width=1)
        timeout_bar.move_to(tl_bad).shift(UP * 0.15)
        timeout_end = Dot(RIGHT * 2 + DOWN * 1, color=DUMMY_CLR, radius=0.08)
        timeout_text = Text("3Δ 超时 → dummy", font=FONT, font_size=14, color=DUMMY_CLR).next_to(timeout_end, UP, buff=0.1)

        total_brace = BraceBetweenPoints(LEFT * 4 + DOWN * 1.4, RIGHT * 3.5 + DOWN * 1.4, color=FAIL_CLR)
        total_lbl = MathTex(r"3\Delta + \delta", font_size=28, color=FAIL_CLR).next_to(total_brace, DOWN, buff=0.1)

        self.play(Create(tl_bad), FadeIn(bad_lbl), run_time=0.4)
        self.play(FadeIn(timeout_bar, timeout_end, timeout_text), run_time=0.5)
        self.play(Create(total_brace), Write(total_lbl), run_time=0.5)
        self.pad_segment()

        self.show_sub("对比 Tendermint 的 6Δ 超时，Simplex 的恶意 leader 浪费时间减半。这就是去掉 leader 2Δ 等待带来的效率提升。")

        self.play(FadeOut(tl_good, good_lbl, good_dots, good_labels, delta_brace, delta_lbl, tl_bad, bad_lbl, timeout_bar, timeout_end, timeout_text, total_brace, total_lbl), run_time=0.5)

        bar_tend = Rectangle(width=6, height=0.6, fill_color=VERIFIER_CLR, fill_opacity=0.3, stroke_color=VERIFIER_CLR, stroke_width=2).shift(UP * 0.5)
        bar_tend_lbl = Text("Tendermint: 6Δ", font_size=22, color=VERIFIER_CLR).move_to(bar_tend)

        bar_simp = Rectangle(width=3, height=0.6, fill_color=ACCENT, fill_opacity=0.3, stroke_color=ACCENT, stroke_width=2).shift(DOWN * 0.5)
        bar_simp.align_to(bar_tend, LEFT)
        bar_simp_lbl = Text("Simplex: 3Δ", font_size=22, color=ACCENT).move_to(bar_simp)

        half = Text("减半!", font=FONT, font_size=28, color=OK_CLR).shift(RIGHT * 3 + DOWN * 0.5)

        self.play(FadeIn(bar_tend, bar_tend_lbl), run_time=0.5)
        self.play(FadeIn(bar_simp, bar_simp_lbl), run_time=0.5)
        self.play(FadeIn(half, scale=1.3), run_time=0.4)

        self.clear_all()


# ═════════════════════════════════════════════════════════════════════════════
# Part 4 · 合 — Conclude
# ═════════════════════════════════════════════════════════════════════════════

class S10_ApplicationScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        sec = Text("走向生产", font=FONT, font_size=42, color=WHITE)
        self.play(Write(sec), run_time=0.6)
        self.play(sec.animate.scale(0.55).to_edge(UP, buff=0.3))

        self.show_sub("Simplex 不只是一篇论文。它已经走进了生产系统。")
        self.wait(1)
        self.pad_segment()

        self.show_sub("Solana 的下一代共识 Alpenglow 采用了 Simplex 的思想。Commonware 库将 Simplex 作为核心共识模块。Ava Labs 也在他们的系统中实现了 Simplex。")

        apps = [
            ("Solana Alpenglow", "下一代共识引擎\n融合 Simplex 思想", LEADER_CLR),
            ("Commonware", "核心共识库\n生产级实现", OK_CLR),
            ("Ava Labs", "完整的 Simplex\nGo 实现", VERIFIER_CLR),
        ]

        cards = VGroup()
        for name, desc, clr in apps:
            card = RoundedRectangle(
                width=3.5, height=2.8, corner_radius=0.18,
                fill_color=CARD_BG, fill_opacity=0.9,
                stroke_color=clr, stroke_width=2,
            )
            n_txt = Text(name, font_size=22, color=clr)
            d_txt = Text(desc, font=FONT, font_size=15, color=WHITE, line_spacing=1.3)
            VGroup(n_txt, d_txt).arrange(DOWN, buff=0.3).move_to(card)
            cards.add(VGroup(card, n_txt, d_txt))

        cards.arrange(RIGHT, buff=0.35).shift(DOWN * 0.3)
        for card in cards:
            self.play(FadeIn(card, shift=UP * 0.4), run_time=0.5)
        self.pad_segment()

        self.show_sub("从 2023 年的学术论文到多个区块链的生产部署，Simplex 用了不到两年时间。这在共识协议的历史上极为罕见。")

        self.play(FadeOut(cards), run_time=0.4)

        tl = Line(LEFT * 4, RIGHT * 4, color=MUTED, stroke_width=2).shift(DOWN * 0.5)
        d2023 = Dot(LEFT * 3 + DOWN * 0.5, color=ACCENT, radius=0.08)
        d2023_lbl = Text("2023\n论文发表", font=FONT, font_size=16, color=ACCENT).next_to(d2023, DOWN, buff=0.15)
        d2025 = Dot(RIGHT * 3 + DOWN * 0.5, color=OK_CLR, radius=0.08)
        d2025_lbl = Text("2025\n生产部署", font=FONT, font_size=16, color=OK_CLR).next_to(d2025, DOWN, buff=0.15)
        arrow = Arrow(d2023.get_center(), d2025.get_center(), buff=0.15, color=ACCENT, stroke_width=3)
        fast_lbl = Text("< 2 年", font=FONT, font_size=22, color=ACCENT).next_to(tl, UP, buff=0.3)

        self.play(Create(tl), FadeIn(d2023, d2023_lbl), FadeIn(d2025, d2025_lbl), run_time=0.6)
        self.play(GrowArrow(arrow), FadeIn(fast_lbl), run_time=0.5)

        self.clear_all()


class S11_OutroScene(SubtitleMixin, Scene):
    def construct(self):
        self.camera.background_color = BG

        self.show_sub("让我们回到最开始的问题。")

        servers = VGroup(*[
            make_server(RIGHT * (i * 1.2 - 3) + UP * (0.5 if i % 2 == 0 else -0.5),
                        color=EVIL_CLR if i in [1, 4] else NODE_CLR)
            for i in range(6)
        ])
        self.play(FadeIn(servers, lag_ratio=0.1), run_time=0.8)
        self.pad_segment()

        self.show_sub("在一个充满不信任的网络中，如何让诚实的节点达成一致？")

        q = Text(
            "如何在不信任的网络中\n让诚实的节点达成一致？",
            font=FONT, font_size=32, color=WHITE, line_spacing=1.5,
        )
        self.play(FadeOut(servers), run_time=0.4)
        self.play(Write(q), run_time=1.5)
        self.pad_segment()

        self.show_sub("Simplex 的回答出人意料的简单：每轮一个 leader、一次投票、一个超时。通过 finalize 和 dummy vote 的互斥性，用最少的规则，构建最坚固的安全保证。")

        self.play(FadeOut(q), run_time=0.5)

        elements = VGroup(
            Text("1 Leader / 轮", font=FONT, font_size=22, color=LEADER_CLR),
            Text("1 次投票", font=FONT, font_size=22, color=NODE_CLR),
            Text("3Δ 超时", font=FONT, font_size=22, color=DUMMY_CLR),
            Text("Finalize ⊕ Dummy = 互斥", font=FONT, font_size=22, color=ACCENT),
        ).arrange(DOWN, buff=0.3)
        for e in elements:
            self.play(FadeIn(e, shift=RIGHT * 0.3), run_time=0.3)
        self.wait(1)
        self.pad_segment()

        self.show_sub("Leonardo da Vinci 说过：「简单是终极的复杂。」Simplex 正是这句话在分布式系统中最好的注脚。")

        self.play(FadeOut(elements), run_time=0.5)

        quote_en = Text(
            '"Simplicity is the ultimate sophistication."',
            font_size=28, color=ACCENT,
        )
        quote_cn = Text(
            "— 简单是终极的复杂",
            font=FONT, font_size=24, color=MUTED,
        )
        quote = VGroup(quote_en, quote_cn).arrange(DOWN, buff=0.3)
        self.play(Write(quote_en), run_time=1.5)
        self.play(FadeIn(quote_cn, shift=UP * 0.2), run_time=0.6)
        self.wait(2)
        self.pad_segment()

        self.hide_sub()
        self.show_sub("这就是 Simplex 共识算法的美。")
        final = Text(
            "这就是 Simplex 共识算法的美。",
            font=FONT, font_size=28, color=MUTED,
        )
        self.play(FadeOut(quote), run_time=0.5)
        self.play(FadeIn(final, shift=UP * 0.2), run_time=0.8)
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=2)
        self._save_stamps()
