"""算法：FFT 的递归分治。

视频重点。剧本要求「在公式推导的基础上，直观展示 FFT 的递归分治细节」，并明确
举例：用动画展示系数按位置分成奇、偶两个子多项式。

3.1 拆：系数按奇偶下标分组，得到两个规模减半的子问题。
3.2 合：两个半长 DFT 用一次乘法喂出两个输出（butterfly）。
3.3 树：递归展开的层数与每层代价，解释 n log n 从哪来。
"""

from manimlib import *
import numpy as np

from utils.theme import *
from utils.mobjects import *

N = 8
EVEN_IDX = list(range(0, N, 2))
ODD_IDX = list(range(1, N, 2))


def coeff_card(index, color, size=0.82):
    """一个系数卡片：圆角框 + x_i。"""
    rect = RoundedRectangle(
        width=size, height=size, corner_radius=0.12,
        stroke_color=color, stroke_width=2,
        fill_color=color, fill_opacity=0.12,
    )
    label = Tex(Rf"x_{{{index}}}", font_size=SMALL_LABEL, color=WHITE).move_to(rect)
    return VGroup(rect, label)


# ================================================================ 3.1

class SplitEvenOdd(InteractiveScene):
    """3.1 按位置分组：偶数下标一组，奇数下标一组。"""

    def construct(self):
        cards = VGroup(*[coeff_card(i, WHITE) for i in range(N)])
        cards.arrange(RIGHT, buff=0.28)
        # 卡片保持居中就够：4 个卡片总宽 4.12，左侧放下 E(x)/O(x) 标签绰绰有余
        cards.move_to(UP * 1.7)

        self.play(LaggedStart(*[FadeIn(c, UP) for c in cards], lag_ratio=0.1, run_time=1.4))

        note = NarrationBoard(self)
        note.say("把 8 个系数按位置排开，现在要把它一分为二", hold=3.0)

        self.play(
            *[cards[i][0].animate.set_stroke(color=EVEN_COLOR, width=3) for i in EVEN_IDX],
            *[cards[i][0].animate.set_stroke(color=ODD_COLOR, width=3) for i in ODD_IDX],
            run_time=1.2,
        )
        note.say("偶数位置的系数留一组，奇数位置的系数另分一组", hold=3.0)

        # 目标位置：先用副本排好，再把真卡片平移过去
        tmpl_even = VGroup(*[cards[i].copy() for i in EVEN_IDX])
        tmpl_even.arrange(RIGHT, buff=0.28).move_to(UP * 0.45)
        tmpl_odd = VGroup(*[cards[i].copy() for i in ODD_IDX])
        tmpl_odd.arrange(RIGHT, buff=0.28).move_to(DOWN * 0.85)

        self.play(
            *[cards[i].animate.move_to(tmpl_even[j].get_center()) for j, i in enumerate(EVEN_IDX)],
            *[cards[i].animate.move_to(tmpl_odd[j].get_center()) for j, i in enumerate(ODD_IDX)],
            run_time=2.0,
        )
        self.wait(0.8)

        even_group = VGroup(*[cards[i] for i in EVEN_IDX])
        odd_group = VGroup(*[cards[i] for i in ODD_IDX])

        e_tag = VGroup(
            Tex(R"E(x)", font_size=LABEL, color=EVEN_COLOR),
            Text("偶数下标", font=CH_FONT, font_size=SMALL_LABEL, color=EVEN_COLOR),
        ).arrange(DOWN, buff=0.14).next_to(even_group, LEFT, buff=0.55)
        o_tag = VGroup(
            Tex(R"O(x)", font_size=LABEL, color=ODD_COLOR),
            Text("奇数下标", font=CH_FONT, font_size=SMALL_LABEL, color=ODD_COLOR),
        ).arrange(DOWN, buff=0.14).next_to(odd_group, LEFT, buff=0.55)

        self.play(FadeIn(e_tag, RIGHT), FadeIn(o_tag, RIGHT), run_time=1.0)
        note.say("这两组各自又是一个规模减半的多项式", hold=3.0)

        note.clear()
        e_formula = Tex(
            R"E(x) = x_0 + x_2x + x_4x^2 + x_6x^3",
            font_size=BODY, color=EVEN_COLOR,
        )
        o_formula = Tex(
            R"O(x) = x_1 + x_3x + x_5x^2 + x_7x^3",
            font_size=BODY, color=ODD_COLOR,
        )
        formulas = VGroup(e_formula, o_formula).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        formulas.to_edge(DOWN, buff=0.65)

        self.play(
            LaggedStart(*[FadeIn(f, UP) for f in formulas], lag_ratio=0.35),
            run_time=1.4,
        )
        self.wait(2.8)

        note.say("这一步只花了搬运的功夫，真正的计算在两个子问题上递归", hold=3.2)
        note.clear()


