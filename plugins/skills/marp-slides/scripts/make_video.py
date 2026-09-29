#!/usr/bin/env python3
"""슬라이드 PNG + 나레이션 wav → mp4.

슬라이드마다 정지 화면에 해당 wav 를 얹은 세그먼트를 만들고 이어 붙인다 (오디오 끝에 0.6초 여유).
**PNG 장수와 wav 번호 집합이 1:1 로 일치하지 않으면 멈춘다** — 여기서 어긋나면 이후 모든 슬라이드의
소리가 한 장씩 밀리는 싱크 사고가 난다. 나레이션 없는 장을 두려면 `--allow-silent` 로 3초 무음 처리.

ffmpeg 는 시스템 ffmpeg 가 있으면 그것, 없으면 `pip install imageio-ffmpeg` 의 번들 바이너리를 쓴다.

    python3 <스킬디렉토리>/scripts/make_video.py [--png marp/dist] [--wav marp/video/audio] [--out marp/video/slides.mp4]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def ffmpeg_exe() -> str:
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise SystemExit("ffmpeg 가 없다 — 시스템 설치 또는 `pip install imageio-ffmpeg`")


def pair_slides(pngs: list[Path], wavs: dict[int, Path], allow_silent: bool = False) -> list[tuple[int, Path, Path | None]]:
    """슬라이드 번호 1..N 에 wav 를 붙인다. 번호가 어긋나면 SystemExit — 밀린 싱크로 영상을 만들지 않는다."""
    if not pngs:
        raise SystemExit("PNG 없음 — `npx marp src/slides.md --html --theme-set … --images png --output dist/slide.png`")
    expect = set(range(1, len(pngs) + 1))
    extra = sorted(set(wavs) - expect)
    if extra:
        raise SystemExit(f"슬라이드는 {len(pngs)}장인데 나레이션 {extra}번이 남는다 — 대본 절 번호를 PNG 번호에 맞춘다")
    missing = sorted(expect - set(wavs))
    if missing and not allow_silent:
        raise SystemExit(f"슬라이드 {missing}번 나레이션이 없다 — 대본에 절을 추가하거나 `--allow-silent` 로 무음 처리")
    return [(i, png, wavs.get(i)) for i, png in enumerate(pngs, 1)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", default="marp/dist", help="marp --images png 산출 (slide.001.png …)")
    ap.add_argument("--wav", default="marp/video/audio")
    ap.add_argument("--out", default="marp/video/slides.mp4")
    ap.add_argument("--pad", type=float, default=0.6)
    ap.add_argument("--allow-silent", action="store_true")
    args = ap.parse_args()

    ff = ffmpeg_exe()
    pngs = sorted(Path(args.png).glob("slide.*.png"))
    wavs = {int(p.stem): p for p in Path(args.wav).glob("*.wav") if p.stem.isdigit()}
    pairs = pair_slides(pngs, wavs, args.allow_silent)
    seg_dir = Path(args.out).parent / "seg"; seg_dir.mkdir(parents=True, exist_ok=True)

    def run(*a: str) -> None:
        subprocess.run([ff, "-y", "-hide_banner", "-loglevel", "error", *a], check=True)

    segs = []
    for i, png, wav in pairs:
        seg = seg_dir / f"{i:02d}.mp4"
        if wav is None:
            run("-loop", "1", "-framerate", "24", "-i", str(png), "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", "3",
                "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(seg))
        else:
            run("-loop", "1", "-framerate", "24", "-i", str(png), "-i", str(wav), "-af", f"apad=pad_dur={args.pad}",
                "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", str(seg))
        segs.append(seg)
        print(f"seg {i:02d} ← {png.name} + {wav.name if wav else '무음'}", flush=True)
    lst = seg_dir / "list.txt"
    lst.write_text("".join(f"file '{s.resolve()}'\n" for s in segs), encoding="utf-8")
    run("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", args.out)
    info = subprocess.run([ff, "-i", args.out], capture_output=True, text=True).stderr
    dur = next((l.strip() for l in info.splitlines() if "Duration" in l), "")
    print(f"[done] {args.out} ({Path(args.out).stat().st_size / 1e6:.1f} MB) {dur}")


if __name__ == "__main__":
    main()
