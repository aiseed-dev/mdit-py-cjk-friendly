"""markdown-it-py plugin: make CommonMark friendly to Japanese/Chinese/Korean.

Fixes the two classic CJK problems (reference:
https://github.com/tats-u/markdown-cjk-friendly — the CommonMark
"CJK-friendly" specification draft; this is an independent, simplified
implementation of the same ideas for markdown-it-py):

1. **Soft line breaks** — CommonMark renders a source line break as "\\n",
   which browsers collapse into a space. Between two CJK characters that
   space is wrong ("これは\\n続き" must join without a space). The plugin
   renders such softbreaks as nothing.

2. **Emphasis flanking** — ``**「重要」**です`` fails to parse because the
   full-width bracket is Unicode punctuation and breaks CommonMark's
   left/right-flanking rules. The plugin treats CJK characters as
   punctuation-compatible in the flanking computation, so emphasis
   adjacent to CJK text (including full-width punctuation) works.

Usage::

    from markdown_it import MarkdownIt
    from mdit_py_cjk_friendly import cjk_friendly

    md = MarkdownIt("commonmark").use(cjk_friendly)
    md.render("これは**「重要」**です。")   # -> <strong>「重要」</strong>
"""

from __future__ import annotations

import re

from markdown_it import MarkdownIt
from markdown_it.rules_inline.state_inline import StateInline

__version__ = "0.1.0"
__all__ = ["cjk_friendly", "is_cjk", "__version__"]

# CJK: ideographs, kana, CJK symbols/punctuation, full/half-width forms.
_CJK_RE = re.compile(
    "[　-〿"      # CJK symbols & punctuation (、。「」…)
    "぀-ヿ"       # hiragana, katakana
    "㐀-䶿一-鿿豈-﫿"  # ideographs
    "＀-｠￠-￦"               # full-width forms
    "\U00020000-\U0002a6df"                    # ideographs ext. B
    "]"
)


def is_cjk(char: str) -> bool:
    """True if *char* (a 1-character string) is a CJK character."""
    return bool(char) and bool(_CJK_RE.match(char))


# ---------------------------------------------------------------------------
# 2. emphasis: patch StateInline.scanDelims once, gated per-parser by a flag
#    set in the plugin (parsers without the plugin keep exact upstream
#    behaviour via the saved original).
# ---------------------------------------------------------------------------

_orig_scan_delims = StateInline.scanDelims


def _scan_delims_cjk(self: StateInline, start: int, canSplitWord: bool):
    scanned = _orig_scan_delims(self, start, canSplitWord)
    if not getattr(self.md, "_cjk_friendly", False):
        return scanned
    if scanned.can_open and scanned.can_close:
        return scanned

    pos = start
    maximum = self.posMax
    marker = self.src[start]
    while pos < maximum and self.src[pos] == marker:
        pos += 1
    last_char = self.src[start - 1] if start > 0 else " "
    next_char = self.src[pos] if pos < maximum else " "
    if not (is_cjk(last_char) or is_cjk(next_char)):
        return scanned

    # Re-run the flanking computation treating CJK characters (letters and
    # full-width punctuation alike) as punctuation. This makes a delimiter
    # adjacent to CJK text usable as both opener and closer, which is the
    # practical effect of the CJK-friendly specification draft.
    from markdown_it.common.utils import isMdAsciiPunct, isPunctChar, isWhiteSpace

    is_last_punct = is_cjk(last_char) or isMdAsciiPunct(ord(last_char)) or isPunctChar(last_char)
    is_next_punct = is_cjk(next_char) or isMdAsciiPunct(ord(next_char)) or isPunctChar(next_char)
    is_last_ws = isWhiteSpace(ord(last_char))
    is_next_ws = isWhiteSpace(ord(next_char))

    left_flanking = not (is_next_ws or (is_next_punct and not (is_last_ws or is_last_punct)))
    right_flanking = not (is_last_ws or (is_last_punct and not (is_next_ws or is_next_punct)))

    if not canSplitWord:
        can_open = left_flanking and ((not right_flanking) or is_last_punct)
        can_close = right_flanking and ((not left_flanking) or is_next_punct)
    else:
        can_open = left_flanking
        can_close = right_flanking

    return type(scanned)(can_open, can_close, scanned.length)


StateInline.scanDelims = _scan_delims_cjk  # type: ignore[method-assign]


# ---------------------------------------------------------------------------
# 1. softbreak renderer: join CJK—CJK line breaks without a space.
# ---------------------------------------------------------------------------

def _softbreak(renderer, tokens, idx, options, env) -> str:
    prev_char = tokens[idx - 1].content[-1:] if idx > 0 else ""
    next_char = tokens[idx + 1].content[:1] if idx + 1 < len(tokens) else ""
    if is_cjk(prev_char) and is_cjk(next_char):
        return ""
    return "<br>\n" if options.breaks else "\n"


def cjk_friendly(md: MarkdownIt) -> None:
    """markdown-it-py plugin: ``MarkdownIt().use(cjk_friendly)``."""
    md._cjk_friendly = True  # type: ignore[attr-defined]
    md.add_render_rule("softbreak", _softbreak)
