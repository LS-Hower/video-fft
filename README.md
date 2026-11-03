# video-fft

对快速傅里叶变换算法的讲解视频。用 3b1b 版 Manim（manimgl）写场景代码并渲染成片。

**仅支持 Windows**（协作双方均使用 Windows）：字体常量、venv 激活脚本、路径分隔符、ffmpeg 与 LaTeX 安装方式都按 Windows 约定，不做跨平台适配。

## 上手

需要 Python 3.13、ffmpeg、git（依赖从 GitHub 拉取）、一套 LaTeX 发行版（本机用 TeX Live 2026，备选 MiKTeX）。

```bash
python -m venv .venv
source .venv/Scripts/activate      # cmd/PowerShell：.venv\Scripts\activate
pip install -r requirements.txt
python -m manimlib --version      # ManimGL v1.7.2
```

依赖全部从网络安装，**不需要**本机存在 `reference/` 目录。

## 项目约定

- 开发约定（命令、代码规范、事实核查、许可）：[`AGENTS.md`](AGENTS.md)
- 内容唯一事实源：[`script.md`](script.md)；原始草稿：[`script_raw.md`](script_raw.md)
- 参考资料出处、固定 commit 与许可：[`materials.md`](materials.md)

渲染产物落在 `videos/`，不进 commit。
