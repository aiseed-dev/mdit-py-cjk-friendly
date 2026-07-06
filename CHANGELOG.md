# Changelog

## 0.1.1 (2026-07-07)

### Fixed

- 内側が和文約物・外側が英数字のケース (`a**あ、**b`、`**abc、**です` 等) が
  不成立のままだった問題を修正。flanking 判定を仕様ドラフトに沿った
  「CJK は許可側では約物・阻止側では非約物」の非対称な扱いに書き直した。
  素の CommonMark で成立するケースへの影響がないことは回帰テストで担保
  (全29テスト)。


## 0.1.0 (2026-07-07)

Initial release, extracted from the aiseed-dev/website build tooling.

- `cjk_friendly` plugin for markdown-it-py:
  - softbreak between two CJK characters renders as nothing (no spurious space)
  - emphasis flanking treats CJK characters as punctuation-compatible, so
    `**「重要」**です` parses as emphasis (parser-level; per-parser opt-in)
