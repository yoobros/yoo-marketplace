# 나레이션 영상 만들기 (슬라이드 PNG + TTS → mp4)

덱을 **한 명의 화자**가 읽는 발표 영상으로 만드는 절차. 산출물은 `marp/video/<이름>.mp4`.
`marp/` 안의 영상·오디오는 git 에 넣지 않는다 (`.gitignore` 에 `video/` 추가).

## 0. 구조

```
marp/
├── script/narration.md      # 대본 — `## N. 제목` 절 = 슬라이드 N (assets/narration-template.md 복사)
├── dist/slide.001.png …     # marp --images png
└── video/
    ├── audio/01.wav …       # scripts/tts.py
    ├── seg/                 # 중간 산출 (슬라이드별 mp4)
    └── <이름>.mp4           # scripts/make_video.py
```

## 1. 대본 작성 규칙

- 절 하나 = 슬라이드 한 장. **절 번호 = PNG 번호** (표지가 1). 장수와 절 수가 다르면 `make_video.py` 가 멈춘다 —
  이 검사를 끄지 말 것. 어긋나면 이후 모든 장의 소리가 한 장씩 밀린다.
- 슬라이드 글을 읽지 말고, 그 장의 메시지 하나를 40~70초(한국어 250~450자)로 말한다. 10장이면 8~12분.
- 수식이 있는 장은 **기호마다 뜻을 말로 풀어** 준다 (슬라이드에도 기호 표를 둔다).
- 숫자·약어는 한글로 풀어 쓴다 (0.45 → 영점사오, GRPO → 지 알 피 오). TTS 가 영문 약어를 제멋대로 읽는 것을 막는다.
- 지난 버전과의 차이·고친 결함은 말하지 않는다 — 최종 상태만.

## 2. TTS — 화자 한 명 고정

1. 서버 준비 (사내 k8s TTS: Supertonic 프리셋 10종 `F1~F5/M1~M5`, CPU. voxcpm 은 GPU·프리셋 6종):
   `kubectl --context <ctx> port-forward svc/tts-supertonic 18081:8080`
2. 화자 목록: `curl localhost:18081/v1/voices`
3. 합성: `python3 <스킬디렉토리>/scripts/tts.py --base http://127.0.0.1:18081 --speaker F1`
   - 화자 인자는 **전 구간 하나**. "voice-N" 처럼 seed 기반 화자는 절마다 음색이 달라질 수 있으니
     프리셋 화자(Supertonic) 를 쓴다.
   - 있는 wav 는 건너뛴다. 대본을 고친 절만 `video/audio/NN.wav` 를 지우고 다시 돌린다.
   - 미치환 `{{...}}` 가 있으면 멈춘다.

## 3. 슬라이드 PNG

```bash
cd marp && CHROME_PATH=<chrome> npx marp src/slides.md --html --theme-set themes/<테마>/<테마>.css --images png --output dist/slide.png
```

- Chrome 이 없으면 `npx puppeteer browsers install chrome` 후 그 경로를 `CHROME_PATH` 로.
- **marp 가 간헐적으로 멈춘다** (mermaid CDN 로드 대기). `timeout 240` 으로 감싸고 PNG 장수가 맞을 때까지
  2~3회 재시도한다. 재시도 전 남은 `chrome` 프로세스를 정리한다.
- PNG 장수 = 대본 절 수 인지 확인 (`ls dist/slide.*.png | wc -l`).

## 4. 합치기

```bash
python3 <스킬디렉토리>/scripts/make_video.py --png marp/dist --wav marp/video/audio --out marp/video/<이름>.mp4
```

- ffmpeg: 시스템에 없으면 `pip install imageio-ffmpeg` (번들 바이너리 자동 사용).
- 세그먼트 길이 = wav + 0.6초. 전체 길이와 세그먼트별 길이를 결과 보고에 적는다.

## 5. 검수 체크리스트 (전달 전)

- [ ] 절 수 = PNG 장수 = wav 수
- [ ] 화자 한 명 (meta.json 의 speaker 하나)
- [ ] 대본에 `{{` 없음, 슬라이드에 `{{` 없음
- [ ] 슬라이드 9~10장 PNG 를 눈으로 확인 (표 잘림·다이어그램 크기)
- [ ] 총 길이가 목표(보통 10분 안팎) 안인가 — 길면 대본을 줄인다, 속도(`--speed`)로 때우지 않는다

## 6. 갱신

슬라이드 한 장을 고치면: 그 장의 대본 절 수정 → 해당 wav 삭제 → `tts.py` → PNG 재렌더 → `make_video.py`.
전부 다시 만들 필요 없다.
