"""数学基础：复数几何、欧拉公式、单位根。

场景顺序 = 成片顺序。内容边界以 `scripts/manual_script.md` 的「数学基础」节为准，改内容先改脚本。
讲解全部由屏幕文字承载（不配音），统一走 `utils/mobjects.py` 的 `NarrationBoard`：
文字先静止出现并留足阅读时间，再做几何动画；出结论公式前先 clear() 腾出底部。
"""

from manimlib import *
import numpy as np

from utils.theme import *
from utils.mobjects import *


def get_live_point(plane, r_tracker, theta_tracker, color, label_tex=R"z", direction=DR):
    """跟随 (模长, 辐角) 两个 tracker 的「箭头 + 点 + 标签」。

    返回 `(VGroup, value_fn)`，value_fn() 给出当前复数。
    标签用 add_updater 而不是 always_redraw —— Tex 每帧重编译太慢。
    """
    def value():
        return r_tracker.get_value() * np.exp(1j * theta_tracker.get_value())

    arrow = always_redraw(lambda: get_complex_arrow(plane, value(), color=color))
    dot = always_redraw(lambda: get_complex_dot(plane, value(), color=color))
    label = Tex(label_tex, font_size=SMALL_LABEL, color=color)
    label.add_updater(lambda m: m.next_to(plane.n2p(value()), direction, buff=0.12))

    return VGroup(arrow, dot, label), value


# ================================================================ 1.1

