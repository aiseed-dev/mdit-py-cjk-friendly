# mdit-py-cjk-friendly

[日本語](README.md) | [English](README.en.md) | [简体中文](README.zh.md) | 한국어

[markdown-it-py](https://github.com/executablebooks/markdown-it-py)를
한국어·일본어·중국어 (CJK) 텍스트에 친화적으로 만드는 플러그인.

```bash
# PyPI 공개 전에는 GitHub에서 설치:
pip install "mdit-py-cjk-friendly @ git+https://github.com/aiseed-dev/mdit-py-cjk-friendly.git"
# PyPI 공개 후: pip install mdit-py-cjk-friendly
```

```python
from markdown_it import MarkdownIt
from mdit_py_cjk_friendly import cjk_friendly

md = MarkdownIt("commonmark").use(cjk_friendly)

md.render("이것은**「중요」**합니다.")
# <p>이것은<strong>「중요」</strong>합니다.</p>
```

## 해결하는 문제

CommonMark는 공백으로 단어를 구분하는 언어를 전제로 설계되어,
CJK 텍스트에서 잘 알려진 두 가지 문제가 발생합니다:

1. **소프트 줄바꿈이 공백이 됩니다.** 소스의 줄바꿈은 `\n`으로 렌더링되고,
   브라우저는 이를 공백 하나로 접습니다 — 일본어·중국어 문장 중간에서는
   잘못된 동작입니다. 이 플러그인을 쓰면 두 CJK 문자 사이의 소프트
   줄바꿈은 아무것도 출력하지 않습니다. 라틴 문자 텍스트는 기존 동작을
   유지합니다.
2. **전각 문장부호 옆의 강조가 실패합니다.** `**「중요」**합니다`는 `「`가
   유니코드 문장부호라서 left/right-flanking 규칙에 걸려 별표가 그대로
   남습니다. 이 플러그인은 flanking 판정에서 CJK 문자를 문장부호 호환으로
   취급하여 파서 레벨에서 해결합니다 (코드 스팬·코드 블록에는 영향이
   없습니다).

강조 동작은 [CommonMark CJK-friendly 사양 초안](https://github.com/tats-u/markdown-cjk-friendly)의
아이디어를 따른, markdown-it-py용 독립 간이 구현입니다
(JavaScript 사용자는 해당 프로젝트의 플러그인을 사용하세요).

## 참고

- `.use(cjk_friendly)`를 호출한 파서에만 적용됩니다. 같은 프로세스의 다른
  `MarkdownIt` 인스턴스는 업스트림과 완전히 동일하게 동작합니다.
- markdown-it-py 2.x / 3.x 지원.

## 라이선스

MIT
