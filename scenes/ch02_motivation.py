"""FFT 的动机：多项式的两种表示、相乘的代价、DFT 与 FFT。

剧本三节对应三个场景类，类在文件中的顺序 = 成片顺序。讲解全部由屏幕文字承载
（不配音），统一走 `NarrationBoard`。
"""

from manimlib import *
import numpy as np

from utils.theme import *
from utils.mobjects import *


# ================================================================ 2.1

class PolynomialRepresentations(InteractiveScene):
    """2.1 同一份信息，两种装法：系数向量 与 点值。"""

    COEFFS = [3, 2, 5, 1]     # 升幂：3 + 2x + 5x^2 + x^3
    XS = [0, 1, 2, 3]

    def construct(self):
        coeffs = np.array(self.COEFFS, dtype=float)

        # ---------------- 系数表示
        poly = Tex(R"f(x) = 3 + 2x + 5x^2 + x^3", font_size=KEY_FORMULA, color=WHITE)
        poly.to_edge(UP, buff=0.9)
        self.play(Write(poly))

        note = NarrationBoard(self)
        note.say("一个多项式，第一反应是把每一项的系数依次写下来", hold=3.2)

        vec = Tex(R"\begin{bmatrix} 3 \\ 2 \\ 5 \\ 1 \end{bmatrix}",
                  font_size=KEY_FORMULA, color=ACCENT)
        vec.next_to(poly, DOWN, buff=0.75)
        down_arrow = Arrow(
            poly.get_bottom() + DOWN * 0.05,
            vec.get_top() + UP * 0.05,
            buff=0,
            color=MUTED,
            stroke_width=2,
        )
        self.play(GrowArrow(down_arrow), FadeIn(vec, UP))
        self.wait(1.2)

        note.say("四个系数，就是这条多项式的全部信息", hold=2.8)

        # ---------------- 点值表示
        # 公式与系数收到左上角，把画面让给坐标系
        head = VGroup(poly, down_arrow, vec)
        self.play(head.animate.scale(0.52).to_corner(UL, buff=0.62), run_time=1.2)

        axes = get_axes(x_range=(0, 3.6, 1), y_range=(0, 90, 30), width=7.0, height=3.4)
        axes.move_to(RIGHT * 2.3 + DOWN * 0.75)
        axis_labels = axes.get_axis_labels("x", "f(x)")

        graph = axes.get_graph(
            lambda x: np.polyval(coeffs[::-1], x),
            x_range=(0, 3.3),
            color=ACCENT,
            stroke_width=3,
        )
        self.play(FadeIn(axes), FadeIn(axis_labels), ShowCreation(graph), run_time=2.0)

        note.say("但同一条曲线，也可以只由它上面的几个点确定", hold=2.8)

        pts = VGroup()
        tags = VGroup()
        for x in self.XS:
            # 这组取值都是整数，先取整再显示，别让画面出现 (0, 3.0) 这种尾巴
            y = int(round(float(np.polyval(coeffs[::-1], x))))
            d = Dot(axes.c2p(x, y), radius=0.09, fill_color=SUM_COLOR, stroke_width=0)
            pts.add(d)
            tags.add(
                Tex(Rf"({x}, {y})", font_size=SMALL_LABEL, color=SUM_COLOR)
                .next_to(d, UR, buff=0.10)
            )
        self.play(LaggedStart(*[FadeIn(d, scale=0.6) for d in pts], lag_ratio=0.18, run_time=1.6))
        self.play(LaggedStart(*[Write(t) for t in tags], lag_ratio=0.18, run_time=1.4))
        self.wait(1.5)

        note.say("四个系数、四个点，装的是同一条曲线", hold=3.0)

        # ---------------- 收束：两种表示并列
        self.play(
            FadeOut(axes),
            FadeOut(axis_labels),
            FadeOut(graph),
            FadeOut(pts),
            FadeOut(tags),
            FadeOut(head),
            run_time=1.0,
        )

        note.clear()
        lhs = VGroup(
            Text("系数表示", font=CH_FONT, font_size=LABEL, color=EVEN_COLOR),
            Tex(R"(a_0,\ a_1,\ \dots,\ a_{n-1})", font_size=LABEL, color=EVEN_COLOR),
        ).arrange(DOWN, buff=0.28)
        rhs = VGroup(
            Text("点值表示", font=CH_FONT, font_size=LABEL, color=ODD_COLOR),
            Tex(R"(x_0, y_0),\ \dots,\ (x_{n-1}, y_{n-1})", font_size=LABEL, color=ODD_COLOR),
        ).arrange(DOWN, buff=0.28)
        pair = VGroup(lhs, rhs).arrange(RIGHT, buff=1.9).move_to(ORIGIN)
        equiv = Text("同一份信息，两种装法", font=CH_FONT, font_size=LABEL, color=MUTED)
        equiv.next_to(pair, UP, buff=0.7)

        self.play(FadeIn(equiv, UP), run_time=0.8)
        self.play(
            LaggedStart(FadeIn(lhs, RIGHT), FadeIn(rhs, LEFT), lag_ratio=0.35),
            run_time=1.4,
        )
        self.wait(3.0)


