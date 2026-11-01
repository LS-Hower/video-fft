"""全片统一的视觉主题：字体、字号、配色。

所有场景从这里取值，不要在业务代码里硬写字号或颜色。
"""

from manimlib import *
import manimpango

# ------------------------------------------------------------------ 字体

CH_FONT = "Microsoft YaHei"   # 中文解说文本，本机已确认存在
EN_FONT = "Consolas"          # 代码/英文标签

if CH_FONT not in manimpango.list_fonts():
    raise RuntimeError(f"缺少中文字体 {CH_FONT}，请先在系统安装或改 utils/theme.py 的 CH_FONT")

# ------------------------------------------------------------------ 字号

HEADING = 60        # 章节标题
KEY_FORMULA = 48    # 主角公式
LABEL = 36          # 一般标签
SMALL_LABEL = 24    # 单位圆/坐标轴标注
TINY = 18           # 脚注、下标说明

# ------------------------------------------------------------------ 配色

EVEN_COLOR = BLUE_C      # 偶数项 / 左半（BLUE_D 在深色背景上偏暗，统一用 C 档）
ODD_COLOR = GREEN_C      # 奇数项 / 右半
Z_COLOR = EVEN_COLOR     # 第一章的第一个操作数 z，沿用同一套蓝/绿
W_COLOR = ODD_COLOR      # 第一章的第二个操作数 w
ROOT_COLOR = TEAL_C      # 单位根
ACCENT = YELLOW_C        # 唯一的强调色（一根打通全片）
SUM_COLOR = RED_C        # 求和/重心/负号支
MUTED = GREY_A           # 次要元素
COST_COLOR = RED_C       # O(n^2) 一侧
FAST_COLOR = TEAL_C      # O(n log n) 一侧
