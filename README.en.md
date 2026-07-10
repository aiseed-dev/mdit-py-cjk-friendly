# mdit-py-cjk-friendly

[日本語](README.md) | English | [繁體中文](README.zh-TW.md) | [한국어](README.ko.md)

A [markdown-it-py](https://github.com/executablebooks/markdown-it-py) plugin
that makes CommonMark friendly to Japanese, Chinese and Korean text.

```bash
# Until the PyPI release, install from GitHub:
pip install "mdit-py-cjk-friendly @ git+https://github.com/aiseed-dev/mdit-py-cjk-friendly.git"
# After the PyPI release: pip install mdit-py-cjk-friendly
```

```python
from markdown_it import MarkdownIt
from mdit_py_cjk_friendly import cjk_friendly

md = MarkdownIt("commonmark").use(cjk_friendly)

md.render("これは**「重要」**です。")
# <p>これは<strong>「重要」</strong>です。</p>

md.render("これは長い文章なので\n途中で改行しています。")
# <p>これは長い文章なので途中で改行しています。</p>   (no spurious space)
```

## What it fixes

CommonMark was designed around space-separated languages, which breaks CJK
text in two well-known ways:

1. **Soft line breaks become spaces.** A source line break renders as `\n`,
   which browsers collapse into a space — wrong inside a Japanese sentence.
   With this plugin a softbreak between two CJK characters renders as
   nothing; Latin text keeps the normal behaviour.

2. **Emphasis fails next to full-width punctuation.** `**「重要」**です`
   leaves literal asterisks because `「` is Unicode punctuation and breaks
   the left/right-flanking rules. The plugin treats CJK characters as
   punctuation-compatible in the flanking computation (applied at the
   parser level, so code spans and code blocks are naturally unaffected).

The emphasis behaviour follows the ideas of the
[CommonMark CJK-friendly specification draft](https://github.com/tats-u/markdown-cjk-friendly)
(this is an independent, simplified implementation for markdown-it-py;
JavaScript users should use the plugins from that project).

## Notes

- Only parsers that `.use(cjk_friendly)` are affected; other `MarkdownIt`
  instances in the same process keep exact upstream behaviour.
- Works with markdown-it-py 2.x and 3.x.

## Furigana (ruby) — optional

Because this adds syntax, it ships as a separate opt-in plugin `ruby`
(Denden Markdown notation):

```python
from mdit_py_cjk_friendly import cjk_friendly, ruby

md = MarkdownIt("commonmark").use(cjk_friendly).use(ruby)
md.render("{漢字|かんじ}")          # → <ruby>漢字<rp>(</rp><rt>かんじ</rt><rp>)</rp></ruby>
md.render("{東京|とう|きょう}")      # → mono ruby (one reading per character)
```

- No conversion when reading count doesn't match the base length or a part
  is empty (no guessing)
- Escape with `\{`; code spans and code blocks are untouched
- Output includes `<rp>` parentheses, so non-ruby renderers degrade to
  「漢字(かんじ)」

## License

MIT
