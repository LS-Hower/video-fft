# materials.md

参考资料的**出处清单**。这里列的是内容来源与引用依据，**不是运行依赖** ——
manimgl 由 `requirements.txt` 从网络安装，不需要 clone 下列任何仓库，`../reference/` 也不是项目的一部分。

## GitHub 仓库

括号内为核对其内容时所用的 commit：`AGENTS.md` §5 里的行号只在该 commit 下成立。

- `https://github.com/3b1b/manim` · `fafa083a4fb274bba9cabde0b6e2f50ba6da0622`（2026-09-09）· MIT
- `https://github.com/3b1b/videos` · `306a1346a356c7a7b097875ceb51c5cd67d0a56c`（2026-09-29）· **CC BY-NC-SA 4.0**
  （含非商业条款：只借鉴动画思路、在 `utils/` 里重写构件并注明出处，不整段抄进本仓库；本仓库是 public 的）
- `https://github.com/manim-kindergarten/manim_sandbox` · `f7dae90f25389b40f8c28f3eb7b6201170e54c97`（2022-08-02）· MIT

## 其他

- 维基条目：`https://en.wikipedia.org/wiki/Fast_Fourier_transform`。本地留存的是该条目的 wikitext
  （`Fast-Fourier-transform.wiki`）；所有年份、人名、复杂度数字以此为准。
- OpenAI 预印本（2026-09-25）：`https://github.com/openai/math/tree/main/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026`，
  主定理在 `build/sections/introduction.tex`。**预印本、尚待同行评议**；攻的是上界而非下界（见 `script_raw.md` 勘误）。
