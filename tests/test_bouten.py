"""bouten プラグイン(傍点・傍線 = text-emphasis)の検査。

記法は Pandoc 風のクラス付きスパン ``[テキスト]{.class}`` → ``<em class>``。
青空文庫の注記(傍点9種・傍線5種)を無損失に運べることを、実データ由来の
フィクスチャで確認する。
"""
from markdown_it import MarkdownIt

from mdit_py_cjk_friendly import bouten, cjk_friendly, ruby


def md():
    return MarkdownIt("commonmark").use(cjk_friendly).use(bouten)


def test_sesame_dot():
    out = md().render("[邪智暴虐]{.sesame_dot}を憎んだ。")
    assert '<em class="sesame_dot">邪智暴虐</em>を憎んだ。' in out


def test_bouten_variants():
    for cls in ("black_circle", "white_circle", "bullseye", "fisheye", "saltire"):
        out = md().render(f"[あ]{{.{cls}}}")
        assert f'<em class="{cls}">あ</em>' in out


def test_underline_variants():
    for cls in ("underline_solid", "underline_double", "underline_dotted",
                "underline_dashed", "underline_wave", "overline_solid"):
        out = md().render(f"[語]{{.{cls}}}")
        assert f'<em class="{cls}">語</em>' in out


def test_link_untouched():
    """``[x](y)`` はリンクのまま(傍点規則は素通り)。"""
    out = md().render("[青空](https://example.com)")
    assert '<a href="https://example.com">青空</a>' in out
    assert "<em" not in out


def test_bare_bracket_untouched():
    out = md().render("[ただの角括弧]")
    assert "<em" not in out
    assert "[ただの角括弧]" in out


def test_empty_bracket_passthrough():
    out = md().render("[]{.sesame_dot}")
    assert "<em" not in out


def test_newline_inside_passthrough():
    out = md().render("[あ\nい]{.sesame_dot}")
    assert "<em" not in out


def test_html_escaped_in_output():
    out = md().render("[<b>&]{.sesame_dot}")
    assert "<b>" not in out
    assert "&lt;b&gt;" in out and "&amp;" in out


def test_code_span_untouched():
    out = md().render("`[あ]{.sesame_dot}`")
    assert "<em" not in out
    assert "<code>[あ]{.sesame_dot}</code>" in out


def test_without_plugin_no_conversion():
    out = MarkdownIt("commonmark").use(cjk_friendly).render("[あ]{.sesame_dot}")
    assert "<em" not in out
    assert "[あ]{.sesame_dot}" in out


def test_coexists_with_ruby():
    """ruby と bouten を同時に使える(独立した opt-in)。"""
    m = MarkdownIt("commonmark").use(cjk_friendly).use(ruby).use(bouten)
    out = m.render("[{漢字|かんじ}]{.sesame_dot}")
    # inner はプレーン扱い: ruby 記法はそのまま文字列として傍点内に入る
    assert '<em class="sesame_dot">' in out
    out2 = m.render("{漢字|かんじ}[語]{.sesame_dot}")
    assert "<ruby>" in out2 and '<em class="sesame_dot">語</em>' in out2


# ── 青空文庫由来フィクスチャ(aozorabunko-py の decorate.COMMAND_TABLE 準拠) ──
# 注記付きテキスト → aozorabunko が生成する Markdown → 本プラグインの出力。
# 双方のバージョンアップで往復が壊れないことを固定する。
AOZORA_FIXTURES = [
    # (注記付きテキスト, aozora の Markdown, 期待 HTML 断片)
    ("邪智暴虐［＃「邪智暴虐」に傍点］",
     "[邪智暴虐]{.sesame_dot}",
     '<em class="sesame_dot">邪智暴虐</em>'),
    ("あ［＃「あ」に二重傍線］",
     "[あ]{.underline_double}",
     '<em class="underline_double">あ</em>'),
    ("あ［＃「あ」の左に傍点］",              # 方向フィルタ: 左 → 反対側
     "[あ]{.sesame_dot_after}",
     '<em class="sesame_dot_after">あ</em>'),
    ("あ［＃「あ」の上に傍線］",              # 方向フィルタ: 上 → overline
     "[あ]{.overline_solid}",
     '<em class="overline_solid">あ</em>'),
]


def test_aozora_fixtures():
    m = md()
    for _annotated, markdown, expected_html in AOZORA_FIXTURES:
        assert expected_html in m.render(markdown)