# ================================================================ 3.2

class ButterflyCombine(InteractiveScene):
    """3.2 两个半长 DFT 合成全长 DFT：一次乘法喂两个输出。"""

    def construct(self):
        note = NarrationBoard(self)

        e_dot = Dot(LEFT * 3.4 + UP * 1.5, radius=0.10, fill_color=EVEN_COLOR, stroke_width=0)
        o_dot = Dot(LEFT * 3.4 + DOWN * 1.5, radius=0.10, fill_color=ODD_COLOR, stroke_width=0)
        x1_dot = Dot(RIGHT * 3.4 + UP * 1.5, radius=0.10, fill_color=ACCENT, stroke_width=0)
        x2_dot = Dot(RIGHT * 3.4 + DOWN * 1.5, radius=0.10, fill_color=ACCENT, stroke_width=0)

        e_lab = Tex(R"E_k", font_size=LABEL, color=EVEN_COLOR).next_to(e_dot, LEFT, buff=0.25)
        o_lab = Tex(R"O_k", font_size=LABEL, color=ODD_COLOR).next_to(o_dot, LEFT, buff=0.25)
        x1_lab = Tex(R"X_k", font_size=LABEL, color=ACCENT).next_to(x1_dot, RIGHT, buff=0.25)
        x2_lab = Tex(R"X_{k+n/2}", font_size=LABEL, color=ACCENT).next_to(x2_dot, RIGHT, buff=0.25)

        nodes = VGroup(e_dot, o_dot, x1_dot, x2_dot, e_lab, o_lab, x1_lab, x2_lab)
        self.play(LaggedStart(*[FadeIn(m, scale=0.6) for m in nodes], lag_ratio=0.06, run_time=1.2))
        self.wait(0.5)

        note.say("两个半长结果都算好之后，用一次乘法就能拼出两个输出", hold=3.2)

        # 四条连线，按来源分色：蓝=E 的贡献，绿=O 的贡献。
        # 权重只挂在从 O 出发的两条上 —— E 的两条系数都是 1。
        def link(a, b, color, width=2.5):
            return Arrow(a.get_center(), b.get_center(), buff=0.16, color=color,
                         stroke_width=width, tip_width_ratio=3)

        top = link(e_dot, x1_dot, EVEN_COLOR)          # E → X_k
        diag_down = link(e_dot, x2_dot, EVEN_COLOR)    # E → X_{k+n/2}
        diag_up = link(o_dot, x1_dot, ODD_COLOR)       # O → X_k，带 +ω^k
        bottom = link(o_dot, x2_dot, ODD_COLOR)        # O → X_{k+n/2}，带 −ω^k

        self.play(
            LaggedStart(ShowCreation(top), ShowCreation(diag_down), lag_ratio=0.3, run_time=1.2),
            LaggedStart(ShowCreation(diag_up), ShowCreation(bottom), lag_ratio=0.3, run_time=1.2),
        )

        # 标在各自线段的不同位置上，别都挤到交叉点
        w_up = Tex(R"\times\ \omega^{k}", font_size=SMALL_LABEL, color=SUM_COLOR)
        w_up.next_to(diag_up.point_from_proportion(0.28), UP, buff=0.12)
        w_dn = Tex(R"\times\ (-\omega^{k})", font_size=SMALL_LABEL, color=SUM_COLOR)
        w_dn.next_to(bottom.point_from_proportion(0.5), DOWN, buff=0.16)
        self.play(Write(w_up), Write(w_dn))
        self.wait(1.0)

        note.say("上面一路加，下面一路减，这就是折半引理在起作用", hold=3.2)
        note.clear()

        results = VGroup(
            Tex(R"X_k = E_k + \omega^{k} O_k", font_size=LABEL, color=ACCENT),
            Tex(R"X_{k+n/2} = E_k - \omega^{k} O_k", font_size=LABEL, color=ACCENT),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        results.to_edge(DOWN, buff=0.55)

        self.play(LaggedStart(*[FadeIn(r, UP) for r in results], lag_ratio=0.35), run_time=1.4)
        self.wait(3.0)


# ================================================================ 3.3

class RecursionTree(InteractiveScene):
    """3.3 递归树：每层方块总宽相同 = 每层代价都是 n，层数是 log n。"""

    LEVELS = [(1, 8), (2, 4), (4, 2), (8, 1)]
    YS = [2.55, 1.3, 0.05, -1.2]
    TOTAL_W = 7.4
    GAP = 0.08

    def construct(self):
        note = NarrationBoard(self)

        rows = VGroup()
        for (count, size), y in zip(self.LEVELS, self.YS):
            # 每行总宽锁死为 TOTAL_W：块数翻倍、块宽减半，宽度不减
            body_w = (self.TOTAL_W - (count - 1) * self.GAP) / count
            blocks = VGroup(*[
                Rectangle(
                    width=body_w, height=0.52,
                    stroke_color=ROOT_COLOR, stroke_width=1.6,
                    fill_color=ROOT_COLOR, fill_opacity=0.15,
                ) for _ in range(count)
            ]).arrange(RIGHT, buff=self.GAP)
            blocks.move_to(UP * y)
            rows.add(blocks)

        note.say("每分一次，问题数目翻倍，单个规模减半", hold=3.0)
        self.play(FadeIn(rows[0], UP), run_time=0.8)
        self.wait(0.4)
        for i in range(1, len(rows)):
            self.play(FadeIn(rows[i], UP), run_time=0.7)
            self.wait(0.25)
        self.wait(0.8)

        costs = VGroup()
        for (count, size), y in zip(self.LEVELS, self.YS):
            costs.add(
                Tex(Rf"{count} \times {size} = {count * size}",
                    font_size=SMALL_LABEL, color=MUTED)
                .move_to(RIGHT * 5.15 + UP * y)
            )
        self.play(LaggedStart(*[FadeIn(c, RIGHT) for c in costs], lag_ratio=0.2, run_time=1.4))
        self.wait(1.0)

        note.say("每一层加起来都是 8：规模变小了，代价并没有增加", hold=3.2)
        note.clear()

        line1 = VGroup(
            Text("层数", font=CH_FONT, font_size=BODY, color=MUTED),
            Tex(R"\log_2 n", font_size=BODY, color=ACCENT),
            Text("，每层", font=CH_FONT, font_size=BODY, color=MUTED),
            Tex(R"\Theta(n)", font_size=BODY, color=ACCENT),
        ).arrange(RIGHT, buff=0.16)
        line1.move_to(DOWN * 2.35)

        line2 = VGroup(
            Text("总代价", font=CH_FONT, font_size=LABEL, color=MUTED),
            Tex(R"\Theta(n\log n)", font_size=KEY_FORMULA, color=FAST_COLOR),
        ).arrange(RIGHT, buff=0.32)
        line2.move_to(DOWN * 3.15)

        self.play(FadeIn(line1, UP), run_time=1.0)
        self.play(FadeIn(line2, UP), run_time=1.0)
        self.wait(3.0)
