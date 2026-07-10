"""ruby プラグイン(でんでん形式のふりがな)の検査。"""
from markdown_it import MarkdownIt

from mdit_py_cjk_friendly import cjk_friendly, ruby


def md():
    return MarkdownIt("commonmark").use(cjk_friendly).use(ruby)


def test_group_ruby():
    out = md().render("{漢字|かんじ}を書く。")
    assert "<ruby>漢字<rp>(</rp><rt>かんじ</rt><rp>)</rp></ruby>を書く。" in out


def test_mono_ruby():
    out = md().render("{東京|とう|きょう}")
    assert (
        "<ruby>東<rp>(</rp><rt>とう</rt><rp>)</rp>"
        "京<rp>(</rp><rt>きょう</rt><rp>)</rp></ruby>"
    ) in out


def test_reading_count_mismatch_passthrough():
    """読みの数が文字数と合わなければ変換しない(推測しない)。"""
    out = md().render("{東京都|とう|きょう}")
    assert "<ruby>" not in out
    assert "{東京都|とう|きょう}" in out


def test_no_pipe_passthrough():
    out = md().render("{ただの波括弧}")
    assert "<ruby>" not in out
    assert "{ただの波括弧}" in out


def test_empty_parts_passthrough():
    assert "<ruby>" not in md().render("{|かんじ}")
    assert "<ruby>" not in md().render("{漢字|}")


def test_escaped_brace():
    out = md().render("\\{漢字|かんじ}")
    assert "<ruby>" not in out
    assert "{漢字|かんじ}" in out


def test_code_span_untouched():
    out = md().render("`{漢字|かんじ}`")
    assert "<ruby>" not in out
    assert "<code>{漢字|かんじ}</code>" in out


def test_html_escaped_in_output():
    out = md().render("{<b>|&}")
    assert "<b>" not in out
    assert "&lt;b&gt;" in out and "&amp;" in out


def test_without_plugin_no_conversion():
    out = MarkdownIt("commonmark").use(cjk_friendly).render("{漢字|かんじ}")
    assert "<ruby>" not in out


def test_multiple_in_one_line_with_emphasis():
    out = md().render("**{強|きょう}調**と{弱|じゃく}。")
    assert out.count("<ruby>") == 2
    assert "<strong>" in out


def test_multiline_inner_passthrough():
    out = md().render("{漢字|かん\nじ}")
    assert "<ruby>" not in out
