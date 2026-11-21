# 制作约定

> 本文件是 `scripts/manual_script.md` 的配套制作对齐信息，不是分镜。剧本各节「快速掠过 / 三秒贴完 / 一带而过 / 占位符」等指示性标注就是节奏约定，照做即可；不预设时长、不预先写死逐句讲解稿、不写逐帧画面。

## 符号与术语

| 项 | 约定 |
| --- | --- |
| 单位根 | $\omega_n = \mathrm{e}^{-2\pi\mathrm{i}/n}$ |
| DFT | $X_k = \sum_{m=0}^{n-1} x_m\,\omega_n^{km}$；逆变换改用正号并除以 $n$ |
| 折半引理 | $\omega_n^{2k} = \omega_{n/2}^{k}$ |
| 消去引理 | $\omega_n^{k+n/2} = -\omega_n^{k}$ |
| 全称 | DFT = 离散傅里叶变换 / Discrete Fourier Transform；FFT = 快速傅里叶变换 / Fast Fourier Transform（首次出现写中英文全名） |

视频统一采用上表约定（与 `utils/fft.py`、`np.fft` 一致），画面上的 DFT/FFT 数值一律由 `utils/fft.py` 现算并与 `np.fft` 对照通过。`assets/fft_example.cpp` 采用相反约定（默认 $\mathrm{e}^{+2\pi\mathrm{i}/n}$ 作正变换），其内部自洽、结果等价；代码展示时用浮窗点明，不要改代码也不要混用两套数值。「数学基础」章的单位根几何图沿用现有场景的 `sign=+1`（同一组点、仅编号方向相反），从 DFT 起统一用负号。

## 章节 ↔ 场景文件

| 章节 | 场景文件 | 状态 |
| --- | --- | --- |
| 引入：FT 应用墙 | `scenes/ch00_opening.py` | 待实现 |
| 数学基础（复数运算 / 欧拉公式 / 单位复数根） | `scenes/ch01_complex.py` | 已有四场，按本约定复核 |
| FFT 的动机（多项式表示 / 相乘 / DFT 与 FFT） | `scenes/ch02_motivation.py` | 待实现 |
| 算法：递归分治 | `scenes/ch03_algorithm.py` | 待实现，视频重点 |
| 其他内容（技术 / 人文） | `scenes/ch04_background.py` | 待实现，从简 |
| 代码展示 | `scenes/ch05_closing.py` | 待实现 |

场景类在文件中的排列顺序 = 成片顺序；类定名后回填本表。

## 素材占位符

- 目录沿用 `custom_config.yml`：`assets/raster_images/`（配图、肖像）、`assets/vector_images/`、`assets/data/`。
- 不放假图进仓库：占位符是虚线边框矩形 + 居中文字「素材名 / 待补」，由 `utils/` 里的工厂函数生成（随第一个用到素材的场景一起实现）；素材到位后替换为 `ImageMobject(path)`。场景里不硬写素材路径。
- 命名 `<章节>_<用途>_<序号>.png`（如 `ch00_ft_app_01.png`），肖像 `portrait_<姓>.png`。
- `assets/CREDITS.md` 记每个正式素材的来源 URL、许可与商用状态；public 仓库里许可未确认的素材一律保持占位符、不进 commit。

## 讲解文字（不配音）

- 全片**不做配音**，讲解全部由屏幕文字（`Text` / `Tex`）承载；没有旁白稿，也不做与旁白对应的字幕。
- 文字是唯一的讲解通道：核心定义与推导要停留到能读完，文字出现与画面动作尽量错开，不要同一时刻既动又读。剧本里「快速掠过 / 三秒贴完 / 一带而过」仍按原指示执行 —— 那是刻意的节奏设计（观众可自行暂停），不要把所有文字都拉长。
- 讲解文字在实现场景时按对应章节撰写，不预先写死；全中文，公式保留拉丁/希腊符号；缩写首次出现写中英文全名。
- `utils/mobjects.py` 的 `get_caption()` 是屏幕底部一行讲解文字的占位工厂，沿用即可。

## 其他

- 涉及人名、年份、复杂度数字时按 `AGENTS.md` §7 核查出处，查不到标 `[待核]`。
