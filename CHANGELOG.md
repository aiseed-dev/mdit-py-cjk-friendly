# Changelog

## 0.1.0 (2026-07-07)

Initial release, extracted from the aiseed-dev/website build tooling.

- `cjk_friendly` plugin for markdown-it-py:
  - softbreak between two CJK characters renders as nothing (no spurious space)
  - emphasis flanking treats CJK characters as punctuation-compatible, so
    `**「重要」**です` parses as emphasis (parser-level; per-parser opt-in)
