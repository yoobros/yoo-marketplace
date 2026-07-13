# 왜 `htmlLabels: false` 인가 (PDF 노드 텍스트 잘림의 원리)

mermaid 기본값(`htmlLabels: true`)은 노드 라벨을 SVG `foreignObject` 안의 HTML로 렌더한다.
이 방식은 브라우저 화면(HTML)·PNG 스크린샷에서는 멀쩡해 보이지만, **marp 의 PDF/PPTX 빌드는
headless Chromium 의 "인쇄(print)" 경로를 타는데 거기서는 foreignObject 의 텍스트 폭 계산이
어긋나 노드 박스보다 글자가 커져 잘린다** (예: `상품 로그·CTR` → `상품 로그`, `벡터 검색` →
`벡터 ㄱ`). `htmlLabels: false` 로 두면 라벨을 순수 SVG `<text>` 로 그리고 노드 박스를
`getBBox` 로 정확히 계산하므로 HTML·PDF·PPTX 모두에서 동일하게 안전하다. `<br/>` 줄바꿈도
SVG text 에서 정상 동작한다.

같은 이유로 PNG 내보내기(`--images png`)는 화면 렌더 경로라 검증 수단이 못 된다 —
잘림은 인쇄 경로(PDF/PPTX)에서만 나타날 수 있으므로 검증은 반드시 실제 PDF 로 한다.

# mermaid 로컬 vendoring (CDN 불가 환경)

CDN 로드가 실패하면 다이어그램 자리가 **조용히 빈 채로** 빌드된다. 사내망·오프라인
환경에서는 mermaid 를 프로젝트에 받아두고 상대경로로 참조한다:

```bash
mkdir -p src/vendor
curl -o src/vendor/mermaid.min.js https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js
```

마지막 슬라이드의 script src 를 교체:

```html
<script src="vendor/mermaid.min.js"></script>
```

주의: `dist/slides.html` 로 정적 서빙할 때는 `vendor/` 를 dist 에 같이 복사해야 한다
(`cp -r src/vendor dist/`). PDF/PPTX 는 빌드 시점에 인라인 실행되므로 무관.
