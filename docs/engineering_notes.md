# 实现笔记：踩过的坑与验证方法

> `AGENTS.md` §4 已有旧 API 黑名单与类型约束，这里**不重复**，只记实现 14 个场景期间
> 实际踩到、且不看源码不容易猜到的坑。结论对应 `materials.md` 所列固定 commit 的
> manimgl；升级 manim 后需重新验证。

## 渲染档位与验证套路

| 参数 | 输出 | 用途 |
| --- | --- | --- |
| `-l` | 480p | 快速验证、抽帧排错 |
| `-m` | 720p | 中间档 |
| `--hd` | 1080p | 成片（与 `custom_config.yml` 一致） |
| `--uhd` | 4K | 需要时 |

`custom_config.yml` 默认 1920×1080 @ 30fps；`-w` 写 mp4，`-s` 只存末帧，
`-a` 渲染整文件所有场景。离线出末帧必须 `-w -s` 成对使用。

一次验证的固定套路：

```bash
python -m py_compile scenes/chXX.py utils/*.py
python -m manimlib scenes/chXX.py SceneName -l -w -s     # 末帧看构图
python -m manimlib scenes/chXX.py -a -l -w               # 整章低清
ffmpeg -v error -ss 12.0 -i videos/SceneName.mp4 -frames:v 1 -y videos/frame.png
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 videos/SceneName.mp4
```

改完先 `py_compile`，再末帧，再全片；抽出的帧要目检文字有没有被压、出没出画。

## 抽帧判断的陷阱

**动画中途帧会被误判成排版 bug**。`Write` / `FadeIn` / `LaggedStart` 进行中抽到的帧，
公式可能只写出一半、文字只滑入一半；曾据此以为 `to_corner(UR, buff=0.45)` 会裁切公式，
实际定位完全正常（静止帧里公式齐全、未越界）。

判断布局问题要抽**动画结束后的静止帧**（各场景末尾都有 `self.wait(...)`），
或直接用 `-w -s` 的末帧。目测不准时用像素分析量包围盒，比放大截图可靠。

## 拼接

```bash
# concat 清单放在 videos/ 里；file 路径相对清单文件所在目录，不要写成 videos/xxx.mp4
{ for n in FTApplications ProductAsRotation ...; do echo "file '$n.mp4'"; done; } > videos/concat.txt
ffmpeg -v error -f concat -safe 0 -i videos/concat.txt -c copy -y videos/fft_full_hd.mp4
```

`-c copy` 要求各段**同分辨率、同帧率**，混档位会失败或显示异常。逐段 `ffprobe`
核对过再拼，比拼完再排查省事。顺序以 `scripts/production_notes.md` 的章节 ↔ 场景表为准。

## 文字渲染（三个不同的坑）

1. **`Text` / `MarkupText` 不支持 `\n`**：含换行的字符串会逐字符竖排
   （实测 `Text('a\nb\nc\nd')` 宽度只有 0.057，高度却是 4 行）。因此 manimgl 的
   `Code` 组件（基于 `MarkupText`）也不能用。多行文本必须逐行建 `Text` 再
   `arrange(DOWN, aligned_edge=LEFT, buff=...)`，见 `scenes/ch05_closing.py`。
2. **`Tex` 不解析中文**：含中文的标签一律用 `Text`。时间线最后一个节点写「今天」时，
   用 `Tex` 渲染出了错误的年份数字。
3. **`Text` 不解析 LaTeX**：讲解文案里不要写 `e^{iθ}`、`ω^{k}` 之类 TeX 语法，
   会原样显示成一串字符。公式交给 `Tex`，中文讲解用自然语言描述。

## 颜色、缩放与定位

- `Dot(..., color=...)` 不生效（点会是白色）；用 `fill_color=...`，通常配
  `stroke_width=0`，见 `scenes/ch02_motivation.py`。
- `VGroup` 整体 `scale()` 以**组包围盒中心**缩放。要放大一对对径点，在各自原位
  重建大点，否则两点会被沿半径推到圆外。
- `to_edge(UP)` 只改纵坐标，水平方向要显式 `move_to` / `set_x` 才居中。
- 讲解文字压在网格或代码上时，用 `BackgroundRectangle` 加半透明底衬
  （`NarrationBoard` 已这么做）；不配音时文字是唯一讲解通道，可读性优先。
- 折半 / 求和这类阶段切换时，把不再对应的标签、点、辐条一起 `FadeOut`，
  否则会悬空，语义上误导成「还有 8 个根」。

## 内容侧的两条硬约束

- 应用卡片只写领域名，不写「某某使用 FFT」：JPEG 类编码走 DCT。
- butterfly 图里蓝色是 E 的两条贡献（权重 1），绿色是 O 的两条
  （`+ω^k` / `−ω^k`）。曾把 `−ω^k` 标到 E 出发的无权边上，是语义错误。

## 数值

`utils/fft.py` 的画面数值一律现算并与 `np.fft` 对照。实现期修过三个 bug，
改回来会静默出错：迭代 FFT 的 `even` / `odd` 是视图别名（必须 `.copy()`）、
`bit_reverse_indices` 用 `.ravel()` 会炸矩阵形状、`fft_convolve` 用 `np.resize`
会循环填充（要零填充）。`python utils/fft.py` 是自检入口。
