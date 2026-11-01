# AGENTS.md — video-fft

讲快速傅里叶变换（FFT）的中文科普视频。用 3b1b 版 Manim（`manimgl`，不是 ManimCommunity）写场景代码并渲染成片。

`script.md` 是内容的事实源：镜头设计、数学推导、口播文本都在那里，代码是它的实现。要改镜头，先改脚本。
`../reference/` 只读，不要改动其中的任何文件。

---

## 1. 环境

Python 3.13.14；ffmpeg 7.1.1（已在 PATH）；GPU RTX 4060 Laptop。manimgl **尚未安装**，源码在 `../reference/manim`（MIT）。

```bash
python -m venv .venv
source .venv/Scripts/activate      # cmd/PowerShell：.venv\Scripts\activate
pip install -e ../reference/manim  # 装本地源码，保证与 reference 的 API 一致
pip install av                     # 当前 requirements 未自动装齐，需手动补
python -m manimlib --version
```

首次装完要验证三件事，缺一项后面都会反复踩：

- `manimgl ../reference/manim/example_scenes.py OpeningManimExample -l` 能出画面；
- 中文能出字：最小场景里 `Text("复数", font=CH_FONT)` 不是豆腐块（字体常量在 `utils/theme.py`）；
- 公式能编译：`Tex(R"\omega_n^{k}")` 可用，不行就装 LaTeX 发行版（Windows 推荐 MiKTeX）。

仓库根需要 `custom_config.yml`（尚未创建）：

```yaml
directories:
  mirror_module_path: False        # 输出平铺到 videos/，不照抄模块路径
  base: ""
  subdirs:
    output: "videos"
    raster_images: "assets/raster_images"
    vector_images: "assets/vector_images"
    data: "assets/data"
camera:
  resolution: (1920, 1080)
  fps: 30
```

`../reference/videos/custom_config.yml` 是 macOS 绝对路径 + 4K + 3b1b 私有资源树，不要照抄。

---

## 2. 目录

```
├── script.md              # 内容脚本
├── custom_config.yml
├── utils/
│   ├── theme.py           # 颜色 / 字号 / 中英文字体常量
│   ├── fft.py             # 朴素 DFT、radix-2 FFT、位反转、NTT（与 np.fft 自检）
│   └── mobjects.py        # 单位圆盘、蝴蝶图、系数表等构件工厂
├── scenes/
│   ├── ch00_opening.py
│   ├── ch01_complex.py    # 复数几何、欧拉公式、单位根性质
│   ├── ch02_motivation.py # 多项式两种表示、卷积、DFT 定义
│   ├── ch03_algorithm.py  # 分治 → 蝴蝶 → 迭代 → FFT 电路
│   ├── ch04_background.py # 历史、FFTW、FT 用途、NTT、大整数乘法、新成果
│   └── ch05_closing.py
├── assets/                # 图片 / SVG / 数据
└── videos/                # 渲染产物，已 gitignore
```

场景类在文件中的排列顺序 = 成片顺序。

---

## 3. 命令

**始终用 `python -m manimlib`，不用 `manimgl` 可执行脚本** —— 后者不把当前目录放进 `sys.path`，`from utils.theme import *` 会 ModuleNotFoundError。

```bash
python -m manimlib scenes/ch01_complex.py ProductAsRotation -l        # 480p 预览（开窗）
python -m manimlib scenes/ch01_complex.py ProductAsRotation -w -s     # 只存最后一帧（排错最快）
python -m manimlib scenes/ch01_complex.py ProductAsRotation -w        # 渲染 mp4 到 videos/
python -m manimlib scenes/ch01_complex.py ProductAsRotation -w -o     # 渲染完自动打开
python -m manimlib scenes/ch01_complex.py ProductAsRotation -e 120    # 第 120 行进交互式 iPython（旧写法 -se）
python -m manimlib scenes/ch01_complex.py -a -l -w                    # 整文件所有场景
python -m manimlib scenes/ch01_complex.py SceneX -w -n 3,6            # 只渲染第 3~6 个动画
```

