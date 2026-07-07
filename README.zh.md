# mdit-py-cjk-friendly

[日本語](README.md) | [English](README.en.md) | 简体中文 | [한국어](README.ko.md)

让 [markdown-it-py](https://github.com/executablebooks/markdown-it-py)
对中文、日文、韩文 (CJK) 文本友好的插件。

```bash
# PyPI 发布前，从 GitHub 安装:
pip install "mdit-py-cjk-friendly @ git+https://github.com/aiseed-dev/mdit-py-cjk-friendly.git"
# PyPI 发布后: pip install mdit-py-cjk-friendly
```

```python
from markdown_it import MarkdownIt
from mdit_py_cjk_friendly import cjk_friendly

md = MarkdownIt("commonmark").use(cjk_friendly)

md.render("这是**「重点」**内容。")
# <p>这是<strong>「重点」</strong>内容。</p>

md.render("这是一个较长的句子\n中间换了一行。")
# <p>这是一个较长的句子中间换了一行。</p>   (不会插入多余的空格)
```

## 解决的问题

CommonMark 以空格分隔单词的语言为前提设计，对 CJK 文本有两个众所周知的问题:

1. **软换行变成空格。** 源文件中的换行渲染为 `\n`，浏览器会将其折叠为一个
   空格——在中文句子中这是错误的。使用本插件后，两个 CJK 字符之间的软换行
   不输出任何内容；拉丁文本保持原有行为。
2. **全角标点旁的强调失效。** `**「重点」**内容` 会留下字面的星号，因为
   `「` 属于 Unicode 标点，破坏了 left/right-flanking 规则。本插件在
   flanking 判定中将 CJK 字符视为与标点兼容 (在解析器层面处理，
   代码段与代码块自然不受影响)。

强调行为遵循 [CommonMark CJK-friendly 规范草案](https://github.com/tats-u/markdown-cjk-friendly)
的思路 (本项目是面向 markdown-it-py 的独立简化实现；
JavaScript 用户请使用该项目的插件)。

## 说明

- 只影响调用了 `.use(cjk_friendly)` 的解析器；同一进程中的其他
  `MarkdownIt` 实例保持与上游完全一致的行为。
- 支持 markdown-it-py 2.x 与 3.x。

## 许可证

MIT
