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
    max-width: 92% !important;
    max-height: 300px;
    height: auto !important;
  }
  .cols .mermaid svg { max-height: 210px; }
  .small { font-size: 0.8em; }
  .lead h2 { color: #fff; }
  table { font-size: 0.82em; }
  table thead th { background-color: var(--accent, #03C75A); color: #fff; }
  section.highlight strong { color: #fff; text-decoration: underline; text-decoration-color: color-mix(in srgb, #fff 50%, transparent); }
  .pill { display: inline-block; padding: 1px 8px; border-radius: 12px; background: #f4f4f4; color: #555; font-size: 0.78em; border: 1px solid #e0e0e0; }
  .cols { display: flex; gap: 28px; }
  .cols > div { flex: 1; }
  .card {
    border: 1px solid #e8e8e8;
    border-left: 3px solid var(--accent, #03C75A);
    border-radius: 6px;
    padding: 12px 16px;
    background: #fff;
    margin-bottom: 10px;
  }
  .muted { color: #888; font-size: 0.85em; }
  /* --- 폰트 크게 + 세로 균형 (여백 줄이고 전달력↑) --- */
  section:not(.lead):not(.highlight) {
    padding: 88px 60px 52px 60px; font-size: 1.15em;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;   /* 세로 중앙 균형 — 콘텐츠를 화면에 채움 */
    align-items: stretch !important;
  }
  section p { margin: 0.5em 0; line-height: 1.55; }
  section ul, section ol { margin: 0.45em 0; padding-left: 1.15em; }
  section li { line-height: 1.55; margin: 0.3em 0; }
  /* --- 표 밀도 (PDF 잘림 방지) --- */
  table th, table td { padding: 5px 12px; }
  section.compact { font-size: 1.0em; }
  section.compact table { font-size: 0.76em; }
  section.compact table th, section.compact table td { padding: 4px 9px; }
  section.compact .muted { font-size: 0.72em; }
  section.compact li, section.compact p { line-height: 1.4; }
  .cols pre.tall svg { max-height: 420px !important; }
---

<!--
==============================================================================
 code-baseline: {{sha}} ({{YYYY-MM-DD}})
 (코드/프로젝트 설명 덱일 때만) 이 덱이 설명하는 대상 코드의 커밋을 명시한다.
 갱신 시:  git rev-parse --short HEAD  &&  git log -1 --format=%cd --date=short
 문서 브랜치 머지 커밋이 아니라 '설명 대상 코드'의 커밋을 적는다.
==============================================================================
-->

<!-- _class: lead -->

# 발표 제목

## 한 문장 부제 — 무엇을 하는가

### 팀/프로젝트명 · 이슈번호

<div class="footnote">

프로젝트명 · 저장소 URL · 코드 기준 {{sha}} ({{YYYY-MM-DD}})

</div>

---

# 목차

1. **한 장 요약** — 무엇을 만드는가
2. **동기** — 왜 필요한가
3. **핵심 개념** — 용어/구조
4. **전체 아키텍처**
5. **세부 파이프라인 / 구현**
6. **현재 상태 & 로드맵**

---

<!-- _class: highlight -->

# 한 장 요약

## 청중이 하나만 기억한다면 이 문장

**무엇을 만드나** — 한 문단 요약

- **기존**: 지금까지의 방식/한계
- **우리**: 무엇이 달라지는가

**기대 효과**

- 효과 1
- 효과 2

---

# 동기 — 좌우 대비 (문제/해결, 기존/신규)

<div class="cols">
<div>

### 지금까지 (문제)

<pre class="mermaid">
graph TD
A["입력"] --> B["같은 것"]
A --> C["비슷한 것"]
</pre>

문제 설명 한두 문장.

</div>
<div>

### 우리가 하려는 것 (해결)

<pre class="mermaid">
graph TD
A["입력"] --> B["다른 분야 1"]
A --> C["다른 분야 2"]
A --> D["다른 분야 3"]
</pre>

해결 설명 한두 문장. **핵심어는 볼드**.

</div>
</div>

---

# 핵심 개념 — pill 태그 + card 요점

개념 문단. <span class="pill">태그 · 부가 라벨</span> 은 pill 로.

<div class="cols">
<div>

### 개념 A <span class="pill">특성 요약</span>

**① 단계** — 설명
**② 단계** — 설명

</div>
<div>

### 개념 B <span class="pill">특성 요약</span>

**① 단계** — 설명
**② 단계** — 설명

</div>
</div>

<div class="card">

이 슬라이드의 **핵심 요점 한 문단**은 card 로 — 좌측 accent 보더가 시선을 잡는다.

</div>

---

# 전체 아키텍처 — mermaid flowchart

<pre class="mermaid">
flowchart LR
subgraph OFF["① 배치"]
direction TB
O1["입력"] --> O2["처리"]
end
O2 --> DB[("저장소")]
DB --> ON["② 서빙"]
</pre>

- 다이어그램 아래 핵심 설명 2~3 bullet
- 수치는 **볼드** (예: ~ms, ~70배)

<p class="muted">부연/캡션은 muted 로 — 본문 흐름을 방해하지 않게</p>

---

<!-- _class: compact -->

# 밀도 높은 슬라이드 — 표 2개 이상이면 compact

| 항목 | 값 A | 값 B |
|------|-----:|-----:|
| 행 1 | 1 | 2 |
| 행 2 | 3 | 4 |

<div class="cols">
<div>

<pre class="mermaid tall">
sequenceDiagram
    autonumber
    participant A as 호출자
    participant B as 서버
    A->>B: 요청
    B-->>A: 응답
</pre>

</div>
<div>

- 시퀀스 다이어그램은 `.cols` 한쪽에 `tall` 클래스로 세로 확보
- 반대쪽에 설명/표 배치

</div>
</div>

<p class="muted">측정 조건 · 코드 기준 sha · 날짜 같은 재현 정보는 muted 캡션에</p>

---

# 현재 상태 & 로드맵

<div class="cols">
<div>

### ✅ 완료

- 항목 — 한 줄 근거
- 항목 — 한 줄 근거

</div>
<div>

### 🚀 차기 과제 (순서)

1. 과제 1
2. 과제 2

<div class="card">
현재 위치 + 다음 한 걸음을 card 한 문단으로.
</div>

</div>
</div>

---

<!-- _class: lead -->

# 감사합니다

## 프로젝트명 — 한 줄 소개

### 문의 · 상세: README.md / 이슈번호

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
