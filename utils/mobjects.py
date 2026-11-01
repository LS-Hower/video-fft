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

def get_nth_roots(n: int, sign: float = 1.0) -> np.ndarray:
    """n 个单位根 ω_n^k。数值一律取自 utils.fft，不在这里另算。"""
    return roots_of_unity(n, sign=sign)


def get_root_dots(plane, n: int, sign: float = 1.0, color=ROOT_COLOR, radius=0.09):
    return VGroup(*[
        get_complex_dot(plane, z, color=color, radius=radius)
        for z in get_nth_roots(n, sign)
    ])


def get_root_labels(plane, n: int, sign: float = 1.0, color=ROOT_COLOR, font_size=SMALL_LABEL):
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
    """底部字幕占位。正式字幕系统上线后由 script.md 的旁白稿驱动。"""
    return Text(text, font=CH_FONT, font_size=font_size, color=color).to_edge(DOWN, buff=0.35)


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
