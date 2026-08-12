# Claude Code용 PptxGenJS 경로

Claude Code에서 편집형 PPTX를 요청받으면 `PptxGenJS`로 Marp의 콘텐츠와 디자인 토큰을
네이티브 PowerPoint 객체로 재구성한다. HTML 화면 캡처나 `marp --pptx`를 편집형 결과물로
취급하지 않는다.

## 지원 조건과 설치

PptxGenJS 4.0.1은 Node.js 18 이상에서 ESM과 CommonJS를 지원한다. npm 패키지에는 OS/CPU
제한이 선언되어 있지 않아 Node.js가 동작하는 macOS, Linux, Windows에서 같은 로컬 설치
명령을 사용한다. PowerPoint나 LibreOffice는 **생성 자체에는 필요하지 않다**.

Node.js 18에서는 4.0.1의 ESM 진입점 선언과 파일 형식이 맞지 않아 직접 `import`가 실패할
수 있다. `.mjs`에서 `createRequire(import.meta.url)`로 `require("pptxgenjs")`를 호출해
패키지의 CommonJS 진입점을 명시적으로 사용한다. 저장소 smoke script가 이 경로의 예시다.

```bash
node --version
npm install --save-dev pptxgenjs@4.0.1
node -e "console.log(require.resolve('pptxgenjs'))"
```

재현 가능한 하네스는 `package.json`과 `package-lock.json`을 커밋하고 이후 설치에 `npm ci`를
사용한다. 전역 설치와 무버전 `npx` 호출은 피한다. 프록시나 사내 레지스트리 문제로 설치가
실패하면 원인을 보고하며, `marp --pptx`로 자동 폴백하지 않는다.

### 현재 보안 주의사항

2026-08-12 기준 `npm audit`은 PptxGenJS 4.0.1의 전이 의존성 `image-size@1.2.1`에 ICNS
무한 루프([GHSA-w3rx-r6r6-pgpr](https://github.com/advisories/GHSA-w3rx-r6r6-pgpr))와
JXL/HEIF 무한 루프([GHSA-5p2g-fcmc-qvqq](https://github.com/advisories/GHSA-5p2g-fcmc-qvqq))
DoS 위험을 보고한다. 현재 npm registry에는 이를 해결한 호환 버전이 없으므로 다음을 지킨다.

- 비신뢰 사용자에게 받은 ICNS/JXL/HEIF 이미지를 PPTX 생성 입력으로 직접 처리하지 않는다.
- 신뢰한 PNG/JPEG/SVG 자산만 사용하고 입력 크기·개수를 제한한다.
- CI에서 `npm audit` 결과를 기록하고, 수정 버전이 나오면 lockfile과 이 고지를 갱신한다.
- `npm audit fix --force`로 PptxGenJS를 오래된 비호환 버전으로 낮추지 않는다.

## 네이티브 생성 계약

- `addText`, `addTable`, `addChart`, `addShape`와 커넥터를 의미에 맞게 사용한다.
- 사진·로고·질감 외의 정보성 콘텐츠를 전체 슬라이드 이미지로 만들지 않는다.
- 화면 문구는 짧게 유지하고 근거·수치·출처·발표 스크립트는 `addNotes`로 발표자 노트에
  보존한다.
- 덱의 공통 테마, 좌표계, 안전 여백, 제목 영역을 헬퍼로 고정하되 각 슬라이드의 핵심 시각은
  콘텐츠 의미에 맞게 구성한다.
- 간트·순차 흐름·차트·표의 라벨은 실제 렌더에서 읽을 수 있는 크기로 유지한다.

## 검증

1. `inspect_editability.py --require-editable`로 OOXML 네이티브 객체와 image-only 슬라이드가
   없는지 검사한다.
2. LibreOffice Impress 또는 PowerPoint로 모든 슬라이드를 렌더한다. LibreOffice는 생성
   의존성이 아니라 교차 플랫폼 시각 QA용 선택 사항이다.
3. 겹침, 경계 침범, 잘림, 제목 줄바꿈, 심한 축소, 과도한 빈 공간과 작은 차트를 수정한다.
4. 구조 검사와 모든 슬라이드 렌더 검사를 다시 실행한다.

## 설치 시간과 자원 측정

PptxGenJS는 설치 시간·CPU·메모리의 공식 보장값을 제공하지 않는다. 네트워크, npm 캐시,
이미지 수와 해상도, 차트 수에 따라 달라지므로 고정 수치를 가이드의 요구사항으로 쓰지 말고
실행 환경에서 측정한다.

- 설치: cold/warm cache를 나누어 `npm ci` 경과 시간과 설치 전후 디스크 사용량 기록
- 생성: 5장 smoke와 실제 규모 덱의 경과 시간, 최대 RSS, 출력 파일 크기 기록
- 렌더: LibreOffice 경과 시간, 최대 RSS, 폰트 대체 경고와 페이지별 이미지 크기 기록
- 한국어: macOS/Linux/Windows 각각에서 대체 폰트와 줄바꿈 차이를 렌더로 확인

저장소의 `marp-slides-pptxgenjs-smoke` workflow는 Node.js 18에서 macOS, Ubuntu, Windows의
설치와 네이티브 텍스트·표·차트·발표자 노트 생성을 최소 검증한다. 실제 운영 하네스에는 같은
매트릭스에 Node.js 20/22와 대표 30장 덱 벤치마크를 추가한다.

공식 참고: [Integration](https://gitbrent.github.io/PptxGenJS/docs/integration/),
[Speaker Notes](https://gitbrent.github.io/PptxGenJS/docs/speaker-notes/),
[Charts](https://gitbrent.github.io/PptxGenJS/docs/api-charts.html),
[Tables](https://gitbrent.github.io/PptxGenJS/docs/api-tables/).
