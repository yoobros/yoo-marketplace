---
name: marp-slides
description: >
  Marp(Markdown Presentation)로 슬라이드를 만들고 관리한다. 자연어로 슬라이드 생성·수정·빌드를
  요청하면 .md 파일을 편집하고 marp-cli로 HTML/PDF/PPTX를 빌드한다. LaTeX 수식, Mermaid
  다이어그램, 논문 스타일 footnote/citation, 네이버 커스텀 테마를 지원한다.
  "슬라이드 만들어줘", "발표자료", "프레젠테이션", "ppt", "marp", "슬라이드에 ~ 추가해줘",
  "수식 넣어줘", "다이어그램 그려줘", "footnote 추가", "테마 바꿔줘" 같은 요청에서 트리거.
---

Marp 기반 프레젠테이션을 자연어로 만들고 관리하는 스킬입니다.

## 프로젝트 구조

슬라이드 프로젝트는 아래 구조로 생성합니다. 사용자가 경로를 지정하지 않으면 현재 작업 디렉토리에 `marp/` 폴더를 만듭니다.

```
marp/
├── src/                        # 슬라이드 소스 (.md)
│   └── slides.md
├── themes/                     # 커스텀 테마
│   └── naver/
│       ├── naver.css
│       └── assets/
├── dist/                       # 빌드 결과물 (git 미추적)
├── package.json
└── .gitignore
```

## 초기화

새 슬라이드 프로젝트를 만들 때:

1. 위 디렉토리 구조를 생성한다
2. `npm init -y && npm install @marp-team/marp-cli`로 marp-cli를 설치한다
3. package.json에 빌드 스크립트를 추가한다:
   ```json
   {
     "scripts": {
       "build": "marp src/slides.md --html --theme-set themes/naver/naver.css --output dist/slides.html",
       "build:pdf": "marp src/slides.md --html --theme-set themes/naver/naver.css --pdf --output dist/slides.pdf",
       "build:pptx": "marp src/slides.md --html --theme-set themes/naver/naver.css --pptx --output dist/slides.pptx",
       "build:all": "npm run build && npm run build:pdf && npm run build:pptx",
       "preview": "marp -s src/ --theme-set themes/naver/naver.css"
     }
   }
   ```
4. `.gitignore`에 `node_modules/`, `dist/`, `package-lock.json`을 추가한다
5. 이 스킬의 `assets/naver.css` 파일을 `themes/naver/naver.css`로 복사한다

## 네이버 테마

이 스킬에 번들된 `assets/naver.css`는 네이버 공식 .thmx에서 추출한 커스텀 테마이다.
NAVER 로고가 base64로 임베드되어 있어 self-contained이다.

### 색상 변수

| 변수 | 값 | 용도 |
|------|-----|------|
| `--naver-green` | `#03C75A` | 제목, 강조 |
| `--naver-dark` | `#1F497D` | h3 |
| `--accent1` ~ `--accent6` | Office 계열 | 차트, 강조 |

### 슬라이드 클래스

개별 슬라이드에 `<!-- _class: 클래스명 -->`으로 적용한다.

| 클래스 | 용도 |
|--------|------|
| `lead` | 타이틀/표지 슬라이드 (중앙 정렬, 그라데이션 배경) |
| `invert` | 어두운 배경 슬라이드 |
| `highlight` | 네이버 그린 배경 강조 슬라이드 |
| (없음) | 기본 흰색 배경 |

## 슬라이드 작성 규칙

### 기본 frontmatter

모든 슬라이드 파일은 이 frontmatter로 시작한다:

```markdown
---
marp: true
theme: naver
math: mathjax
paginate: true
style: |
  .mermaid {
    display: flex;
    justify-content: center;
    background: none;
    border: none;
    width: 100%;
  }
  .mermaid svg {
    max-width: 100% !important;
    max-height: 330px;
    height: auto !important;
  }
---
```

### 슬라이드 구분

`---`로 슬라이드를 구분한다.

### 제목 (h1)

CSS에서 `section > h1:first-of-type`이 `position: absolute; top: 30px`으로 고정되어 있다.
모든 일반 슬라이드에서 h1은 동일한 위치에 표시된다. lead 클래스 슬라이드는 예외.

### 타이틀 슬라이드

```markdown
<!-- _class: lead -->

# 발표 제목
## 부제목
### 소속 발표자명
```

### 목차 슬라이드

표지 바로 다음에 목차를 넣는다:

```markdown
# 목차

1. 첫 번째 주제
2. 두 번째 주제
3. 세 번째 주제
```

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