# ================================================================ 2.2

def coeff_vector(values, color, font_size=LABEL):
    """一行/一列系数向量。"""
    body = R" & ".join(str(int(v)) for v in values)
    # 注意 f-string 里 LaTeX 的花括号要写两遍，否则 {bmatrix} 会被当成占位符
    return Tex(Rf"\begin{{bmatrix}} {body} \end{{bmatrix}}", font_size=font_size, color=color)


def count_label(number, color, font_size=LABEL):
    """「12 次乘法」这类计数标签。"""
    return VGroup(
        Tex(str(number), font_size=font_size, color=color),
        Text("次乘法", font=CH_FONT, font_size=BODY, color=color),
    ).arrange(RIGHT, buff=0.14)


class PolynomialMultiplication(InteractiveScene):
    """2.2 两种表示下相乘的代价完全不同：逐对系数相乘 vs 逐点相乘。"""

    F = [3, 2, 5, 1]      # 升幂
    G = [1, 4, 2]

    def construct(self):
        f = np.array(self.F)
        g = np.array(self.G)
        prod = np.convolve(f, g)          # [3, 14, 19, 25, 14, 2]

        # 分隔线只画到中段：底部留给两侧的复杂度结论，别让线穿过去
        divider = Line(
            UP * 3.1, DOWN * 1.5,
            stroke_color=MUTED, stroke_width=1, stroke_opacity=0.35,
        ).shift(DOWN * 0.3)
        self.play(ShowCreation(divider), run_time=0.8)

        note = NarrationBoard(self)

        # ---------------- 左：系数表示，n×m 对系数
        left_title = Text("系数表示", font=CH_FONT, font_size=LABEL, color=EVEN_COLOR)
        left_title.move_to(LEFT * 3.4 + UP * 2.6)

        f_vec = coeff_vector(f, EVEN_COLOR)
        g_vec = coeff_vector(g, ODD_COLOR)
        VGroup(f_vec, g_vec).arrange(RIGHT, buff=1.5).next_to(left_title, DOWN, buff=0.65)
        times = Tex(R"\times", font_size=LABEL, color=MUTED)
        times.move_to((f_vec.get_right() + g_vec.get_left()) / 2)

        note.say("两个多项式相乘，系数表示下每一对系数都要乘一次", hold=3.0)
        self.play(
            Write(left_title),
            FadeIn(f_vec, RIGHT),
            FadeIn(g_vec, LEFT),
            FadeIn(times),
            run_time=1.2,
        )
        self.wait(0.8)

        # 4×3 的乘法格：用点阵把「多」画出来
        grid = VGroup(*[
            Dot(radius=0.07, fill_color=EVEN_COLOR, stroke_width=0)
            for _ in range(len(f) * len(g))
        ]).arrange_in_grid(n_rows=len(f), n_cols=len(g), buff=0.26)
        grid.next_to(VGroup(f_vec, g_vec), DOWN, buff=0.8)

        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in grid], lag_ratio=0.05, run_time=1.8))
        count_l = count_label(len(f) * len(g), EVEN_COLOR)
        count_l.next_to(grid, RIGHT, buff=0.7)
        self.play(Write(count_l))
        self.wait(0.8)

        # ---------------- 右：点值表示，逐点相乘
        right_title = Text("点值表示", font=CH_FONT, font_size=LABEL, color=ODD_COLOR)
        right_title.move_to(RIGHT * 3.4 + UP * 2.6)

        note.say("点值表示下，只需要把同一个点上的两个高度相乘", hold=3.0)

        rows = VGroup(*[
            VGroup(
                Tex(Rf"x_{{{i}}}", font_size=BODY, color=MUTED),
                Tex(R":", font_size=BODY, color=MUTED),
                Tex(R"f", font_size=BODY, color=EVEN_COLOR),
                Tex(R"\times", font_size=BODY, color=MUTED),
                Tex(R"g", font_size=BODY, color=ODD_COLOR),
            ).arrange(RIGHT, buff=0.18)
            for i in range(len(prod))
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        rows.next_to(right_title, DOWN, buff=0.6)

        self.play(Write(right_title), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(r, RIGHT) for r in rows], lag_ratio=0.12, run_time=1.6))
        count_r = count_label(len(prod), ODD_COLOR)
        count_r.next_to(rows, RIGHT, buff=0.7)
        self.play(Write(count_r))
        self.wait(1.0)

        # ---------------- 收束：渐近复杂度
        note.say("一个是平方级，一个是线性级，差距会随规模越来越大", hold=3.0)
        note.clear()

        big_l = VGroup(
            Text("系数表示", font=CH_FONT, font_size=SMALL_LABEL, color=EVEN_COLOR),
            Tex(R"\Theta(n^2)", font_size=KEY_FORMULA, color=COST_COLOR),
        ).arrange(RIGHT, buff=0.28)
        big_r = VGroup(
            Text("点值表示", font=CH_FONT, font_size=SMALL_LABEL, color=ODD_COLOR),
            Tex(R"\Theta(n)", font_size=KEY_FORMULA, color=FAST_COLOR),
        ).arrange(RIGHT, buff=0.28)
        compare = VGroup(big_l, big_r).arrange(RIGHT, buff=1.6).to_edge(DOWN, buff=0.55)

        self.play(
            LaggedStart(*[FadeIn(m, UP) for m in compare], lag_ratio=0.35),
            run_time=1.4,
        )
        self.wait(3.0)


