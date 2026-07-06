"""CJK-friendly プラグインのテスト (softbreak / 強調 / 非干渉)。"""
import pytest
from markdown_it import MarkdownIt
from mdit_py_cjk_friendly import cjk_friendly, is_cjk


@pytest.fixture
def md():
    return MarkdownIt("commonmark").use(cjk_friendly)


def test_softbreak_joins_cjk(md):
    assert md.render("これは長い文章なので\n途中で改行しています。") == \
        "<p>これは長い文章なので途中で改行しています。</p>\n"


def test_softbreak_keeps_newline_for_latin(md):
    assert "text\nwith" in md.render("English **bold** text\nwith wrap.")


def test_softbreak_mixed_boundary_keeps_newline(md):
    # 片側が英数字なら改行(=空白)を残す
    assert "ABC\nこれ" in md.render("ABC\nこれは日本語。")


def test_emphasis_adjacent_fullwidth_bracket(md):
    assert md.render("これは**「重要」**です。") == \
        "<p>これは<strong>「重要」</strong>です。</p>\n"


def test_emphasis_plain_cjk(md):
    assert "<strong>太字</strong>" in md.render("**太字**のテスト。")


def test_emphasis_em_adjacent_cjk_punct(md):
    assert "<em>強調</em>" in md.render("「*強調*」と書く。")


def test_latin_emphasis_unchanged(md):
    assert "<strong>bold</strong>" in md.render("a **bold** word")


def test_intraword_asterisks_not_emphasis(md):
    assert "2**3" in md.render("数式 2**3 は8。")


def test_code_spans_untouched(md):
    assert "<code>**そのまま**</code>" in md.render("コード内は `**そのまま**` です。")


def test_code_blocks_untouched(md):
    out = md.render("```\n**コードブロック**\nこれは\n続き\n```")
    assert "**コードブロック**" in out and "これは\n続き" in out


def test_plain_parser_unaffected():
    # プラグインを使わないパーサは従来挙動のまま (グローバルパッチのゲート確認)
    plain = MarkdownIt("commonmark")
    assert "**「重要」**" in plain.render("これは**「重要」**です。")
    assert "なので\n途中" in plain.render("これは長い文章なので\n途中で改行しています。")


def test_is_cjk():
    assert all(is_cjk(c) for c in "漢あア「。￥Ａ")
    assert not any(is_cjk(c) for c in "aZ1 .(")
