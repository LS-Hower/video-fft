"""其他内容：技术补遗与人文脉络。

剧本明确这部分「较为简略」：
- 技术部分：三个推导「贴在屏幕上三秒钟，想看的观众自己暂停看」，另外三个话题
  用极简练的几句话一带而过。
- 人文部分：FFT 从高斯到现代的重新发明之路、FFTW、近年新进展。

所以这里刻意不做深挖，靠停留时间和信息密度控制节奏。
"""

from manimlib import *
import numpy as np

from utils.theme import *
from utils.mobjects import *


# ================================================================ 4.1

def term_row(cn, tex, color, font_size=BODY):
    """一行「中文名 + 公式」。"""
    return VGroup(
        Text(cn, font=CH_FONT, font_size=font_size, color=color),
        Tex(tex, font_size=font_size, color=WHITE),
    ).arrange(RIGHT, buff=0.45)


class TechRecap(InteractiveScene):
    """4.1 技术补遗：推导快速贴屏，话题一句话带过。"""

    def construct(self):
        note = NarrationBoard(self)
        note.say("几段推导直接贴在屏幕上，想细看的可以暂停", hold=2.6)
        note.clear()

        # ---------------- 三个推导，快速贴屏
        derivations = VGroup(
            term_row("逆 DFT", R"x_m = \frac{1}{n}\sum_{k=0}^{n-1} X_k\,\omega_n^{-km}", ACCENT),
            term_row("递归式", R"T(n) = 2T\left(\tfrac{n}{2}\right) + \Theta(n)\ \Rightarrow\ \Theta(n\log n)", FAST_COLOR),
            term_row("蝶形网络", R"\log n\ \text{levels},\ \ n/2\ \text{butterflies each}", ROOT_COLOR),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        derivations.move_to(UP * 0.3)

        for row in derivations:
            self.play(FadeIn(row, RIGHT), run_time=0.6)
            self.wait(2.4)
        self.wait(0.6)
        self.play(FadeOut(derivations, DOWN), run_time=0.8)

        # ---------------- 三个话题，各一句话
        topics = VGroup(
            term_row("DFT 与 FT", R"\text{DFT is FT sampled at equally spaced points}", MUTED, SMALL_LABEL),
            term_row("NTT", R"\text{swap roots of unity for modular primitive roots}", ACCENT, SMALL_LABEL),
            term_row("大整数乘法", R"\Theta(n\log n\log\log n)\ \to\ \Theta(n\log n)", SUM_COLOR, SMALL_LABEL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        topics.move_to(UP * 0.2)

        note.say("还有三件事，各用一句话带过", hold=2.2)
        self.play(LaggedStart(*[FadeIn(t, RIGHT) for t in topics], lag_ratio=0.3, run_time=2.0))
        self.wait(2.0)

        note.say("NTT 全程整数运算，没有浮点误差；大整数乘法的位复杂度已被压到线性对数", hold=4.0)
        self.wait(1.0)


# ================================================================ 4.2

EVENTS = [
    ("1805", "高斯", "已有雏形，没有发表"),
    ("1965", "Cooley–Tukey", "重新发明，改变工程"),
    ("1997", "FFTW", "自动挑选最快算法"),
    ("今天", "仍在演进", "学习方法开始参与"),
]


class HumanStory(InteractiveScene):
    """4.2 人文脉络：一条时间线，四个节点。"""

    def construct(self):
        note = NarrationBoard(self)

        line = Line(LEFT * 5.6, RIGHT * 5.6, stroke_color=MUTED, stroke_width=2)
        line.move_to(UP * 0.2)
        self.play(ShowCreation(line), run_time=1.0)

        xs = [-4.4, -1.5, 1.4, 4.4]
        colors = [MUTED, ACCENT, FAST_COLOR, ROOT_COLOR]

        note.say("同一个想法被反复发现，每次都写在不同的时代里", hold=2.8)

        for (year, who, what), x, color in zip(EVENTS, xs, colors):
            dot = Dot(RIGHT * x + UP * 0.2, radius=0.08, fill_color=color, stroke_width=0)

            # 人物肖像用占位符，素材到位后整块换成 ImageMobject
            portrait = get_placeholder(
                f"portrait_{who}", width=1.15, height=1.45, color=color,
                label=who, font_size=TINY,
            ).move_to(RIGHT * x + UP * 1.6)

            year_tex = Text(year, font=CH_FONT, font_size=LABEL, color=color).next_to(dot, DOWN, buff=0.3)
            what_text = Text(what, font=CH_FONT, font_size=SMALL_LABEL, color=GREY_B)
            what_text.next_to(year_tex, DOWN, buff=0.3)
            if what_text.get_width() > 2.7:
                what_text.scale(2.7 / what_text.get_width())

            self.play(FadeIn(portrait, UP), FadeIn(dot, scale=0.5), run_time=0.8)
            self.play(Write(year_tex), FadeIn(what_text, UP), run_time=0.8)
            self.wait(1.4)

        note.say("数学上的漂亮结构，往往要等几十年才等到能跑它的机器", hold=3.5)
        note.clear()

        closing = VGroup(
            Text("从纸上的引理", font=CH_FONT, font_size=BODY, color=MUTED),
            Text("到每秒十亿次运算", font=CH_FONT, font_size=BODY, color=MUTED),
        ).arrange(RIGHT, buff=0.35)
        closing.to_edge(DOWN, buff=0.7)
        self.play(FadeIn(closing, UP), run_time=1.0)
        self.wait(2.6)