class ProductAsRotation(InteractiveScene):
    """1.1 复数乘法 = 拉伸 + 旋转。本节重头：模相乘、辐角相加。"""
    Z = complex(2, 1)
    W = complex(1, 2)
    X_RANGE = (-9, 9, 2)
    Y_RANGE = (-6, 6, 2)
    UNIT = 0.55

    def construct(self):
        z, w = self.Z, self.W
        plane = get_plane(self.X_RANGE, self.Y_RANGE, unit=self.UNIT)
        self.add(plane, get_unit_circle(plane))

        # ---- z 与实时读数
        r_tracker = ValueTracker(abs(z))
        theta_tracker = ValueTracker(float(np.angle(z)))
        z_group, z_value = get_live_point(plane, r_tracker, theta_tracker, Z_COLOR, R"z")

        mod_row, mod_num = get_readout(R"\vert z \vert =", abs(z), 3, color=Z_COLOR)
        arg_row, arg_num = get_readout(
            R"\arg z =", float(np.degrees(np.angle(z))), 1, unit=R"^\circ", color=Z_COLOR,
        )
        panel = VGroup(mod_row, arg_row).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        panel.to_corner(UL, buff=0.5)
        mod_num.add_updater(lambda m: m.set_value(r_tracker.get_value()))
        arg_num.add_updater(lambda m: m.set_value(float(np.degrees(theta_tracker.get_value()))))

        self.play(GrowArrow(z_group[0]), FadeIn(z_group[1], scale=0.5))
        self.play(Write(z_group[2]), FadeIn(panel, shift=RIGHT))
        self.wait()

        note = NarrationBoard(self)
        note.say("每个复数有两个身份：模长是离原点的距离，辐角是相对正实轴转过的角度", hold=3.0)

        # ---- ① 乘 3：只拉伸，不转向
        note.say("先看拉伸：乘 3 把模长变成三倍，方向一点没变", hold=2.5)
        times3 = Tex(R"\times 3", font_size=LABEL, color=ACCENT)
        times3.next_to(z_group[2], RIGHT, buff=0.35)
        ray = DashedLine(plane.n2p(0), plane.n2p(3.4 * z), color=MUTED, stroke_width=1.5)
        self.play(ShowCreation(ray), Write(times3))
        self.play(r_tracker.animate.set_value(abs(z) * 3), run_time=1.6)
        self.wait(1.0)
        self.play(FadeOut(ray), FadeOut(times3))
        self.play(r_tracker.animate.set_value(abs(z)), run_time=0.8)

        # ---- ② 乘 i：只旋转，不改长度
        note.say("再看旋转：乘 i 绕原点转 90°，长度不变", hold=2.5)
        times_i = Tex(R"\times i", font_size=LABEL, color=ACCENT)
        times_i.next_to(z_group[2], RIGHT, buff=0.35)
        self.play(Write(times_i))

        arg_z = float(np.angle(z))
        arcs = VGroup()
        for step in (1, 2):
            arc = Arc(
                start_angle=arg_z + (step - 1) * PI / 2,
                angle=PI / 2,
                radius=0.8 + 0.3 * step,
                arc_center=plane.n2p(0),
                stroke_color=ACCENT,
                stroke_width=3,
            )
            arcs.add(arc)
            self.play(
                ShowCreation(arc),
                theta_tracker.animate.set_value(arg_z + step * PI / 2),
                run_time=1.4,
            )
        i_note = Tex(R"i^2 = -1", font_size=LABEL, color=ACCENT)
        i_note.next_to(z_group[2], DR, buff=0.2)
        self.play(Write(i_note))
        self.wait(1.0)
        # Circle 是 Arc 的子类，清弧只清自己建的那一组，别顺手删掉单位圆
        self.play(FadeOut(times_i), FadeOut(i_note), FadeOut(arcs))
        self.play(theta_tracker.animate.set_value(arg_z), run_time=0.8)

        # ---- ③ z · w：先拉伸，再旋转
        note.say("一般乘法就是两件事一起做：模长相乘、辐角相加", hold=3.0)
        w_group = VGroup(
            get_complex_arrow(plane, w, color=W_COLOR),
            get_complex_dot(plane, w, color=W_COLOR),
            get_complex_label(plane, w, R"w = 1+2i", RIGHT, color=W_COLOR),
        )
        z_arc = get_angle_arc(plane, z, radius=0.7, color=ACCENT)
        w_arc = get_angle_arc(plane, w, radius=1.0, color=W_COLOR)
        self.play(
            LaggedStart(GrowArrow(w_group[0]), FadeIn(w_group[1], scale=0.5),
                        Write(w_group[2]), lag_ratio=0.3),
        )
        self.play(ShowCreation(z_arc), ShowCreation(w_arc))
        self.wait(1.0)
        self.play(r_tracker.animate.set_value(abs(z) * abs(w)), run_time=1.3)
        self.wait(0.8)
        self.play(
            Rotate(w_arc, angle=arg_z, about_point=plane.n2p(0)),
            theta_tracker.animate.set_value(arg_z + float(np.angle(w))),
            run_time=1.6,
        )
        self.wait(1.0)

        product = z * w
        final_arrow = get_complex_arrow(plane, product, color=ACCENT)
        final_dot = get_complex_dot(plane, product, color=ACCENT)
        z_group[0].clear_updaters()
        z_group[1].clear_updaters()
        self.play(
            FadeOut(z_group[0]), FadeOut(z_group[1]), FadeOut(z_group[2]),
            FadeIn(final_arrow), FadeIn(final_dot),
        )
        product_label = get_complex_label(
            plane, product, R"zw = 5i", RIGHT, color=ACCENT, font_size=LABEL,
        )
        self.play(Write(product_label))

        # 读数面板从 z 换成 zw
        new_panel = VGroup(
            get_readout(R"\vert zw \vert =", abs(product), 3, color=ACCENT)[0],
            get_readout(R"\arg(zw) =", float(np.degrees(np.angle(product))), 1,
                        unit=R"^\circ", color=ACCENT)[0],
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        new_panel.move_to(panel, UL)
        self.play(FadeOut(panel, shift=DOWN), FadeIn(new_panel, shift=UP))
        self.wait(1.0)

        note.clear()
        identities = VGroup(
            Tex(R"\vert zw \vert = \vert z \vert \cdot \vert w \vert", font_size=LABEL, color=ACCENT),
            Tex(R"\arg(zw) = \arg z + \arg w", font_size=LABEL, color=ACCENT),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        identities.to_edge(DOWN, buff=0.4)
        self.play(LaggedStart(*[FadeIn(m, shift=UP) for m in identities], lag_ratio=0.4))
        self.wait(3.0)


# ================================================================ 1.2

class QuotientGeometry(InteractiveScene):
    """1.2 除法是乘法的镜像：模长相除、辐角相减。简短带过，不重复 1.1 的铺垫。"""
    Z = complex(2, 1)
    W = complex(1, 2)
    X_RANGE = (-9, 9, 2)
    Y_RANGE = (-6, 6, 2)
    UNIT = 0.55

    def construct(self):
        z, w = self.Z, self.W
        plane = get_plane(self.X_RANGE, self.Y_RANGE, unit=self.UNIT)
        self.add(plane, get_unit_circle(plane))

        r_tracker = ValueTracker(abs(z))
        theta_tracker = ValueTracker(float(np.angle(z)))
        z_group, _ = get_live_point(plane, r_tracker, theta_tracker, Z_COLOR, R"z")

        mod_row, mod_num = get_readout(R"\vert z \vert =", abs(z), 3, color=Z_COLOR)
        arg_row, arg_num = get_readout(
            R"\arg z =", float(np.degrees(np.angle(z))), 1, unit=R"^\circ", color=Z_COLOR,
        )
        panel = VGroup(mod_row, arg_row).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        panel.to_corner(UL, buff=0.5)
        mod_num.add_updater(lambda m: m.set_value(r_tracker.get_value()))
        arg_num.add_updater(lambda m: m.set_value(float(np.degrees(theta_tracker.get_value()))))

        self.add(z_group, panel)

        note = NarrationBoard(self)
        note.say("除法是乘法的反面：模长相除、辐角相减", hold=3.0)

        w_label = Tex(R"\div w", font_size=LABEL, color=W_COLOR)
        w_label.next_to(z_group[2], RIGHT, buff=0.35)
        self.play(Write(w_label))
        self.play(r_tracker.animate.set_value(abs(z) / abs(w)), run_time=1.3)
        self.play(
            theta_tracker.animate.set_value(float(np.angle(z) - np.angle(w))),
            run_time=1.3,
        )
        self.wait(1.0)

        result_label = get_complex_label(
            plane, z / w, R"z / w", DR, color=ACCENT, font_size=LABEL,
        )
        self.play(Write(result_label))
        self.wait(1.0)

        note.say("乘 w 与除以 w 互为逆运算，把模长和角度分别还原", hold=2.5)

        note.clear()
        identities = VGroup(
            Tex(R"\vert z/w \vert = \vert z \vert / \vert w \vert", font_size=LABEL, color=ACCENT),
            Tex(R"\arg(z/w) = \arg z - \arg w", font_size=LABEL, color=ACCENT),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        identities.to_edge(DOWN, buff=0.4)
        self.play(FadeOut(w_label), LaggedStart(*[FadeIn(m, shift=UP) for m in identities], lag_ratio=0.4))
        self.wait(3.0)


# ================================================================ 1.3

class EulerFormula(InteractiveScene):
    """1.3 欧拉公式只当工具：给模长 1 的复数一个简写，再推广到极坐标表示 z = r e^{iθ}。"""
    X_RANGE = (-5.5, 5.5, 1)
    Y_RANGE = (-3.2, 3.2, 1)
    UNIT = 1.1
    THETA = TAU / 8

    def construct(self):
        plane = get_plane(self.X_RANGE, self.Y_RANGE, unit=self.UNIT)
        circle = get_unit_circle(plane, color=ROOT_COLOR, stroke_width=3)
        self.add(plane, circle)

        r_tracker = ValueTracker(1.0)
        theta_tracker = ValueTracker(0.0)

        def value():
            return r_tracker.get_value() * np.exp(1j * theta_tracker.get_value())

        arrow = always_redraw(lambda: get_complex_arrow(plane, value(), color=ACCENT))
        dot = always_redraw(lambda: get_complex_dot(plane, value(), color=ACCENT))
        label = Tex(R"e^{i\theta}", font_size=LABEL, color=ACCENT)
        label.add_updater(lambda m: m.next_to(plane.n2p(value()), UR, buff=0.12))

        # cos / sin 投影（仅 r = 1 阶段展示，r 变动时淡出，避免标签与数值不符）
        x_proj = always_redraw(lambda: DashedLine(
            plane.n2p(value()), plane.n2p(complex(value().real, 0)),
            color=EVEN_COLOR, stroke_width=2,
        ))
        y_proj = always_redraw(lambda: DashedLine(
            plane.n2p(value()), plane.n2p(complex(0, value().imag)),
            color=ODD_COLOR, stroke_width=2,
        ))
        cos_row, cos_num = get_readout(R"\cos\theta =", 1.0, 3, color=EVEN_COLOR)
        sin_row, sin_num = get_readout(R"\sin\theta =", 0.0, 3, color=ODD_COLOR)
        panel = VGroup(cos_row, sin_row).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        panel.to_corner(UR, buff=0.5)
        cos_num.add_updater(lambda m: m.set_value(float(value().real)))
        sin_num.add_updater(lambda m: m.set_value(float(value().imag)))

        one_label = get_complex_label(plane, 1, R"1", DR, color=WHITE)
        self.play(GrowArrow(arrow), FadeIn(dot, scale=0.5), Write(one_label))
        self.play(Write(label), FadeIn(panel, shift=LEFT))

        note = NarrationBoard(self)
        note.say("单位圆上的复数模长都是 1，只剩「转了多少」这一个自由度", hold=3.0)
        self.play(ShowCreation(x_proj), ShowCreation(y_proj))
        self.play(theta_tracker.animate.set_value(self.THETA), run_time=1.4)
        self.wait(1.2)

        note.say("于是给它一个简写，写成 e 的 iθ 次方：θ 就是转过的角度", hold=3.0)
        self.play(theta_tracker.animate.set_value(2 * self.THETA), run_time=1.0)
        self.wait(1.0)

        # 欧拉公式只当工具，短暂显示后收起
        note.clear()
        euler = Tex(R"e^{i\theta} = \cos\theta + i\sin\theta",
                    font_size=KEY_FORMULA, color=ACCENT)
        euler.to_edge(DOWN, buff=0.9)
        self.play(Write(euler))
        self.wait(3.0)
        self.play(FadeOut(euler, UP))

        # 推广：乘上模长 r，得到极坐标表示
        note.say("再乘上模长 r，任意复数都能写成「模长乘旋转」，这就是极坐标表示", hold=4.0)
        self.play(FadeOut(panel, UP), FadeOut(one_label),
                  FadeOut(x_proj), FadeOut(y_proj))
        label.clear_updaters()
        r_label = Tex(R"z = r e^{i\theta}", font_size=LABEL, color=ACCENT)
        r_label.add_updater(lambda m: m.next_to(plane.n2p(value()), UR, buff=0.12))
        self.play(FadeOut(label), FadeIn(r_label))
        self.play(r_tracker.animate.set_value(2.0), run_time=1.4)
        self.wait(1.0)
        self.play(theta_tracker.animate.set_value(self.THETA), run_time=1.0)
        self.wait(1.0)

        note.say("转满一整圈回到 1，这些等分位置就是单位根", hold=3.0)
        self.play(r_tracker.animate.set_value(1.0), run_time=0.8)
        self.play(theta_tracker.animate.set_value(TAU), run_time=1.6)
        self.wait(2.0)


# ================================================================ 1.4

class RootsOfUnity(InteractiveScene):
    """1.4 单位根的几何与两条引理。

    思路参考 3b1b/videos/_2022/convolutions/discrete.py:2468 `RootsOfUnity`
    (CC BY-NC-SA 4.0)，按本仓库规范重写。
    """
    N = 8
    X_RANGE = (-4.5, 4.5, 1)
    Y_RANGE = (-2.6, 2.6, 1)
    UNIT = 1.05   # 求和链最低到 y≈-2.4（数学单位），缩小平面才不压到底部文字/公式

    def construct(self):
        n = self.N
        plane = get_plane(self.X_RANGE, self.Y_RANGE, unit=self.UNIT)
        circle = get_unit_circle(plane, color=ROOT_COLOR, stroke_width=3)
        self.add(plane, circle)

        # 全片统一 ω_n = e^{-2πi/n}（默认 sign=-1，与 utils/fft.py / np.fft 一致）
        roots = get_nth_roots(n)
        dots = get_root_dots(plane, n)
        spokes = VGroup(*[
            Line(plane.n2p(0), plane.n2p(z), color=ROOT_COLOR, stroke_width=1.5, stroke_opacity=0.4)
            for z in roots
        ])

        definition = Tex(R"\omega_n = e^{-2\pi i / n}", font_size=KEY_FORMULA, color=ACCENT)
        definition.to_corner(UL, buff=0.5)
        self.play(Write(definition))

        note = NarrationBoard(self)
        note.say("1 的 n 次方根把单位圆平均分成 n 份；逐个乘下去就能走遍这些位置", hold=3.5)
        self.play(
            LaggedStart(*map(ShowCreation, spokes), lag_ratio=0.08, run_time=2),
            LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.08, run_time=2),
        )
        labels = get_root_labels(plane, n)
        self.play(LaggedStart(*map(Write, labels), lag_ratio=0.08, run_time=1.5))
        self.wait(1.0)

        # ---------------- 性质① 半圈反号
        note.say("转半圈恰好落到 -1，这就是半圈反号", hold=3.0)
        opposite = VGroup(*[
            DashedLine(plane.n2p(roots[k]), plane.n2p(roots[k + n // 2]),
                       color=SUM_COLOR, stroke_width=2)
            for k in range(n // 2)
        ])
        # 高亮这两个对径点：各自在原点位放大，不能整体 scale（VGroup 会以两点中点为心，把它们推到圆外）
        highlight = VGroup(*[
            get_complex_dot(plane, roots[k], color=ACCENT, radius=0.17)
            for k in (0, n // 2)
        ])
        self.play(
            LaggedStart(*map(ShowCreation, opposite), lag_ratio=0.15, run_time=1.5),
            FadeIn(highlight, scale=1.5),
        )
        minus_one = get_complex_label(plane, roots[n // 2], R"= -1", LEFT,
                                     color=ACCENT, font_size=LABEL)
        self.play(Write(minus_one))
        self.wait(1.0)

        note.clear()
        sym_formula = Tex(R"\omega_n^{k + n/2} = -\omega_n^{k}",
                          font_size=LABEL, color=ACCENT)
        sym_formula.to_corner(UR, buff=0.45)
        self.play(Write(sym_formula))
        self.wait(2.5)
        self.play(FadeOut(sym_formula, UP), FadeOut(opposite),
                  FadeOut(highlight), FadeOut(minus_one))

        # ---------------- 性质② 折半引理（重点镜头）
        note.say("折半引理：每个根平方一下，八个位置塌缩成四个", hold=3.0)
        half_roots = get_nth_roots(n // 2)
        # 点塌缩后旧的 ω^k 标签不再对应任何点，一起淡出，避免 4 个标签悬空。
        # spokes 同理：8 条 45° 辐条里有 4 条没有点了，留着会误导成「还是八个根」。
        self.play(
            FadeOut(labels),
            FadeOut(spokes),
            *[dots[k].animate.move_to(plane.n2p(roots[k] ** 2)) for k in range(n)],
            run_time=2.0,
        )
        self.wait(1.0)
        rings = VGroup(*[
            Circle(radius=0.22, stroke_color=ACCENT, stroke_width=3).move_to(plane.n2p(z))
            for z in half_roots
        ])
        self.play(LaggedStart(*map(ShowCreation, rings), lag_ratio=0.2, run_time=1.5))
        half_labels = get_root_labels(plane, n // 2, color=WHITE)
        self.play(LaggedStart(*map(Write, half_labels), lag_ratio=0.2, run_time=1.2))
        self.wait(1.0)

        note.clear()
        halving_formula = Tex(R"(\omega_n^{k})^2 = \omega_{n/2}^{k}",
                              font_size=LABEL, color=ACCENT)
        halving_formula.to_corner(UR, buff=0.45)
        self.play(Write(halving_formula))
        self.wait(2.5)
        self.play(FadeOut(halving_formula, UP), FadeOut(rings), FadeOut(half_labels))

        # ---------------- 性质③ 求和为零
        # 先清掉折半引理留下的点：八边形链条要独占画面，否则和圆上的点糊成一团
        self.play(FadeOut(dots))
        note.say("绕一整圈首尾相接，向量和为零", hold=3.0)
        omega = get_nth_roots(n)[1]
        partial = np.cumsum(omega ** np.arange(n))
        chain = VGroup()
        prev = 0j
        for value in partial:
            chain.add(Arrow(
                plane.n2p(prev), plane.n2p(value), buff=0,
                color=SUM_COLOR, stroke_width=2.5, tip_width_ratio=3,
            ))
            prev = value
        self.play(LaggedStart(*map(GrowArrow, chain), lag_ratio=0.15, run_time=2.5))
        # 终点落回原点，用 LEFT 而不是 DL：链条从原点向右出发，左上方才是空位
        zero_label = get_complex_label(plane, 0, R"0", LEFT, color=SUM_COLOR, font_size=LABEL)
        self.play(Write(zero_label))
        self.wait(1.0)

        note.clear()
        sum_formula = Tex(
            R"\sum_{k=0}^{n-1} (\omega_n^{j})^{k} = 0 \quad (j \not\equiv 0 \bmod n)",
            font_size=LABEL, color=SUM_COLOR,
        )
        sum_formula.to_corner(UR, buff=0.45)
        self.play(Write(sum_formula))
        self.wait(3.0)
