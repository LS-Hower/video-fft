"""代码展示：以一份滚动的 FFT 实现收尾。

剧本要求「以一份滚动的 FFT 代码结束该视频，见 assets/fft_example.cpp，
在视频中以浮窗方式为代码各处添加讲解」。

这份代码用「正号做正变换」的约定，与全片（及 utils/fft.py、np.fft）的负号约定
互为镜像，内部自洽、结果等价。展示时用浮窗点明，不改代码。
"""

from pathlib import Path

from manimlib import *

from utils.theme import *
from utils.mobjects import *

CODE_PATH = Path(__file__).resolve().parent.parent / "assets" / "fft_example.cpp"


def popup(text, color=ACCENT, max_width=4.6):
    """右下角的讲解浮窗：半透明黑底 + 强调色描边。"""
    body = Text(text, font=CH_FONT, font_size=BODY, color=WHITE)
    if body.get_width() > max_width:
        body.scale(max_width / body.get_width())
    bg = RoundedRectangle(
        width=body.get_width() + 0.64,
        height=body.get_height() + 0.46,
        corner_radius=0.16,
        fill_color=BLACK, fill_opacity=0.86,
        stroke_color=color, stroke_width=1.6,
    )
    body.move_to(bg)
    return VGroup(bg, body)


# ================================================================ 5.0

class RollingCode(InteractiveScene):
    """5.0 代码滚动 + 浮窗。"""

    FONT_SIZE = 10
    SEGMENTS = [4.2, 4.4, 4.2, 4.4, 4.2, 3.0]

    def construct(self):
        raw = CODE_PATH.read_text(encoding="utf-8")

        # 不能用 manimgl 的 Code / MarkupText：这个版本的 Text 不支持 \n，
        # 多行字符串会被排成逐字符竖排。逐行建 Text 再纵向排列才正确。
        lines = VGroup(*[
            Text(ln.rstrip() if ln.strip() else " ",
                 font=EN_FONT, font_size=self.FONT_SIZE, color=GREY_B)
            for ln in raw.splitlines()
        ])
        lines.arrange(DOWN, aligned_edge=LEFT, buff=0.045)
        code = lines

        # to_edge(UP) 只改纵坐标，set_x 在这里又没生效，直接算中心点最稳：
        # 顶部留 0.45 边距，水平居中
        code.move_to(UP * (FRAME_Y_RADIUS - 0.45 - code.get_height() / 2))
        self.play(FadeIn(code, UP), run_time=1.0)
        self.wait(0.6)

        # 滚动距离按实际高度算，避免硬编码
        travel = max(code.get_height() - (FRAME_Y_RADIUS * 2 - 0.9), 0.0)
        step = travel / len(self.SEGMENTS)

        cues = [
            "递归版：按奇偶下标拆成两半，再各自递归",
            "合并：一次乘法同时喂出 X_k 与 X_{k+n/2}",
            "迭代版：先位反转重排，再逐层做蝶形",
            "三步走：DFT → 逐点相乘 → 逆 DFT",
        ]

        # 分段上滚，每段之间插一张浮窗；滚完正好停在末尾
        for i, run_time in enumerate(self.SEGMENTS):
            self.play(
                code.animate.shift(UP * step),
                run_time=run_time,
                rate_func=linear,
            )
            if i < len(cues):
                card = popup(cues[i], color=ACCENT if i % 2 == 0 else FAST_COLOR)
                card.to_corner(DR, buff=0.55)
                self.play(FadeIn(card, UP), run_time=0.5)
                self.wait(1.6)
                self.play(FadeOut(card, DOWN), run_time=0.4)

        # 约定说明：这份代码的正负号与全片互为镜像
        mirror = popup("这份代码用正号做正变换，与全片的负号约定互为镜像", color=SUM_COLOR)
        mirror.to_corner(DR, buff=0.55)
        self.play(FadeIn(mirror, UP), run_time=0.6)
        self.wait(2.6)
        self.play(FadeOut(mirror, DOWN), run_time=0.4)

        # 收尾：回到片头标题，首尾呼应
        title = Text("傅里叶变换", font=CH_FONT, font_size=HEADING, color=WHITE)
        subtitle = Text("Fourier Transform", font=EN_FONT, font_size=LABEL, color=MUTED)
        ending = VGroup(title, subtitle).arrange(DOWN, buff=0.32).move_to(ORIGIN)

        self.play(FadeOut(code, DOWN), run_time=1.2)
        self.play(FadeIn(ending, UP), run_time=1.4)
        self.wait(3.0)
