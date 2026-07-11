# mdit-py-cjk-friendly

[日本語](README.md) | English | [繁體中文](README.zh-TW.md) | [한국어](README.ko.md)

A [markdown-it-py](https://github.com/executablebooks/markdown-it-py) plugin
that makes CommonMark friendly to Japanese, Chinese and Korean text.

```bash
pip install mdit-py-cjk-friendly
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

## Emphasis dots / lines (bouten) — optional

Denden Markdown has no dedicated notation for emphasis dots; it only renders
`*text*` → `<em>` and styles it as sesame dots in vertical writing mode
(which cannot distinguish the different mark styles). To write emphasis dots
and lines with an explicit style, the `bouten` plugin adds a Pandoc-style
class span as a separate opt-in:

```python
from mdit_py_cjk_friendly import cjk_friendly, bouten

md = MarkdownIt("commonmark").use(cjk_friendly).use(bouten)
md.render("[邪智暴虐]{.sesame_dot}")      # → <em class="sesame_dot">邪智暴虐</em>
md.render("[あ]{.underline_double}")      # → <em class="underline_double">あ</em>
```

- Passes a single class name through to `<em class>`; appearance (which class
  is sesame dots, double underline, etc.) is defined by CSS
- Does nothing unless `]` is immediately followed by `{.class}`, so links
  `[x](y)` and bare `[x]` are left intact. Inner text is literal (no guessing)
- `*`/`**` (emphasis/strong) are left to plain Markdown
- Example class names for Aozora Bunko styles: dots `sesame_dot` /
  `white_sesame_dot` / `black_circle` / `white_circle` / `bullseye` /
  `fisheye` / `saltire` / `black_up-pointing_triangle` /
  `white_up-pointing_triangle`; lines `underline_solid` / `underline_double` /
  `underline_dotted` / `underline_dashed` / `underline_wave` (`overline_*` for
  the opposite side)

## License

MIT
