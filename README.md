# mdit-py-cjk-friendly

日本語 | [English](https://github.com/aiseed-dev/mdit-py-cjk-friendly/blob/main/README.en.md) | [繁體中文](https://github.com/aiseed-dev/mdit-py-cjk-friendly/blob/main/README.zh-TW.md) | [한국어](https://github.com/aiseed-dev/mdit-py-cjk-friendly/blob/main/README.ko.md)

[markdown-it-py](https://github.com/executablebooks/markdown-it-py) を
日本語・中国語・韓国語 (CJK) フレンドリーにするプラグイン。

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
# <p>これは長い文章なので途中で改行しています。</p>   (不要な空白が入らない)
```

## 直る問題

CommonMark は空白で単語を区切る言語を前提に設計されており、
CJK テキストでは有名な問題が2つ起きる:

1. **文中改行が空白になる** — Markdown ソースを日本語文の途中で改行すると、
   描画後に不要な半角スペースが入る。本プラグインは改行の前後がともに
   CJK 文字なら詰めて結合する (英文の折り返しは従来どおり)。
2. **全角約物に隣接した強調が効かない** — `**「重要」**です` は CommonMark
   の flanking 規則で不成立になりリテラルの `**` が残る。本プラグインは
   flanking 判定で CJK 文字を punctuation 互換として扱い、パーサレベルで
   解決する (コードスパン・コードブロックには影響しない)。

強調の挙動は [CommonMark CJK-friendly 仕様ドラフト](https://github.com/tats-u/markdown-cjk-friendly)
の考え方に従った、markdown-it-py 向けの独立・簡易実装です
(JavaScript は本家プロジェクトのプラグインをどうぞ)。

## ふりがな(ルビ)— オプション

構文の追加になるため、別プラグイン `ruby` として opt-in で提供する
(でんでんマークダウン形式):

```python
from mdit_py_cjk_friendly import cjk_friendly, ruby

md = MarkdownIt("commonmark").use(cjk_friendly).use(ruby)
md.render("{漢字|かんじ}")          # → <ruby>漢字<rp>(</rp><rt>かんじ</rt><rp>)</rp></ruby>
md.render("{東京|とう|きょう}")      # → モノルビ (読みの数=文字数のとき)
```

- 読みの数が文字数と合わない・空の要素がある場合は変換しない(推測しない)
- `\{` でエスケープ。コードスパン・コードブロック内は変換されない
- `<rp>` 括弧つきで出力するので、ルビ非対応の環境では「漢字(かんじ)」に落ちる

## 補足

- 効くのは `.use(cjk_friendly)` したパーサだけ。同一プロセスの他の
  `MarkdownIt` インスタンスは上流と完全に同じ挙動を保つ
- markdown-it-py 2.x / 3.x 対応

## ライセンス

MIT
