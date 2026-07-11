# mdit-py-cjk-friendly

[日本語](README.md) | [English](README.en.md) | [繁體中文](README.zh-TW.md) | 한국어

[markdown-it-py](https://github.com/executablebooks/markdown-it-py)를
한국어·일본어·중국어 (CJK) 텍스트에 친화적으로 만드는 플러그인.

```bash
pip install mdit-py-cjk-friendly
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

## 후리가나(루비) — 선택

문법 확장이므로 별도의 opt-in 플러그인 `ruby` 로 제공합니다
(덴덴 마크다운 표기):

```python
from mdit_py_cjk_friendly import cjk_friendly, ruby

md = MarkdownIt("commonmark").use(cjk_friendly).use(ruby)
md.render("{漢字|かんじ}")   # → <ruby>漢字<rp>(</rp><rt>かんじ</rt><rp>)</rp></ruby>
```

- 읽기 개수가 글자 수와 맞지 않거나 빈 요소가 있으면 변환하지 않음(추측하지 않음)
- `\{` 로 이스케이프. 코드 스팬 안은 변환되지 않음
- `<rp>` 괄호 포함 출력이므로 루비 미지원 환경에서는 「漢字(かんじ)」로 표시

## 방점·방선(bouten) — 선택

덴덴 마크다운에는 방점 전용 표기가 없고, `*text*` → `<em>` 를 세로쓰기일 때만
방점으로 표시하는 사양뿐입니다(방점의 종류를 구분할 수 없음). 종류를 지정해
방점·방선을 쓰려면, 별도의 opt-in 플러그인 `bouten` 이 Pandoc 스타일의 클래스
스팬을 추가합니다:

```python
from mdit_py_cjk_friendly import cjk_friendly, bouten

md = MarkdownIt("commonmark").use(cjk_friendly).use(bouten)
md.render("[邪智暴虐]{.sesame_dot}")      # → <em class="sesame_dot">邪智暴虐</em>
md.render("[あ]{.underline_double}")      # → <em class="underline_double">あ</em>
```

- 클래스 이름 하나를 `<em class>` 로 그대로 전달할 뿐이며, 겉모습(어느 클래스가
  참깨점·이중 밑줄인지)은 CSS 가 정함
- `]` 바로 뒤가 `{.class}` 가 아니면 아무것도 하지 않으므로 링크 `[x](y)` 와
  단순 `[x]` 를 깨뜨리지 않음. 안쪽 텍스트는 그대로 취급(추측하지 않음)
- `*`/`**`(강조·굵게)는 순수 Markdown 에 맡김
- 아오조라 문고 종류에 대응하는 클래스 예: 방점 `sesame_dot` /
  `white_sesame_dot` / `black_circle` / `white_circle` / `bullseye` /
  `fisheye` / `saltire` / `black_up-pointing_triangle` /
  `white_up-pointing_triangle`, 방선 `underline_solid` / `underline_double` /
  `underline_dotted` / `underline_dashed` / `underline_wave`(반대쪽은
  `overline_*`)

## 라이선스

MIT
