---
name: marp-slides
description: >
  Marp(Markdown Presentation)로 슬라이드를 만들고 관리한다. 자연어로 슬라이드 생성·수정·빌드를
  요청하면 .md 파일을 편집하고 marp-cli로 HTML/PDF/PPTX를 빌드한다. LaTeX 수식, Mermaid
  다이어그램, 논문 스타일 footnote/citation, 커스텀 테마(번들 네이버 테마 또는 브랜드
  CSS/디자인 가이드 기반 신규 테마)를 지원한다.
  "슬라이드 만들어줘", "발표자료", "프레젠테이션", "ppt", "marp", "슬라이드에 ~ 추가해줘",
  "수식 넣어줘", "다이어그램 그려줘", "footnote 추가", "테마 바꿔줘", "브랜드 스타일로 꾸며줘"
  같은 요청에서 트리거.
---

Marp 기반 프레젠테이션을 자연어로 만들고 관리하는 스킬입니다.

> **번들 자산 경로**: 본문에서 `assets/...` 는 **이 SKILL.md 파일이 있는 디렉토리 기준**이다.
> 번들 파일: `assets/slides-template.md` (덱 골격+레이아웃 CSS), `assets/naver.css` (네이버 테마),
> `assets/naver-logo*.png`. 복사 예: `cp <스킬디렉토리>/assets/slides-template.md marp/src/slides.md`

## 새 덱을 만드는 최단 경로

