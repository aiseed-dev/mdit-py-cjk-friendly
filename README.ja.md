# mdit-py-cjk-friendly

[markdown-it-py](https://github.com/executablebooks/markdown-it-py) を
日本語 (中国語・韓国語) フレンドリーにするプラグイン。

```bash
pip install mdit-py-cjk-friendly
```

```python
from markdown_it import MarkdownIt
from mdit_py_cjk_friendly import cjk_friendly

md = MarkdownIt("commonmark").use(cjk_friendly)
```

## 直る問題

1. **文中改行が空白になる** — Markdown ソースを日本語文の途中で改行すると、
   描画後に不要な半角スペースが入る。本プラグインは改行の前後がともに
   CJK 文字なら詰めて結合する (英文の折り返しは従来どおり)。
2. **全角記号に隣接した強調が効かない** — `**「重要」**です` は CommonMark
   の flanking 規則で不成立になりリテラルの `**` が残る。本プラグインは
   flanking 判定で CJK 文字を punctuation 互換として扱い、パーサレベルで
   解決する (コードスパン・コードブロックには影響しない)。

強調の挙動は [CommonMark CJK-friendly 仕様ドラフト](https://github.com/tats-u/markdown-cjk-friendly)
の考え方に従った、markdown-it-py 向けの独立・簡易実装です。

## ライセンス

MIT
