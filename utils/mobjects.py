"""可复用构件工厂。

规格见 AGENTS.md §4：复用构件写成模块级 `get_*` 工厂函数，几何坐标一律由
ComplexPlane 换算，业务代码里不出现手算坐标。

借鉴过 3b1b 代码（CC BY-NC-SA 4.0）的地方已在 docstring 注明出处，实现为本仓库重写。
"""

from manimlib import *
import numpy as np

from utils.theme import *
from utils.fft import roots_of_unity


# ------------------------------------------------------------------ 复平面

def get_plane(
    x_range=(-9, 9, 2),
    y_range=(-6, 6, 2),
    unit: float = 0.55,
    **kwargs,
) -> ComplexPlane:
    """一张复平面。`unit` = 一个数学单位对应多少屏幕单位（即单位圆半径）。"""
    x_min, x_max, _ = x_range
    y_min, y_max, _ = y_range
    style = dict(
        background_line_style=dict(stroke_color=BLUE_E, stroke_width=1, stroke_opacity=0.35),
        faded_line_style=dict(stroke_color=BLUE_E, stroke_width=1, stroke_opacity=0.12),
        axis_config=dict(stroke_color=GREY_B, stroke_width=2, include_ticks=False),
    )
    style.update(kwargs)
    return ComplexPlane(
        x_range,
        y_range,
        width=(x_max - x_min) * unit,
        height=(y_max - y_min) * unit,
        **style,
    )


def plane_unit(plane: ComplexPlane) -> float:
    """平面上 1 个单位对应的屏幕长度。"""
    return float(np.linalg.norm(plane.n2p(1) - plane.n2p(0)))


def get_unit_circle(plane, color=MUTED, stroke_width=2, opacity=0.9):
    return Circle(
        radius=plane_unit(plane),
        arc_center=plane.n2p(0),
        stroke_color=color,
        stroke_width=stroke_width,
        stroke_opacity=opacity,
    )


def get_complex_dot(plane, z, color=WHITE, radius=0.09):
    return Dot(plane.n2p(z), radius=radius, fill_color=color)


def get_complex_arrow(plane, z, color=WHITE, stroke_width=4, buff=0.0):
    return Arrow(
        plane.n2p(0),
        plane.n2p(z),
        buff=buff,
        color=color,
        stroke_width=stroke_width,
    )


def get_complex_label(plane, z, tex, direction=UR, color=WHITE, font_size=SMALL_LABEL, buff=0.12):
    label = Tex(tex, font_size=font_size, color=color)
    label.next_to(plane.n2p(z), direction, buff=buff)
    return label


def get_angle_arc(plane, z, radius=0.6, color=ACCENT, stroke_width=3):
    """从正实轴扫到 z 的辐角圆弧。

    manimgl 1.7 没有 Angle / RightAngle，用 Arc 手搭；半径单位是屏幕单位。
    """
    return Arc(
        start_angle=0.0,
        angle=float(np.angle(z)),
        radius=radius,
        arc_center=plane.n2p(0),
        stroke_color=color,
        stroke_width=stroke_width,
    )


# ------------------------------------------------------------------ 单位根

def get_nth_roots(n: int, sign: float = -1.0) -> np.ndarray:
    """n 个单位根 ω_n^k。数值一律取自 utils.fft，默认与 DFT / np.fft 同为负号。"""
    return roots_of_unity(n, sign=sign)


def get_root_dots(plane, n: int, sign: float = -1.0, color=ROOT_COLOR, radius=0.09):
    return VGroup(*[
        get_complex_dot(plane, z, color=color, radius=radius)
        for z in get_nth_roots(n, sign)
    ])


def get_root_labels(plane, n: int, sign: float = -1.0, color=ROOT_COLOR, font_size=SMALL_LABEL):
    """ω^0 … ω^{n-1} 的标签，一律朝远离原点的方向摆。"""
    labels = VGroup()
    for k, z in enumerate(get_nth_roots(n, sign)):
        direction = normalize(plane.n2p(z) - plane.n2p(0))
        labels.add(get_complex_label(
            plane, 1.35 * z, Rf"\omega^{{{k}}}",
            direction=direction, color=color, font_size=font_size,
        ))
    return labels


# ------------------------------------------------------------------ 文字

def get_caption(text: str, font_size=LABEL, color=GREY_B):
    """屏幕底部一行讲解文字的占位。不配音，文字即讲解；文案在实现场景时按 scripts/manual_script.md 对应章节撰写。"""
    return Text(text, font=CH_FONT, font_size=font_size, color=color).to_edge(DOWN, buff=0.35)


class NarrationBoard:
    """不配音时承载全部讲解的屏幕文字板，位于画面底部。

    用法（场景内）::

        note = NarrationBoard(self)
        note.say("完整的一句讲解")   # 淡入 + 停留到能读完
        self.play(几何动画)          # 文字静止后再动，避免同时既读又动
        note.say("下一句讲解")       # 旧的淡出、新的淡入
        note.clear()                 # 结论公式出现前腾出底部位置

    ``hold`` 是留给观众的阅读时间，长句可逐句调大。文字与结论公式共用底部区域，
    二者不得同时出现 —— 出公式前先 clear()。
    """

    def __init__(self, scene, font_size=NARRATION, color=GREY_B):
        self.scene = scene
        self.font_size = font_size
        self.color = color
        self.current = None

    def _make(self, text: str):
        line = Text(text, font=CH_FONT, font_size=self.font_size, color=self.color)
        # 长句保护：超过安全宽度就等比缩字，宁可小一点也不能顶出画面。
        # 不配音时文字是唯一讲解通道，宁可断句也不让观众看不到半句话。
        max_width = 2 * (FRAME_X_RADIUS - 0.7)
        if line.get_width() > max_width:
            line.scale(max_width / line.get_width())
        line.to_edge(DOWN, buff=0.45)
        # 半透明底衬压掉网格线：不配音时文字是唯一讲解通道，可读性优先
        bg = BackgroundRectangle(line, fill_color=BLACK, fill_opacity=0.55, buff=0.16)
        return VGroup(bg, line)

    def say(self, text: str, hold: float = 2.5, run_time: float = 0.5):
        new = self._make(text)
        if self.current is None:
            self.scene.play(FadeIn(new, UP), run_time=run_time)
        else:
            self.scene.play(
                FadeOut(self.current, DOWN), FadeIn(new, UP), run_time=run_time,
            )
        self.current = new
        self.scene.wait(hold)
        return new

    def clear(self, run_time: float = 0.4):
        if self.current is not None:
            self.scene.play(FadeOut(self.current, DOWN), run_time=run_time)
            self.current = None


def get_readout(
    label_tex,
    value: float = 0.0,
    num_decimal_places: int = 3,
    unit=None,
    font_size=LABEL,
    color=WHITE,
):
    """一行「Tex 标签 + 可更新的数字」，返回 `(VGroup, DecimalNumber)`。"""
    number = DecimalNumber(
        value,
        num_decimal_places=num_decimal_places,
        unit=unit,
        font_size=font_size,
        color=color,
    )
    group = VGroup(
        Tex(label_tex, font_size=font_size, color=color),
        number,
    ).arrange(RIGHT, buff=0.15)
    return group, number