# ================================================================ 2.3

def flow_box(text, color, width=2.0, height=0.92):
    """流程图的一个环节。"""
    rect = RoundedRectangle(
        width=width, height=height, corner_radius=0.14,
        stroke_color=color, stroke_width=2,
        fill_color=color, fill_opacity=0.12,
    )
    label = Text(text, font=CH_FONT, font_size=SMALL_LABEL, color=color)
    if label.get_width() > width - 0.28:
        label.scale((width - 0.28) / label.get_width())
    label.move_to(rect)
    return VGroup(rect, label)


def flow_arrow(length=1.35, color=MUTED):
    return Arrow(ORIGIN, RIGHT * length, buff=0, color=color,
                 stroke_width=2, tip_width_ratio=3)


class DFTAndFFT(InteractiveScene):
    """2.3 先把 DFT 和 FFT 分清楚，再给出三步流程。"""

    def construct(self):
        note = NarrationBoard(self)

        # ---------------- 从点值到 DFT：横坐标已知，可以省掉
        pairs = Tex(
            R"(z_0,\ f(z_0)),\ \ (z_1,\ f(z_1)),\ \ \dots,\ \ (z_{n-1},\ f(z_{n-1}))",
            font_size=LABEL, color=WHITE,
        )
        pairs.to_edge(UP, buff=1.3)
        self.play(Write(pairs))

        note.say("点值表示里，每个点要同时记住横坐标和纵坐标", hold=3.0)

        known = Tex(R"z_k = \omega_n^{k}", font_size=LABEL, color=ROOT_COLOR)
        known.next_to(pairs, DOWN, buff=0.7)
        self.play(Write(known))

        note.say("但如果横坐标固定取单位根，它完全已知，不必再存", hold=3.0)

        values = Tex(
            R"f(z_0),\ \ f(z_1),\ \ \dots,\ \ f(z_{n-1})",
            font_size=LABEL, color=ACCENT,
        )
        values.next_to(known, DOWN, buff=0.7)
        to_values = Arrow(
            known.get_bottom() + DOWN * 0.05,
            values.get_top() + UP * 0.05,
            buff=0, color=MUTED, stroke_width=2,
        )
        self.play(GrowArrow(to_values), FadeIn(values, UP))
        self.wait(1.0)

        note.say("只留下这一列数，就是离散傅里叶变换（DFT）", hold=3.5)

        # ---------------- DFT 的定义
        note.clear()
        dft = Tex(R"X_k = \sum_{m=0}^{n-1} x_m\,\omega_n^{km}",
                  font_size=KEY_FORMULA, color=ACCENT)
        dft.next_to(values, DOWN, buff=0.8)
        self.play(Write(dft))
        self.play(
            FadeOut(pairs), FadeOut(known), FadeOut(values), FadeOut(to_values),
            dft.animate.move_to(UP * 1.8),
            run_time=1.2,
        )
        self.wait(1.5)

        # ---------------- DFT 与 FFT 的分工
        dft_tag = Text("DFT：这个变换本身", font=CH_FONT, font_size=LABEL, color=ACCENT)
        dft_tag.next_to(dft, DOWN, buff=0.7)
        fft_tag = Text("FFT：快速算出它的一种算法", font=CH_FONT, font_size=LABEL, color=FAST_COLOR)
        fft_tag.next_to(dft_tag, DOWN, buff=0.45)

        self.play(FadeIn(dft_tag, UP))
        note.say("DFT 说的是「算什么」", hold=2.2)
        self.play(FadeIn(fft_tag, UP))
        note.say("FFT 说的是「怎么快速算」——两者不是同一个东西", hold=3.5)

        # ---------------- 三步流程
        note.clear()
        self.play(FadeOut(dft), FadeOut(dft_tag), FadeOut(fft_tag), run_time=0.8)

        stages = [
            ("f, g 系数", EVEN_COLOR),
            ("f, g 点值", EVEN_COLOR),
            ("乘积点值", SUM_COLOR),
            ("乘积系数", EVEN_COLOR),
        ]
        boxes = VGroup(*[flow_box(t, c) for t, c in stages])
        arrows = VGroup(*[flow_arrow() for _ in range(3)])

        row = VGroup()
        for i, box in enumerate(boxes):
            row.add(box)
            if i < len(arrows):
                row.add(arrows[i])
        row.arrange(RIGHT, buff=0)
        row.move_to(UP * 0.35)

        step_labels = VGroup(
            Tex(R"\mathrm{DFT}", font_size=SMALL_LABEL, color=ACCENT),
            Text("逐点乘", font=CH_FONT, font_size=SMALL_LABEL, color=SUM_COLOR),
            Tex(R"\mathrm{IDFT}", font_size=SMALL_LABEL, color=ACCENT),
        )
        for lab, arr in zip(step_labels, arrows):
            lab.next_to(arr, UP, buff=0.14)

        costs = VGroup(
            Tex(R"\Theta(n\log n)", font_size=SMALL_LABEL, color=FAST_COLOR),
            Tex(R"\Theta(n)", font_size=SMALL_LABEL, color=SUM_COLOR),
            Tex(R"\Theta(n\log n)", font_size=SMALL_LABEL, color=FAST_COLOR),
        )
        for cost, arr in zip(costs, arrows):
            cost.next_to(arr, DOWN, buff=0.14)

        note.say("把多项式相乘拆成三步：算 DFT、逐点乘、再算逆 DFT", hold=3.2)
        self.play(
            LaggedStart(*[FadeIn(b, UP) for b in boxes], lag_ratio=0.18, run_time=1.6),
            LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.18, run_time=1.6),
        )
        self.play(LaggedStart(*[FadeIn(m, UP) for m in step_labels], lag_ratio=0.2, run_time=1.0))
        self.wait(1.0)
        self.play(LaggedStart(*[FadeIn(m, DOWN) for m in costs], lag_ratio=0.2, run_time=1.0))
        self.wait(1.2)

        # ---------------- 总账
        note.say("三步都是 n log n 量级，合起来仍然是 n log n，比平方级快", hold=3.5)
        note.clear()

        total = VGroup(
            Text("三步相加", font=CH_FONT, font_size=LABEL, color=MUTED),
            Tex(R"\Theta(n\log n)", font_size=KEY_FORMULA, color=FAST_COLOR),
        ).arrange(RIGHT, buff=0.4)
        total.to_edge(DOWN, buff=1.55)

        versus = VGroup(
            Text("直接卷积", font=CH_FONT, font_size=SMALL_LABEL, color=COST_COLOR),
            Tex(R"\Theta(n^2)", font_size=LABEL, color=COST_COLOR),
        ).arrange(RIGHT, buff=0.25).next_to(total, DOWN, buff=0.3)

        self.play(FadeIn(total, UP), run_time=1.0)
        self.play(FadeIn(versus, UP), run_time=0.8)
        self.wait(3.0)
