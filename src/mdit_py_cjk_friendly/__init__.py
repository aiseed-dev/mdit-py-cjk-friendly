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

__version__ = "0.3.0"
__all__ = ["cjk_friendly", "ruby", "bouten", "is_cjk", "__version__"]

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

    # Re-run the flanking computation with the CJK-friendly rule
    # (tats-u の仕様ドラフトの本質): CJK 文字は
    #   - 「約物が隣にあると成立しやすくなる」判定 (allow 側) では約物として扱い、
    #   - 「約物が隣にあると不成立になる」判定 (block 側) では約物として扱わない。
    # これにより a**あ、**b (内側が和文約物・外側が英数字) も成立し、
    # CJK が絡まないケースは代数的に素の CommonMark と一致する。
    from markdown_it.common.utils import isMdAsciiPunct, isPunctChar, isWhiteSpace

    def _punct(ch):
        return isMdAsciiPunct(ord(ch)) or isPunctChar(ch)

    last_block = (not is_cjk(last_char)) and _punct(last_char)
    next_block = (not is_cjk(next_char)) and _punct(next_char)
    last_allow = is_cjk(last_char) or _punct(last_char)
    next_allow = is_cjk(next_char) or _punct(next_char)
    is_last_ws = isWhiteSpace(ord(last_char))
    is_next_ws = isWhiteSpace(ord(next_char))

    left_flanking = (not is_next_ws
                     and (not next_block or is_last_ws or last_allow))
    right_flanking = (not is_last_ws
                      and (not last_block or is_next_ws or next_allow))

    if not canSplitWord:
        can_open = left_flanking and ((not right_flanking) or last_allow)
        can_close = right_flanking and ((not left_flanking) or next_allow)
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


# ---------------------------------------------------------------------------
# 3. ruby (opt-in): ふりがな。でんでんマークダウン形式 {漢字|かんじ}
#    cjk_friendly とは独立の追加構文なので、別プラグインとして明示的に
#    ``md.use(ruby)`` したときだけ有効になる。
# ---------------------------------------------------------------------------

from markdown_it.common.utils import escapeHtml  # noqa: E402


def _ruby_rule(state: StateInline, silent: bool) -> bool:
    src = state.src
    pos = state.pos
    if src[pos] != "{":
        return False
    end = src.find("}", pos + 1)
    if end < 0:
        return False
    inner = src[pos + 1 : end]
    if "|" not in inner or "\n" in inner:
        return False
    base, *readings = inner.split("|")
    if not base or not all(readings):
        return False
    if len(readings) > 1 and len(readings) != len(base):
        return False  # モノルビは読みの数=文字数のときだけ。推測しない
    if not silent:
        pairs = (
            list(zip(base, readings)) if len(readings) > 1 else [(base, readings[0])]
        )
        token = state.push("html_inline", "", 0)
        token.content = (
            "<ruby>"
            + "".join(
                f"{escapeHtml(b)}<rp>(</rp><rt>{escapeHtml(r)}</rt><rp>)</rp>"
                for b, r in pairs
            )
            + "</ruby>"
        )
    state.pos = end + 1
    return True


def ruby(md: MarkdownIt) -> None:
    """markdown-it-py plugin (opt-in): でんでん形式のふりがな。

    ``MarkdownIt().use(ruby)`` で有効になる:

    - ``{漢字|かんじ}``      → グループルビ
    - ``{東京|とう|きょう}``  → モノルビ (読みの数=文字数のとき)
    - 読みの数が合わない・空の要素がある場合は変換しない (推測しない)
    - ``\\{`` でエスケープ。コードスパン内は変換されない

    出力は ``<ruby>漢字<rp>(</rp><rt>かんじ</rt><rp>)</rp></ruby>``
    (ルビ非対応環境では「漢字(かんじ)」に落ちる)。
    """
    md.inline.ruler.after("escape", "cjk_ruby", _ruby_rule)


# ---------------------------------------------------------------------------
# 4. bouten (opt-in): 傍点・傍線 (text-emphasis)。Pandoc 風のクラス付きスパン
#    ``[テキスト]{.sesame_dot}`` → ``<em class="sesame_dot">テキスト</em>``。
#
#    でんでんマークダウンには圏点専用の記法が無く、``*text*`` を縦書き時のみ
#    圏点表示する仕様しか持たない (種別を区別できない)。青空文庫の注記は
#    傍点9種・傍線5種を書き分けるため、種別をクラス名として無損失に運べる
#    Pandoc 風スパンを採用する。プラグイン側は種別を解釈せずクラスを
#    ``<em class>`` に透過するだけなので、対応表 (どのクラスがどんな圏点か)
#    は CSS 側 (washi-md / aozorabunko) が持つ。
#
#    ``*``/``**`` (強調・太字) は素の Markdown で足りるので対象外。この
#    プラグインは text-emphasis 系 (=``<em class>``) だけを引き受ける。
# ---------------------------------------------------------------------------

# クラス名は 1 個・英字始まり (``[A-Za-z_][\w-]*``)。``]`` の直後に ``{.``。
_BOUTEN_ATTR_RE = re.compile(r"\{\.([A-Za-z_][\w-]*)\}")


def _bouten_rule(state: StateInline, silent: bool) -> bool:
    src = state.src
    pos = state.pos
    if src[pos] != "[":
        return False
    end = src.find("]", pos + 1)
    if end < 0 or end == pos + 1:      # ``]`` が無い / ``[]`` は対象外
        return False
    inner = src[pos + 1 : end]
    if "\n" in inner or "[" in inner or "]" in inner:
        return False                    # 改行・入れ子は扱わない (推測しない)
    m = _BOUTEN_ATTR_RE.match(src, end + 1)
    if not m:
        return False                    # ``]{.class}`` でなければ素通り (リンク等)
    cls = m.group(1)
    if not silent:
        token = state.push("html_inline", "", 0)
        token.content = f'<em class="{escapeHtml(cls)}">{escapeHtml(inner)}</em>'
    state.pos = m.end()
    return True


def bouten(md: MarkdownIt) -> None:
    """markdown-it-py plugin (opt-in): 傍点・傍線 (text-emphasis)。

    ``MarkdownIt().use(bouten)`` で有効になる Pandoc 風のクラス付きスパン:

    - ``[テキスト]{.sesame_dot}``      → ``<em class="sesame_dot">テキスト</em>``
    - ``[あ]{.underline_double}``      → ``<em class="underline_double">あ</em>``

    クラス名 1 個 (英字始まり) のみを受け付け、``<em class>`` に透過する。
    見た目 (どのクラスがゴマ点・二重傍線か等) は CSS が定める。青空文庫の
    種別に対応するクラス名の例:

    - 傍点: ``sesame_dot`` / ``white_sesame_dot`` / ``black_circle`` /
      ``white_circle`` / ``black_up-pointing_triangle`` /
      ``white_up-pointing_triangle`` / ``bullseye`` / ``fisheye`` / ``saltire``
    - 傍線: ``underline_solid`` / ``underline_double`` / ``underline_dotted`` /
      ``underline_dashed`` / ``underline_wave`` (上側は ``overline_*``)

    ``]`` の直後が ``{.class}`` でなければ何もしない (リンク ``[x](y)`` や
    素の ``[x]`` を壊さない)。inner はプレーンテキスト扱い (ruby と同じ方針で
    推測しない)。``*``/``**`` (強調・太字) は素の Markdown に任せる。
    """
    md.inline.ruler.before("link", "cjk_bouten", _bouten_rule)
