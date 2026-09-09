# 素材包与布局契约

布局文件是数值事实来源。目录中保留 `layout.json`、`assets/` 原始素材；构建生成 `composition.svg`、`import-photoshop.jsx`、`open-illustrator.jsx`、`使用说明.txt`。另需渲染 `preview.png`，如有实机条件再保存 PSD/AI。原生 Adobe 保存不可由改扩展名替代。

## 最小例子

```json
{
  "version": 1,
  "canvas": {"width": 1920, "height": 1080},
  "items": [
    {"id": "background", "kind": "raster", "file": "assets/background.png", "x": 0, "y": 0, "width": 1920, "height": 1080},
    {"id": "star", "kind": "vector", "file": "assets/star.svg", "ps_file": "assets/star.png", "x": 300, "y": 160, "width": 100, "height": 100},
    {"id": "title", "kind": "text", "text": "星之卡", "x": 100, "y": 100, "font_size": 48, "font_family": "Microsoft YaHei", "ps_font": "MicrosoftYaHei", "color": "#FFFFFF"}
  ]
}
```

- UTF-8，单位 px；原点画布左上，x 向右、y 向下；items 从底到顶。画布按 72 ppi 导入 PS，保持脚本中 px 与文字 pt 数值对应，屏幕像素数不变。
- raster/vector 的 x/y 为目标框左上，width/height 为完整素材框尺寸；素材需事先裁齐。提供 `allow_distort: true` 才允许改变原始长宽比，正常情况下误差超过 0.1% 即拒绝。
- text 的 x/y 是**左侧基线原点**，不是字形左上。只支持单行、左对齐、实色。字体家族用于 SVG，PostScript 字体名用于 PS；必须确认字体安装，禁止静默替换后宣称一致。
- raster 只支持非动画 PNG，透明可选；vector 必须 SVG、viewBox 起点为 0,0，有明确正数宽高。为 PS 同时提供同长宽比的 PNG `ps_file`。PNG 不因此成为矢量，PS 只保证该图案作为独立智能对象整体编辑。
- SVG 使用独立路径/形状/组/文字。构建器拒绝脚本、外链、图片、滤镜、CSS style 和事件属性；纯矢量素材的颜色等用 presentation attributes。路径渐变和 clipPath 可以使用本地 #id 引用。带命名空间前缀的 id 会被安全重写。
- 不支持自动旋转、透明度设置、自动换行、变形与跨对象蒙版，额外字段会被拒绝。先把这些落实在独立素材中，或编写经过验证的专用扩展。
- 尺寸可小数，但光栅显示存在抗锯齿；用最终展示比例验看细线。用户要屏幕锐利时可建议像素对齐，不擅改硬性数值。

## 运行

`python <本技能目录>/scripts/build_pack.py <素材包目录>`

仅用 Python 标准库；不生成插画、不自动抠图、不自动安装字体或软件。所有输出在写入前检查存在冲突，已有交付文件时拒绝覆盖。迭代时复制到新版本目录后再构建，或经用户明确同意处理旧输出。

Illustrator 脚本在新文档打开 composition.svg；组保留 id，位图以内嵌图像导入，文字和矢量编辑程度需在实际软件中检查。PS 脚本新建文档，导入 PNG、转智能对象并按可见图层边界设置位置大小，逐项核对数值；不会覆盖或保存现有文档。两者完成后用户另存为 PSD/AI。
