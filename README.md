# Design Asset Pack

**Editable design assets, precise layouts, and honest quality checks for Photoshop & Illustrator.**

**从参考图或文字要求出发，交付独立素材、精确布局与可继续编辑的设计文件。**

[中文](#中文) · [English](#english)

## 中文

### 这是什么？

一个面向 Codex 的设计素材包技能。适合“背景＋几个独立图案”的平面设计、卡面、装饰、图标和插画配套素材。

它指导智能体先理解要求、补问必要信息，再分别制作素材，保存布局参数，检查透明边缘并打包交付。你可以在 Photoshop 或 Illustrator 中继续调整，而不必反复修改一张已经合成的图片。

**这是工作流技能和辅助脚本，不是独立生图模型，也不是 Adobe MCP。** 图像生成需要宿主提供相应工具；脚本本身不会画插画或自动修复抠图。

### 能做什么

- 区分参考图忠实提取、参考风格重绘和纯文字创作。
- 背景、主体、装饰和文字分别交付；简单图案优先真实 SVG 路径。
- 记录像素位置、宽高与长宽比，拒绝意外拉伸和未知布局字段。
- 导出组合 SVG、Photoshop 导入脚本与 Illustrator 打开脚本。
- 检查字母内孔、黑白残边、毛刺和杂点：白／黑／品红底、Alpha 图和局部放大。
- 区分“存在透明通道”和“抠图已验收”；未实测的 Adobe 兼容性必须说明。

### 安装到 Codex

把整个仓库克隆到 Codex 的 skills 目录，文件夹名保持 `design-asset-pack`。

**Windows PowerShell：**

```powershell
$skillBase = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex/skills' }
git clone https://github.com/misakayyds/design-asset-pack.git (Join-Path $skillBase 'design-asset-pack')
```

**macOS / Linux：**

```sh
git clone https://github.com/misakayyds/design-asset-pack.git "${CODEX_HOME:-$HOME/.codex}/skills/design-asset-pack"
```

若该文件夹已存在，先保留你的本地修改，不要直接覆盖。新开一个 Codex 任务，使用 `$design-asset-pack` 调用。其他支持 `SKILL.md` 的宿主可以适配使用，但没有在这里实测。

### 如何调用

附上参考图，输入：

> 用 $design-asset-pack 按这张图制作独立素材包，供 Photoshop 和 Illustrator 编辑。保持比例和配色，背景、图案与文字分开；遗漏的重要设计信息先问我。

或：

> 用 $design-asset-pack 做一套星空卡面素材，1920×1080。边框和星星用矢量，插画单独输出透明 PNG；检查内孔、毛刺和黑边。

### 脚本与示例

需要 Python 3.10+。打包脚本只用标准库；透明诊断和测试需要 Pillow：

```sh
python -m pip install -r requirements.txt
python examples/create_demo.py work/demo
python scripts/build_pack.py work/demo
python scripts/audit_alpha.py work/demo/assets work/demo-review
python -m unittest discover -s tests -v
```

示例是代码绘制的简单几何素材，不调用模型、不需要 API 凭证。示例脚本拒绝覆盖已有目录。

典型交付：

```text
pack/
├── assets/                 # 独立 PNG 与 SVG
├── layout.json             # 尺寸、位置、图层顺序
├── composition.svg         # 组合稿，供 Illustrator 打开
├── import-photoshop.jsx     # 在新文档中导入图层
├── open-illustrator.jsx     # 打开组合 SVG
└── 使用说明.txt
```

技能还要求另行渲染并检查 `preview.png`；打包器不自动生成此文件。`audit_alpha.py` 输出诊断图和统计，**不会修改素材，也不会自动宣布抠图通过**。

Photoshop 中通过“文件 → 脚本 → 浏览”运行 JSX。Illustrator 可以直接打开组合 SVG。检查结果后自行另存为 PSD／AI；脚本不会自动保存或覆盖现有文档。

### 编辑能力与限制

| 内容 | Photoshop | Illustrator |
|---|---|---|
| PNG 插画与背景 | 独立智能对象，整体移动缩放 | 内嵌位图，整体移动缩放 |
| SVG 图案 | 使用配套 PNG 导入智能对象 | 按 SVG 结构编辑路径／分组 |
| 文字 | 独立文字层，需要正确字体 | SVG 文字，需要正确字体 |

PNG 放进 SVG 仍然是位图。PS 导入器不把 SVG 转成原生形状层。复杂 SVG 滤镜、自动换行、旋转与跨对象蒙版不在通用打包器支持范围；详见 [布局契约](references/delivery.md)。

Photoshop 以 72 ppi 创建屏幕用文档，保持像素数和文字单位对应。图案根据可见边界定位，因此应提前处理透明留白。几何读回检查允许 1 px 光栅误差，不能据此承诺亚像素级跨软件一致。

**验证状态：** 已有布局构建测试和透明诊断运行验证；Adobe JSX 做过语法检查，尚未完成 Photoshop／Illustrator 实机导入验证。字体、色彩与 SVG 渲染差异仍需实际检查。技能主体目前使用中文，README 提供中英双语。

### 工作流文件

- [SKILL.md](SKILL.md)：入口与交付流程。
- [透明边缘验收](references/alpha-quality.md)：内孔、色边、毛刺与检查顺序。
- [布局契约](references/delivery.md)：支持的字段与尺寸约定。
- [参考来源](references/sources.md)：借鉴项目与适配边界。

## English

### What is this?

A Codex skill for creating reusable design asset packs from a reference image or a written brief. It fits card layouts, decorations, icons, illustration assets, and designs made of a background plus independently positioned elements.

The workflow separates assets, records geometry, asks about material missing requirements, and checks transparent edges before delivery. You can continue editing individual elements in Photoshop or Illustrator.

**This is a workflow skill with helper scripts, not an image model or an Adobe MCP server.** Raster generation requires tools supplied by the host. The scripts do not generate illustrations or automatically repair cutouts.

### Features

- Separate faithful extraction, reference-inspired recreation, and original design.
- Deliver backgrounds, artwork, decorations, and text independently.
- Use real SVG geometry for suitable shapes; retain raster artwork where appropriate.
- Record pixel coordinates and dimensions, and reject unintended aspect-ratio changes.
- Build a composed SVG and Adobe JSX import/open helpers.
- Review cutout holes, halos, jagged edges, and specks on white, black, magenta, and alpha-only views.
- Keep numerical validation separate from visual approval and Adobe application testing.

### Install

Clone the **whole repository** into the Codex skills directory as `design-asset-pack`. Use the Windows or macOS/Linux commands in the installation section above; they respect `CODEX_HOME` when configured. Preserve any existing local installation before changing it.

Start a new Codex task and invoke:

> Use $design-asset-pack to create a reusable asset pack from this reference for Photoshop and Illustrator. Preserve proportions and colors. Separate the background, artwork, and text, and ask about important missing design requirements.

The skill instructions are currently written in Chinese. Adapting them to other `SKILL.md` hosts is possible but has not been tested here.

### Run the helpers

Python 3.10+ is required. `build_pack.py` uses the standard library; diagnostics, the demo, and tests require Pillow.

```sh
python -m pip install -r requirements.txt
python examples/create_demo.py work/demo
python scripts/build_pack.py work/demo
python scripts/audit_alpha.py work/demo/assets work/demo-review
python -m unittest discover -s tests -v
```

The demo uses simple original geometry and does not call an image service. Both output helpers refuse to overwrite their existing outputs. Keep generated files outside the installed skill's source tree when working on actual designs.

The pack contains independent assets, `layout.json`, `composition.svg`, `import-photoshop.jsx`, `open-illustrator.jsx`, and usage notes. A rendered `preview.png` is a separate workflow requirement, not an automatic builder output. Alpha diagnostics are review artifacts, not repaired assets or automatic approval.

### Adobe editing and limits

- **Photoshop:** PNG assets become separate smart objects; text becomes text layers. Vector assets require PNG companions and do not become native Photoshop vector shape layers.
- **Illustrator:** open the composed SVG to work with its paths, groups, text, and embedded raster images. A PNG inside an SVG is still a raster image.
- Imports create/open new documents without automatically saving PSD/AI files. Inspect the result, then save a new native file.
- The general builder supports a deliberately narrow layout schema: no automatic wrapping, rotation, or cross-object masks. See [the schema](references/delivery.md).
- Photoshop documents use 72 ppi for pixel/point correspondence. Trim unintended transparent padding before import. Geometry readback allows 1 px of raster tolerance; this is not a subpixel fidelity guarantee.

**Validation status:** layout tests and alpha diagnostics have been run; JSX syntax has been checked. Actual Photoshop/Illustrator imports have **not** been validated. Check fonts, colors, transparency, and SVG rendering in the target application before treating an asset pack as final.

### Contributing

Include a minimal synthetic example, expected behavior, and the relevant test result. Adobe compatibility reports should include the application version and actual import/export evidence. Do not submit private artwork or credentials. Run the unittest command above before proposing code changes.

### Acknowledgments

Workflow ideas were informed by `claude-illustrate-skill`, `ai-graphic-design-skill`, `prompt-to-asset`, and Illustrator scripting references. This implementation was independently authored; it does not vendor or require those projects. Links and boundaries are recorded in [sources.md](references/sources.md).

### License / 许可

MIT, see [LICENSE](LICENSE). The license applies to this repository's code, skill text, and original demo. User-supplied artwork, third-party logos, fonts, and generated assets remain subject to their own applicable rights and terms.