`-p` 在这个版本是 presenter mode，**不是** preview。只加 `-s` 不加 `-w` 会开窗等待交互；离线出图必须 `-w -s`。交互式下 `checkpoint_paste()` 的用法见 `../reference/videos/README.md`。

---

## 4. 代码规范

- 首行 `from manimlib import *`；跨模块用 `from utils.theme import *` 之类的显式导入。
- 基类默认 `InteractiveScene`（可拖拽选中，方便调构图）；纯 2D 镜头用 `Scene` 也行。
- 相机是 `self.frame`（`frame.reorient(...)`）；动态几何用 `always_redraw`，只改位置样式用 `add_updater` / `.always`。
- 复数相关一律走 `ComplexPlane(x_range, y_range)` + `n2p()` / `p2n()`，复数转三维点用 `complex_to_R3()`。
- 公式用 `Tex(R"...")`（本版本**没有** `MathTex`），着色 `t2c={...}`；中文用 `Text(..., font=CH_FONT)`，字体名不在业务代码里硬写。
- 常量模块级 `UPPER_SNAKE`；场景可调参数写成**类属性**（如 `N = 8`）。
- 排布只用 `.arrange()` / `.next_to()` / `.get_grid()`，不手算坐标；复用构件写成模块级 `get_*` 工厂函数。
- **数值诚实**：画面上的 DFT/FFT 结果、频谱曲线、蝴蝶图数值必须由 `utils/fft.py` 现算并与 `np.fft` 对照通过，不许为了好看挪数据点。

**旧 manim 写法黑名单**（照抄 reference 老代码会静默失效或报错）

| 禁用 | 改用 |
| --- | --- |
| `CONFIG = {...}` 字典 | 类属性 / `__init__` 参数（**不报错但全部被忽略**） |
| `self.camera_frame` | `self.frame` |
| `OldTex` / `OldTexText` | `Tex` / `Text` |
| `MathTex` | `Tex` |
| `x_min` / `x_max` / `coords_to_point` / `add_numbers()` | `x_range` / `c2p` / `add_coordinate_labels()` |
| `FadeInFromDown` 等 deprecated 动画 | `FadeIn(mob, UP)` / `FadeOut(mob, DOWN)` |

**类型约束**：`GlowDot` / `GlowDots` / `TrueDot` 是 `PMobject`，**不能**进 `VGroup`（要么用 `Group`，要么改用 `Dot`）。

---

## 5. 参考资料（`../reference/`，只读）

| 路径 | 用途 |
| --- | --- |
| `manim/` | manimgl 源码（MIT）。API 的一手真相，写不出效果时先查 `manimlib/mobject/`、`manimlib/animation/` |
| `videos/` | 3b1b 全部视频源码（**CC BY-NC-SA 4.0**，见 §6） |
| `manim_sandbox/` | manim-kindergarten 合集（MIT）。主要查中文字体用法，如 `utils/mobjects/fractal_tree.py:56` 用 `思源黑体 Bold`；非 3b1b 体系，写法不一定对齐本仓库 |
| `Fast-Fourier-transform.wiki` | FFT 维基条目 wikitext 源文件。**所有年份、人名、复杂度数字的一手出处**：History 在第 16 行，复杂度上下界在第 71 行 |
| `An-explicit-power-saving-...-September-25-2026/` | OpenAI Math Release 预印本（2026-09-25）。主定理在 `build/sections/introduction.tex`，措辞要求见 §7 |

### 可复用资产（均已核实存在，行号可能随代码更新漂移）

