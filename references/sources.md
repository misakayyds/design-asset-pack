# 参考来源

本技能独立编写，借鉴以下项目的工作流思路，未复制上游实现，不自动安装上游依赖。核对日期：2026-09-08。

- https://github.com/code-katz/claude-illustrate-skill ：按素材类型选择矢量／位图路线，成套检查、真实尺寸预览。原项目面向 Claude Code、macOS/Linux；这里采用 Python 标准库与跨软件文件交付。
- https://github.com/designrique/ai-graphic-design-skill ：需求梳理、风格一致性与交付流程。
- https://github.com/MohamedAbdallah-14/prompt-to-asset ：素材打包与尺寸、透明度检查思路。这里不依赖其云端路由或费用假设。
- https://github.com/ie3jp/illustrator-mcp-server ：可选的 Illustrator 自动化参考；其 Windows 支持未实机验证，不是本技能依赖。
- https://ai-scripting.docsforadobe.dev/ ：Illustrator 脚本接口参考。

没有 Adobe 实机读回结果前，不承诺某个版本的复杂 SVG、字体、蒙版或导入脚本完全兼容。普通 SVG 几何、路径与文字优先；复杂 SVG 滤镜需另行核验。
