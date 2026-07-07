# mdit-py-cjk-friendly

[日本語](README.md) | [English](README.en.md) | 繁體中文 | [한국어](README.ko.md)

讓 [markdown-it-py](https://github.com/executablebooks/markdown-it-py)
對中文、日文、韓文 (CJK) 文字友善的外掛。

```bash
# PyPI 發佈前，請從 GitHub 安裝:
pip install "mdit-py-cjk-friendly @ git+https://github.com/aiseed-dev/mdit-py-cjk-friendly.git"
# PyPI 發佈後: pip install mdit-py-cjk-friendly
```

```python
from markdown_it import MarkdownIt
from mdit_py_cjk_friendly import cjk_friendly

md = MarkdownIt("commonmark").use(cjk_friendly)

md.render("這是**「重點」**內容。")
# <p>這是<strong>「重點」</strong>內容。</p>

md.render("這是一個比較長的句子\n中間換了一行。")
# <p>這是一個比較長的句子中間換了一行。</p>   (不會插入多餘的空格)
```

## 解決的問題

CommonMark 是以空格分隔單字的語言為前提所設計，對 CJK 文字有兩個
眾所周知的問題:

1. **軟換行變成空格。** 原始檔中的換行會算繪為 `\n`，瀏覽器再將它
   折疊成一個空格——在中文句子裡這是錯的。使用本外掛後，兩個 CJK
   字元之間的軟換行不輸出任何內容；拉丁文字維持原本的行為。
2. **全形標點旁的強調失效。** `**「重點」**內容` 會留下字面的星號，
   因為 `「` 屬於 Unicode 標點，破壞了 left/right-flanking 規則。
   本外掛在 flanking 判定中把 CJK 字元視為與標點相容 (在剖析器層級
   處理，程式碼區段與程式碼區塊自然不受影響)。

強調的行為遵循 [CommonMark CJK-friendly 規範草案](https://github.com/tats-u/markdown-cjk-friendly)
的想法 (本專案是針對 markdown-it-py 的獨立簡化實作；
JavaScript 使用者請改用該專案的外掛)。

## 說明

- 只影響呼叫了 `.use(cjk_friendly)` 的剖析器；同一行程中的其他
  `MarkdownIt` 實例保持與上游完全一致的行為。
- 支援 markdown-it-py 2.x 與 3.x。

## 授權條款

MIT
