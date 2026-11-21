# 素材来源与许可

当前仓库**不含第三方图像素材**：应用墙卡片、人物肖像都是 `utils/mobjects.py`
的 `get_placeholder()` 生成的占位符（虚线框 + 待补文字）。

素材到位后逐条登记，约定见 `scripts/production_notes.md`：

| 文件（`assets/` 下） | 来源 URL | 许可 | 可商用 | 备注 |
| --- | --- | --- | --- | --- |
| _（待补）_ | | | | |

规则：

- 许可未确认的素材一律保持占位符，不进 commit。
- 官方文档、维基共享资源的图优先；标明作者与许可版本。
- 替换时把场景里的 `get_placeholder(...)` 换成 `ImageMobject(path)`，位置与动画不用改。

## 参考代码

- `3b1b/manim`、`3b1b/videos`：CC BY-NC-SA 4.0，只借鉴思路，代码为本仓库重写。
- `assets/fft_example.cpp`：本仓库自备示例，无第三方来源。