1. 아래 [초기화](#초기화)로 프로젝트 골격 생성
2. **이 스킬의 `assets/slides-template.md` 를 `src/slides.md` 로 복사** — 검증된
   frontmatter(레이아웃 유틸리티 CSS 포함) + 덱 구성 골격(표지→목차→한 장 요약→…→감사)이
   들어 있다. 내용만 채우면 완성 형태가 나온다
3. 테마 결정 — 번들 `naver` 테마를 쓰거나, 사용자가 준 브랜드 CSS/디자인 문서로
   [커스텀 테마 제작](#커스텀-테마-제작-브랜드-css디자인-가이드--marp-테마)
4. `npm run build && npm run build:pdf` → [PDF 검증](#빌드-결과-검증-다이어그램이-있으면-pdf-기준으로)
   (검증 대상은 PDF — HTML 빌드만으로는 검증이 안 된다)

템플릿을 무시하고 백지에서 시작하지 않는다 — 수십 회 수작업 반복으로 수렴한 형태다.

## 사전 요구사항 (의존성)

작업 시작 전 아래를 확인하고, 없으면 설치를 안내하거나 (권한이 있으면) 직접 설치한다:

| 도구 | 용도 | 확인 | 설치 |
|------|------|------|------|
| Node.js ≥ 18 + npm | marp-cli 실행 | `node -v` | https://nodejs.org 또는 `brew install node` |
| `@marp-team/marp-cli` | 빌드/미리보기 | `npx marp --version` | 프로젝트 로컬 `npm install @marp-team/marp-cli` (전역 설치 불필요) |
| Chromium 계열 브라우저 | PDF/PPTX 빌드 (marp 이 headless 로 사용) | Chrome/Edge 설치 여부 | 대부분 이미 있음. 없으면 `npx puppeteer browsers install chrome` 후 `CHROME_PATH` 지정 |
| ImageMagick 또는 poppler | PDF 검증 (페이지→PNG) | `magick -version` / `pdftoppm -v` | `brew install imagemagick` 또는 `brew install poppler` (Linux: `apt install imagemagick poppler-utils`) |

- mermaid 는 설치 대상이 아니다 — 슬라이드 마지막 장의 `<script>` 가 CDN 에서 로드한다.
  **인터넷이 안 되는 발표 환경**이면 `mermaid.min.js` 를 로컬에 받아 상대경로로 참조.
- 사내망 등 프록시 환경에서 npm 설치가 실패하면 사내 registry (`npm config set registry ...`) 를 안내.

## 프로젝트 구조

슬라이드 프로젝트는 아래 구조로 생성합니다. 사용자가 경로를 지정하지 않으면 현재 작업 디렉토리에 `marp/` 폴더를 만듭니다.

```
marp/
├── src/                        # 슬라이드 소스 (.md)
│   └── slides.md
├── themes/                     # 커스텀 테마 (테마당 폴더 하나)
│   └── <테마명>/
│       ├── <테마명>.css
│       └── assets/
├── dist/                       # 빌드 결과물 (git 미추적)
├── package.json
└── .gitignore
```

## 초기화

새 슬라이드 프로젝트를 만들 때:

1. 위 디렉토리 구조를 생성한다
2. `npm init -y && npm install @marp-team/marp-cli`로 marp-cli를 설치한다
3. package.json에 빌드 스크립트를 추가한다 (`<테마명>` 치환. **preview 에도 `--html` 필수** —
   빠지면 raw HTML 이 이스케이프되어 mermaid 가 미리보기에서 렌더링되지 않는다):
   ```json
   {
     "scripts": {
       "build": "marp src/slides.md --html --theme-set themes/<테마명>/<테마명>.css --output dist/slides.html",
       "build:pdf": "marp src/slides.md --html --theme-set themes/<테마명>/<테마명>.css --pdf --output dist/slides.pdf",
       "build:pptx": "marp src/slides.md --html --theme-set themes/<테마명>/<테마명>.css --pptx --output dist/slides.pptx",
       "build:all": "npm run build && npm run build:pdf && npm run build:pptx",
       "preview": "marp -s --html src/ --theme-set themes/<테마명>/<테마명>.css"
     }
   }
   ```
4. `.gitignore`에 `node_modules/`, `dist/`, `package-lock.json`을 추가한다
5. 테마 CSS 배치 — 기본은 이 스킬의 `assets/naver.css` 를 `themes/naver/naver.css` 로 복사.
   사용자가 브랜드 스타일을 원하면 아래 커스텀 테마 절차로 제작
6. `assets/slides-template.md` 를 `src/slides.md` 로 복사하고 내용을 채운다

## 테마

### 번들 네이버 테마

이 스킬에 번들된 `assets/naver.css`는 네이버 공식 .thmx에서 추출한 커스텀 테마이다.
NAVER 로고가 base64로 임베드되어 있어 self-contained이다.
accent 색: `--naver-green #03C75A`.

### 슬라이드 클래스 (모든 테마 공통 계약)

개별 슬라이드에 `<!-- _class: 클래스명 -->`으로 적용한다. 커스텀 테마를 만들 때도
이 4종 클래스는 반드시 구현해 템플릿과 호환되게 한다.

| 클래스 | 용도 |
|--------|------|
| `lead` | 타이틀/표지 슬라이드 (중앙 정렬, 배경 강조) |
| `invert` | 어두운 배경 슬라이드 |
| `highlight` | accent 색 배경의 강조 슬라이드 ("한 장 요약" 등) |
| `compact` | 표·다이어그램이 많은 밀도 높은 슬라이드 (폰트/패딩 축소 — 템플릿 style 블록이 제공) |
| (없음) | 기본 밝은 배경 |

### 커스텀 테마 제작 (브랜드 CSS/디자인 가이드 → Marp 테마)

사용자가 브랜드 CSS 파일, 디자인 가이드 문서, 스크린샷, 또는 "○○ 느낌으로" 같은
요청을 주면 그것을 Marp 테마로 변환한다:

1. **디자인 토큰 추출** — 주어진 자료에서 다음을 뽑아 표로 정리해 사용자에게 확인받는다:
   - accent 색 1개 (+ hover용 어두운 변형), 텍스트 스케일 (제목/본문/보조), 배경/테두리 색
   - 제목/본문 폰트 (웹폰트면 base64 임베드 또는 CDN `@import`)
   - 로고 이미지 (있으면 base64 임베드해 self-contained 로)
2. **테마 CSS 작성** — `themes/<테마명>/<테마명>.css`:
   - 첫 줄에 `/* @theme <테마명> */` 필수
   - `section { --accent: <색>; }` 으로 accent 를 CSS 변수로 선언 — 템플릿의 레이아웃
     유틸리티(card 보더, 표 헤더 등)가 `var(--accent, ...)` 로 이 변수를 참조한다
   - 위 4종 슬라이드 클래스(`lead`/`invert`/`highlight`/`compact` 진입점) 구현
   - `section > h1:first-of-type` 을 상단 고정(`position: absolute; top: 30px`)해
     슬라이드 간 제목 위치를 일관되게 (lead 제외)
3. **frontmatter 교체** — `theme: <테마명>` + package.json `--theme-set` 경로 변경
4. **검증** — 템플릿 덱을 그대로 빌드해 4종 클래스 + card/pill/표가 새 테마에서
   깨지지 않는지 PDF 페이지 이미지로 확인 (아래 검증 절차)

디자인 감각이 필요한 색/폰트 선택은 임의로 정하지 말고, 후보 2~3개를 제시해
사용자가 고르게 한다. 비대화형 실행(CI 등)이라 확인을 받을 수 없으면 주어진 자료에서
가장 지배적인 색/폰트를 기본값으로 쓰고, 그 선택과 근거를 결과 보고에 명시한다.

## 슬라이드 작성 규칙

### 기본 frontmatter + 레이아웃 유틸리티

`assets/slides-template.md` 의 frontmatter 를 그대로 쓴다. `style:` 블록에 테마와
무관하게 동작하는 레이아웃 유틸리티가 들어 있다:

| 클래스/규칙 | 용도 |
|------------|------|
| `.cols` (+ `.cols > div`) | 좌우 2단 — 문제/해결, 기존/신규 같은 **대비 구도** |
| `.card` | 좌측 accent 보더 요점 박스 — 슬라이드의 **핵심 한 문단** |
| `.pill` | 인라인 태그/라벨 (h3 옆 특성 요약 등) |
| `.muted` | 회색 축소 캡션 — 측정 조건, 부연, 재현 정보 |
| `.small` | 0.8em 축소 텍스트 |
| `section.compact` | 표 2개 이상/밀도 높은 장 — 폰트·패딩 축소로 PDF 잘림 방지 |
| `section:not(.lead):not(.highlight)` flex 세로 중앙 | 콘텐츠가 적은 장도 세로 균형 — 위쪽 쏠림 방지 |
| `tall` (`<pre class="mermaid tall">`) | `.cols` 안 시퀀스 다이어그램 세로 확보 (max-height 420px) |

### 덱 구성 패턴 (권장 흐름)

1. **표지** (`lead`) — 제목 / 한 문장 부제 / 소속 + footnote 에 저장소·이슈 링크
2. **목차** — `**볼드 주제** — 한 줄 요약` 형태의 번호 목록
3. **한 장 요약** (`highlight`) — 청중이 하나만 기억할 문장 + 기존/신규 대비 + 기대 효과
4. **본문** — 대비는 `.cols`, 요점은 `.card`, 태그는 `.pill`, 밀도 높으면 `compact`
5. **현재 상태 & 로드맵** — ✅ 완료 / 🚀 차기 과제 2단
6. **감사** (`lead`) — 마지막 장 하단에 mermaid `<script>` 블록

한 슬라이드 한 메시지. 본문 bullet 은 3~5개, 핵심어만 **볼드**. 수치·근거는
`.muted` 캡션으로 분리해 본문을 가볍게 유지한다.

### 발표 언어 (한국어/영어)

템플릿 골격과 레이아웃 유틸리티는 언어 무관이다. **덱의 언어는 발표 언어를 따른다** —
사용자가 명시하지 않으면 요청 언어를 따르되, "영어 발표" 맥락이면 확인 후 영어로:

- 템플릿의 placeholder(발표 제목, 목차, 감사합니다 등)를 발표 언어로 채운다
  (영어: Agenda / One-slide Summary / Current Status & Roadmap / Thank You 등)
- mermaid 노드 라벨, 표 헤더, `.pill`/`.muted` 캡션도 같은 언어로 통일
- footnote 의 인용 표기는 원문 그대로 (논문 제목 등은 번역하지 않는다)
- 영어 제목은 sentence case 로 통일하고, 직역 대신 짧은 능동태 표현을 쓴다
- 같은 내용도 영어 표현이 더 길어질 수 있다 — 노드 라벨은 2~3 단어 내로, 표가 넘치면
  `compact` 클래스 적용 후 PDF 로 재확인

### 코드 설명 덱의 code-baseline 마커

특정 코드/프로젝트 상태를 설명하는 덱은 **설명 대상 코드의 커밋**을 두 곳에 명시한다
(문서 브랜치는 나중에 머지되므로 문서 커밋 날짜만으로는 어느 코드인지 알 수 없다):

1. frontmatter 바로 뒤 HTML 주석 — `code-baseline: <sha> (<date>)` (템플릿에 포함)
2. 표지 footnote — `코드 기준 <sha> (<date>)`

갱신 시 `git rev-parse --short HEAD && git log -1 --format=%cd --date=short` 값으로 교체.
코드를 설명하는 덱이 아니면 템플릿의 주석 블록과 footnote 의 `코드 기준 ...` 표기를
둘 다 삭제한다.

### 슬라이드 구분

`---`로 슬라이드를 구분한다.

### 제목 (h1)

테마 CSS에서 `section > h1:first-of-type`이 상단 고정되어 모든 일반 슬라이드에서
h1은 동일한 위치에 표시된다. lead 클래스 슬라이드는 예외.

### LaTeX 수식

인라인: `$E = mc^2$`

블록:
```markdown
$$
P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)}
$$
```

### Mermaid 다이어그램

**반드시 `<pre class="mermaid">` 태그를 사용하고, 들여쓰기 없이 작성한다.**
`<div>`나 들여쓰기를 쓰면 Marp에서 코드블록으로 인식되어 깨진다.

```markdown
<pre class="mermaid">
graph LR
A[시작] --> B[처리]
B --> C{판단}
C -->|Yes| D[완료]
C -->|No| B
</pre>
```

마지막 슬라이드 하단에 mermaid 스크립트를 반드시 추가한다. **`htmlLabels: false` 를 반드시 넣는다** — 이게 빠지면 PDF/PPTX 빌드에서 노드 텍스트가 잘린다(아래 설명). `securityLevel: 'loose'` 는 클릭 링크 등 HTML 상호작용, `themeVariables.fontSize` 는 라벨 크기 조절용:

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  securityLevel: 'loose',
  htmlLabels: false,
  flowchart: { useMaxWidth: true, htmlLabels: false, nodeSpacing: 30, rankSpacing: 42, padding: 8 },
  themeVariables: { fontSize: '15px' }
});
</script>
```

#### 왜 `htmlLabels: false` 인가 (PDF 노드 텍스트 잘림 방지)

mermaid 기본값(`htmlLabels: true`)은 노드 라벨을 SVG `foreignObject` 안의 HTML로 렌더한다.
이 방식은 브라우저 화면(HTML)·PNG 스크린샷에서는 멀쩡해 보이지만, **marp 의 PDF/PPTX 빌드는
headless Chromium 의 "인쇄(print)" 경로를 타는데 거기서는 foreignObject 의 텍스트 폭 계산이
어긋나 노드 박스보다 글자가 커져 잘린다** (예: `상품 로그·CTR` → `상품 로그`, `벡터 검색` →
`벡터 ㄱ`). `htmlLabels: false` 로 두면 라벨을 순수 SVG `<text>` 로 그리고 노드 박스를
`getBBox` 로 정확히 계산하므로 HTML·PDF·PPTX 모두에서 동일하게 안전하다. `<br/>` 줄바꿈도
SVG text 에서 정상 동작한다.

#### 다이어그램이 슬라이드를 넘치지 않게 (SVG 크기 제한)

노드가 많거나 라벨이 긴 다이어그램은 슬라이드 폭/높이를 넘길 수 있다. 템플릿 frontmatter 의
`style` 블록이 SVG 를 슬라이드 안에 가둔다. `useMaxWidth: true` (위 init) 가 폭을,
`max-height` 가 높이를 잡아준다:

```css
.mermaid { display: flex; justify-content: center; background: none; border: none; width: 100%; }
.mermaid svg { max-width: 92% !important; max-height: 300px; height: auto !important; }
.cols .mermaid svg { max-height: 210px; }        /* 2단 안은 더 작게 */
.cols pre.tall svg { max-height: 420px !important; }  /* 시퀀스 다이어그램은 tall 로 세로 확보 */
```

그래도 넘치면 다이어그램을 단순화한다 — 노드 수를 줄이고, 라벨을 짧게(두 단어 내),
`flowchart LR` 의 긴 사슬은 끊어 배치한다.

### Footnote / Citation (논문 스타일 참조)

본문에 상첨자 번호를 넣고, 슬라이드 하단에 참고문헌을 표시한다:

```markdown
Attention 메커니즘<sup>[1]</sup>은 ...

<div class="footnote">

[1] Vaswani, A. et al. "Attention Is All You Need." *NeurIPS*, 2017. https://arxiv.org/abs/1706.03762

</div>
```

- `<sup>[N]</sup>`: accent 색 상첨자 번호
- `<div class="footnote">`: 하단 구분선 + 회색 참고문헌 영역
- footnote 안의 빈 줄은 `<div>` 바로 뒤와 `</div>` 바로 앞에 하나씩 넣어야 마크다운으로 파싱된다
- 논문뿐 아니라 사내 이슈/저장소 링크 참조에도 같은 패턴을 쓴다

## 빌드

빌드 명령은 항상 프로젝트 루트(`marp/`)에서 실행한다.

| 명령 | 결과물 |
|------|--------|
| `npm run build` | `dist/slides.html` |
| `npm run build:pdf` | `dist/slides.pdf` |
| `npm run build:pptx` | `dist/slides.pptx` |
| `npm run build:all` | 위 세 가지 모두 |
| `npm run preview` | localhost:8080 실시간 미리보기 (`--html` 포함 필수) |

또는 npx로 직접:

```bash
npx @marp-team/marp-cli src/slides.md --html --theme-set themes/<테마명>/<테마명>.css --output dist/slides.html
```

## 빌드 결과 검증 (다이어그램이 있으면 PDF 기준으로)

슬라이드에 mermaid 다이어그램이 있으면 **HTML 미리보기나 PNG 스크린샷만으로는 부족하다.**
PNG 내보내기(`--images png`)는 화면 렌더 경로라 멀쩡해 보여도, **PDF/PPTX 는 인쇄 렌더 경로라
노드 텍스트 잘림 같은 문제가 PDF 에서만 나타날 수 있다** (위 `htmlLabels: false` 설명 참조).
그래서 사용자에게 결과물을 넘기기 전, **실제 PDF 를 페이지 이미지로 변환해 눈으로 확인한다**:

```bash
# PDF 빌드 후, 각 페이지를 PNG 로 변환해 확인 (ImageMagick)
npm run build:pdf
magick -density 90 dist/slides.pdf /tmp/pdfcheck/p-%02d.png   # 또는: pdftoppm -png -r 90 dist/slides.pdf /tmp/pdfcheck/p
```

변환된 페이지 이미지를 파일 읽기(이미지 뷰) 도구로 열어 점검한다. 이미지 뷰 도구가
없는 하네스에서는 페이지 이미지 경로를 사용자에게 전달해 직접 검토를 요청한다:
- 다이어그램 **노드 텍스트가 박스 안에 온전히** 들어가는가 (잘림 없음)
- 다이어그램이 슬라이드 폭/높이를 **넘치지 않는가**
- 본문이 슬라이드 하단을 넘어 **잘리지 않는가**
- 표가 많은 장은 `compact` 클래스가 적용되어 잘림이 없는가

문제가 보이면 `htmlLabels: false` 누락·SVG `max-height` 누락·다이어그램 과밀을 의심하고
고친 뒤 다시 PDF 로 확인한다. (HTML 만 보고 "정상"이라고 보고하지 말 것.)

## 수정 요청 처리

사용자가 자연어로 수정을 요청하면:

1. `src/slides.md` 파일을 읽는다
2. 요청에 맞게 마크다운을 수정한다
3. `npm run build`로 HTML을 빌드한다
4. 가능하면 preview로 결과를 확인한다

예시 요청과 대응:
- "3번 슬라이드에 수식 추가해줘" → 해당 슬라이드의 `---` 구간을 찾아 수식 블록 삽입
- "시퀀스 다이어그램에 DB 추가해줘" → `<pre class="mermaid">` 블록 내용 수정
- "어두운 테마로 바꿔줘" → `<!-- _class: invert -->` 추가
- "참고문헌 추가해줘" → `<sup>[N]</sup>` + `<div class="footnote">` 추가
- "우리 브랜드 색으로 바꿔줘" → 커스텀 테마 제작 절차 (디자인 토큰 확인 → 테마 CSS)
