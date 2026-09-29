"""Contract tests for the narration pipeline helpers (script -> wav pairing -> mp4 segments)."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


TTS = load("tts")
MAKE_VIDEO = load("make_video")


class NarrationScriptTests(unittest.TestCase):
    def test_sections_map_numbered_headings_to_slide_numbers_and_join_paragraphs(self) -> None:
        text = (
            "# 제목\n\n서문은 무시\n\n"
            "## 1. 인트로\n\n첫 문단.\n둘째 줄.\n\n둘째 문단.\n\n"
            "## 3. 결론\n\n끝.\n"
        )
        self.assertEqual(TTS.sections(text), [(1, "첫 문단.\n둘째 줄. 둘째 문단."), (3, "끝.")])

    def test_sections_ignore_unnumbered_headings(self) -> None:
        self.assertEqual(TTS.sections("## 참고\n\n본문\n"), [])
        self.assertEqual(TTS.sections("## 2 제목\n\n본문\n"), [])


class SlideAudioPairingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pngs = [Path(f"dist/slide.{i:03d}.png") for i in (1, 2, 3)]
        self.wavs = {i: Path(f"audio/{i:02d}.wav") for i in (1, 2, 3)}

    def test_exact_match_pairs_every_slide(self) -> None:
        pairs = MAKE_VIDEO.pair_slides(self.pngs, self.wavs)
        self.assertEqual([(i, w) for i, _, w in pairs], [(1, self.wavs[1]), (2, self.wavs[2]), (3, self.wavs[3])])

    def test_missing_narration_stops_unless_silent_is_allowed(self) -> None:
        del self.wavs[2]
        with self.assertRaisesRegex(SystemExit, r"\[2\]"):
            MAKE_VIDEO.pair_slides(self.pngs, self.wavs)
        pairs = MAKE_VIDEO.pair_slides(self.pngs, self.wavs, allow_silent=True)
        self.assertEqual([w for _, _, w in pairs], [self.wavs[1], None, self.wavs[3]])

    def test_stray_narration_number_stops_even_with_silent_allowed(self) -> None:
        self.wavs[4] = Path("audio/04.wav")
        for allow_silent in (False, True):
            with self.subTest(allow_silent=allow_silent), self.assertRaisesRegex(SystemExit, r"\[4\]"):
                MAKE_VIDEO.pair_slides(self.pngs, self.wavs, allow_silent=allow_silent)

    def test_no_slides_is_an_error(self) -> None:
        with self.assertRaisesRegex(SystemExit, "PNG 없음"):
            MAKE_VIDEO.pair_slides([], {})


if __name__ == "__main__":
    unittest.main()