| 位置 | 名称 | 用途 |
| --- | --- | --- |
| `videos/_2022/convolutions/discrete.py:2468` | `RootsOfUnity` | 单位根画法：`ComplexPlane` + 单位圆 + `np.exp(TAU*1j*k/N)` + `GlowDot` |
| `videos/_2020/18S191/dft.py:4` | `IntroduceDFT` | DFT 的离散"缠绕"演示，与本项目第 2 章最贴近 |
| `videos/_2019/diffyq/part2/fourier_series.py:5` | `FourierCirclesScene` | epicycle 旋转向量链（`get_rotating_vectors` :66、`get_vector_sum_path` :139、`get_coefficients_of_path` :240） |
| `videos/_2018/fourier.py:792` | `FourierMachineScene` | 时域轴/圆平面/频域轴三分屏骨架（:961 缠绕、:3210 质心直觉） |
| `videos/_2022/piano/fourier_animations.py:294` | `break_down_into_fourier_components` | np.fft → 频谱 → 分解正弦波的完整实现 |
| `videos/_2022/convolutions/discrete.py` | `BigPolynomials` :1862、`ContrastConvolutionToMultiplication` :1738、`AlgorithmOutline` :2534、`dist_to_bars` :50 | 系数网格表、卷积↔乘法对照、快速卷积四步框架、条形图三件套 |

**已知坑**

- `_2018/`、`_2019/` 是老版本代码：`FourierMachineScene.CONFIG`、`FourierCirclesScene.CONFIG` 会被静默忽略，坐标用旧参数名。借鉴时必须按 §4 黑名单改造。
- `videos/_2022/convolutions/discrete.py:2792` 的 `FourierCoefficients` 有 bug（`equations = VGroup` 把类赋给了变量），别抄。
- `once_useful_constructs/` 多数文件自述失效（`region.py`、`graph_scene.py`、`complex_transformation_scene.py` 等），要用得先通读再改写。
- `once_useful_constructs/butterfly_curve.py` 的"蝴蝶曲线"与 FFT 蝴蝶运算无关。

---

## 6. 许可

- `reference/videos/` 是 **CC BY-NC-SA 4.0**（含非商业条款）。借鉴思路没问题；需要现成构件时读懂后在 `utils/` 里重写，并在文件头注明 `参考 3b1b/videos/<文件>:<行号> (CC BY-NC-SA 4.0)，已重写`。
- `reference/manim/`（MIT）是库本身，可作为正常依赖使用。
- `assets/` 里的第三方图片、字体先确认许可再用。

---

## 7. 事实核查

1. 历史、人名、年份、复杂度数字必须能在 §5 那两份 reference 原文里定位到出处；查不到就在 `script.md` 里标 `[待核]`，不凭印象写。
2. 预印本就说预印本 —— 用"作者宣称 / 尚待同行评议"，禁止写"已证明""已被突破"。
3. 提 2026-09-25 那份 OpenAI 预印本时，三条限定必须同时交代：精确复数运算模型允许任意大中间系数；常数极大、没有可用的 crossover 估计；不意味着浮点实现或实际算力有相应提升。
4. 上界与下界不许混用。Ω(n log n) 下界只在受限模型下成立（Morgenstern 1973 有界系数、Pan 1986 异步度、Papadimitriou 1979 算法图结构），无条件下界仍是开放问题；那份预印本攻的是**上界**。

---

## 8. 制作流程

1. 照 `script.md` 写场景，不凭空加镜头；需要改镜头先改脚本。
2. 先把 `utils/` 做扎实：`theme.py` 确认字体与配色可用，`fft.py` 实现并与 `np.fft` 对齐通过自检。
3. 一次一个场景：`-l -s` 验构图 → `-l -w` 看运镜 → 最后用默认分辨率 `-w`。
4. 场景类定名后回填 `script.md` 相应小节标题，两边始终对齐。
5. 渲染产物只落在 `videos/`，不进 commit。

---

## 9. 约定与待定

- 视频时长当前估算 ≈ 22 分钟（主干 16 分 + 背景 5 分 + 头尾 1 分），**仅用于排布参考**：制作过程中按内容需要随时调整，不要为了贴合时长砍内容；有变动就同步更新 `script.md` 的时长标注。
- 单支，不成系列。
- 全中文解说，公式保留拉丁/希腊符号；中文文本字体由 `utils/theme.py` 的 `CH_FONT` 统一决定。
- 第一版先把第 1–3 章做完整；第 4 章（背景）允许先用较简单的静态镜头，后期再补。
- 暂不做配音，只出字幕；字幕文本以 `script.md` 的旁白稿为准。
