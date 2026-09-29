#!/usr/bin/env python3
"""나레이션 대본(script/narration.md) → 슬라이드별 wav.

대본 형식: `## N. 제목` 절 하나 = 슬라이드 N 하나 (N 은 dist/slide.0NN.png 의 번호와 같아야 한다).
화자는 **한 명으로 고정** — 슬라이드마다 목소리가 바뀌면 영상이 어색하다. 절이 바뀌어도 speaker 인자를
바꾸지 않는다. 이미 있는 wav 는 건너뛴다 (대본을 고친 절만 wav 를 지우고 다시 실행).

TTS 서버는 `POST {base}/tts` 에 {"text","speaker","speed","language","format"} 를 받는 것을 가정한다
(Supertonic·voxcpm 계열 사내 서버). 다른 API 면 `render()` 만 바꾼다.

    python3 <스킬디렉토리>/scripts/tts.py --base http://127.0.0.1:18081 --speaker F1 [--speed 1.0] [--script marp/script/narration.md]
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
from pathlib import Path


def sections(text: str) -> list[tuple[int, str]]:
    parts = re.split(r"^## (\d+)\. .*$", text, flags=re.M)[1:]
    out = []
    for i in range(0, len(parts), 2):
        body = " ".join(p.strip() for p in parts[i + 1].strip().split("\n\n") if p.strip())
        out.append((int(parts[i]), body))
    return out


def render(base: str, text: str, speaker: str, speed: float, language: str) -> bytes:
    req = urllib.request.Request(f"{base}/tts", data=json.dumps({"text": text, "speaker": speaker, "speed": speed,
                                 "language": language, "format": "wav"}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=900) as r:
        return r.read()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:18081")
    ap.add_argument("--speaker", required=True, help="고정 화자 id (GET {base}/v1/voices 로 목록)")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--language", default="ko")
    ap.add_argument("--script", default="marp/script/narration.md")
    ap.add_argument("--out", default="marp/video/audio")
    args = ap.parse_args()

    secs = sections(Path(args.script).read_text(encoding="utf-8"))
    if not secs:
        raise SystemExit("대본에 `## N. 제목` 절이 없다")
    left = [n for n, b in secs if "{{" in b]
    if left:
        raise SystemExit(f"미치환 placeholder 가 있는 절: {left}")
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    meta_path = out / "meta.json"
    meta: dict[str, dict] = {}
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8")).get("sections", {})
    for n, body in secs:
        f = out / f"{n:02d}.wav"
        if f.exists():
            continue
        t = time.time()
        f.write_bytes(render(args.base, body, args.speaker, args.speed, args.language))
        meta[str(n)] = {"chars": len(body), "elapsed": round(time.time() - t, 1)}
        print(f"slide {n:02d}: {len(body)}자 (걸림 {meta[str(n)]['elapsed']}s)", flush=True)
    meta_path.write_text(json.dumps({"speaker": args.speaker, "speed": args.speed, "sections": meta},
                                              ensure_ascii=False, indent=1))
    print(f"TTS_DONE · 절 {len(secs)} · 화자 {args.speaker}")


if __name__ == "__main__":
    main()