마지막 슬라이드 하단에 mermaid 스크립트를 반드시 추가한다. **`htmlLabels: false` 를 반드시 넣는다** — 이게 빠지면 PDF/PPTX 빌드에서 노드 텍스트가 잘린다(아래 설명):

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  htmlLabels: false,
  flowchart: { useMaxWidth: true, htmlLabels: false, nodeSpacing: 30, rankSpacing: 42, padding: 8 }
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

노드가 많거나 라벨이 긴 다이어그램은 슬라이드 폭/높이를 넘길 수 있다. frontmatter 의
`style` 블록에 아래를 넣어 SVG 를 슬라이드 안에 가둔다. `useMaxWidth: true` (위 init) 가 폭을,
`max-height` 가 높이를 잡아준다:

```css
.mermaid { display: flex; justify-content: center; background: none; border: none; width: 100%; }
.mermaid svg { max-width: 100% !important; max-height: 330px; height: auto !important; }
```

`.cols`(좌우 2단) 안에 다이어그램을 넣을 때는 `max-height` 를 더 작게(예: 230px) 둔다.
그래도 넘치면 다이어그램을 단순화한다 — 노드 수를 줄이고, 라벨을 짧게(두 단어 내),
`flowchart LR` 의 긴 사슬은 끊어 배치한다.

### Footnote / Citation (논문 스타일 참조)

본문에 상첨자 번호를 넣고, 슬라이드 하단에 참고문헌을 표시한다:

```markdown
Attention 메커니즘<sup>[1]</sup>은 ...

BERT<sup>[2]</sup> 기반 ...

<div class="footnote">

[1] Vaswani, A. et al. "Attention Is All You Need." *NeurIPS*, 2017. https://arxiv.org/abs/1706.03762
[2] Devlin, J. et al. "BERT: Pre-training of Deep Bidirectional Transformers." *NAACL*, 2019. https://arxiv.org/abs/1810.04805

</div>
```

- `<sup>[N]</sup>`: 초록색 상첨자 번호
- `<div class="footnote">`: 하단 구분선 + 회색 참고문헌 영역
- footnote 안의 빈 줄은 `<div>` 바로 뒤와 `</div>` 바로 앞에 하나씩 넣어야 마크다운으로 파싱된다

### 마지막 슬라이드

```markdown
# 끝

감사합니다
```

## 빌드

빌드 명령은 항상 프로젝트 루트(`marp/`)에서 실행한다.

| 명령 | 결과물 |
|------|--------|
| `npm run build` | `dist/slides.html` |
| `npm run build:pdf` | `dist/slides.pdf` |
| `npm run build:pptx` | `dist/slides.pptx` |
| `npm run build:all` | 위 세 가지 모두 |
| `npm run preview` | localhost:8080 실시간 미리보기 |

또는 npx로 직접:

```bash
npx @marp-team/marp-cli src/slides.md --html --theme-set themes/naver/naver.css --output dist/slides.html
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

변환된 페이지 이미지를 Read 로 열어 점검한다:
- 다이어그램 **노드 텍스트가 박스 안에 온전히** 들어가는가 (잘림 없음)
- 다이어그램이 슬라이드 폭/높이를 **넘치지 않는가**
- 본문이 슬라이드 하단을 넘어 **잘리지 않는가**

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

## 새 테마 추가

1. `themes/<테마명>/` 디렉토리 생성
2. `<테마명>.css` 작성 (첫 줄에 `/* @theme <테마명> */` 필수)
3. 에셋은 `assets/` 하위에 배치, CSS에 base64 임베드 권장
4. `package.json` scripts의 `--theme-set` 경로 변경

## 예시 슬라이드 템플릿

아래는 전체 기능을 보여주는 최소 템플릿이다. 새 슬라이드 생성 시 이 구조를 기반으로 한다.

```markdown
---
marp: true
theme: naver
math: mathjax
paginate: true
style: |
  .mermaid {
    display: flex;
    justify-content: center;
    background: none;
    border: none;
    width: 100%;
  }
  .mermaid svg {
    max-width: 100% !important;
    max-height: 330px;
    height: auto !important;
  }
---

<!-- _class: lead -->

# 발표 제목
## 부제목
### 소속 발표자명

---

# 목차

1. 주제 A
2. 주제 B

---

# 주제 A

본문 내용. 인라인 수식 $E = mc^2$.

$$
\text{block equation here}
$$

---

# 주제 B

내용<sup>[1]</sup>을 설명합니다.

<div class="footnote">

[1] 저자. "논문명." *학회*, 연도. URL

</div>

---

# 끝

감사합니다

<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  htmlLabels: false,
  flowchart: { useMaxWidth: true, htmlLabels: false, nodeSpacing: 30, rankSpacing: 42, padding: 8 }
});
</script>
```
