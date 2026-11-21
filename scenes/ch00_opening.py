"""引入：傅里叶变换的应用墙。

剧本只要求「快速列举较多例子、几乎不加讲解地掠过」，用来强调应用之广、间接展示
FFT 影响之大。所以这里不展开任何一项技术：节奏靠卡片出现的密度和亮度扫描，讲解
文字只点两句，观众想细看可以自己暂停。

卡片是 `get_placeholder()` 生成的占位符，素材到位后逐张替换成真实配图。
"""

from manimlib import *
import numpy as np

from utils.theme import *
from utils.mobjects import *


# (中文领域, 英文/缩写)
# 只写领域名，不写「某某用 FFT 实现」：JPEG 一类走的是 DCT 家族，说成 FFT 不准确；
# 而这些领域里傅里叶分析确实是核心工具，措辞留在这里最稳妥。
APP_WALL = [
    ("音频处理", "audio"),
    ("图像处理", "imaging"),
    ("无线通信", "OFDM"),
    ("核磁共振", "MRI"),
    ("雷达声呐", "radar"),
    ("语音识别", "speech"),
    ("频谱分析", "spectrum"),
    ("音乐制作", "music"),
    ("地震勘探", "seismic"),
    ("射电天文", "astronomy"),
    ("大整数乘法", "bigint"),
    ("卫星导航", "GNSS"),
]

WALL_COLORS = [EVEN_COLOR, ODD_COLOR, ROOT_COLOR, ACCENT, SUM_COLOR, W_COLOR]

CARD_W = 2.62
CARD_H = 1.34


def get_app_card(cn: str, en: str, color):
    """一张应用卡片：虚线框 + 中文领域名 + 英文缩写。"""
    return get_placeholder(
        cn, width=CARD_W, height=CARD_H, color=color,
        label=cn, sub_label=en, font_size=LABEL,
    )


# ================================================================ 0.1

class FTApplications(InteractiveScene):
    """0.1 应用墙。快速掠过，不停留。"""

    def construct(self):
        # ---------------- 标题
        title = Text("傅里叶变换", font=CH_FONT, font_size=HEADING * 1.5, color=WHITE)
        subtitle = Text("Fourier Transform", font=EN_FONT, font_size=LABEL, color=MUTED)
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.32)
        title_group.move_to(ORIGIN)

        self.play(Write(title), FadeIn(subtitle, UP), run_time=1.6)
        self.wait(1.0)

        # 标题收到顶部，把画面让给墙
        self.play(
            title_group.animate.scale(0.46).to_edge(UP, buff=0.42),
            run_time=1.0,
        )

        note = NarrationBoard(self)
        note.say("它几乎藏在每一件现代技术里", hold=1.8)

        # ---------------- 应用墙：从中心散开，一瞬间铺满
        cards = VGroup(*[
            get_app_card(cn, en, WALL_COLORS[i % len(WALL_COLORS)])
            for i, (cn, en) in enumerate(APP_WALL)
        ])
        cards.arrange_in_grid(n_rows=3, n_cols=4, buff=0.24)
        cards.move_to(DOWN * 0.28)

        self.play(
            LaggedStart(*[
                FadeIn(card, scale=1.5, shift=card.get_center() * 0.10)
                for card in cards
            ], lag_ratio=0.07, run_time=1.5),
        )
        # 先让观众看清多彩的墙，再开始扫描；否则原始配色一闪就被黄色盖掉
        self.wait(1.4)

        # ---------------- 亮度扫描：像点名一样挨个亮一下再复原
        self.play(
            LaggedStart(*[
                card[0].animate.set_stroke(color=ACCENT, width=4.2)
                for card in cards
            ], lag_ratio=0.06, run_time=1.5),
        )
        self.play(
            *[
                card[0].animate.set_stroke(
                    color=WALL_COLORS[i % len(WALL_COLORS)], width=1.8,
                )
                for i, card in enumerate(cards)
            ],
            run_time=0.7,
        )

        # ---------------- 收束：墙退成背景，浮出主题
        note.say("音频、图像、通信、医疗、天文……背后是同一个变换", hold=3.2)
        self.play(
            cards.animate.set_opacity(0.13).scale(0.95),
            title_group.animate.set_opacity(0.13),
            run_time=1.2,
        )

        note.clear()
        fft_cn = Text("快速傅里叶变换", font=CH_FONT, font_size=HEADING, color=ACCENT)
        # 英文行用半角括号：Consolas 里全角括号会 fallback 到中文字体，宽得撑破底衬
        fft_en = Text("Fast Fourier Transform (FFT)", font=EN_FONT, font_size=LABEL, color=WHITE)
        fft_group = VGroup(fft_cn, fft_en).arrange(DOWN, buff=0.34)
        # 底衬手写而不用 BackgroundRectangle：它给的边距太紧，英文行会贴到框上
        backing = RoundedRectangle(
            width=fft_group.get_width() + 1.4,
            height=fft_group.get_height() + 0.9,
            corner_radius=0.22,
            fill_color=BLACK,
            fill_opacity=0.84,
            stroke_color=ACCENT,
            stroke_width=1.2,
            stroke_opacity=0.35,
        ).move_to(fft_group)

        self.play(FadeIn(backing), Write(fft_cn), FadeIn(fft_en, UP), run_time=1.6)
        self.wait(2.4)
