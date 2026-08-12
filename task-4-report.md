# Task 4 report — editable PPTX evals and metadata

## Outcome

- Replaced the stale `build-pptx` file-existence evaluation with `build-editable-pptx`.
- Added `convert-marp-to-editable-pptx` for native reconstruction of an existing Marp deck.
- Added `build-flattened-pptx-explicitly` for an explicit view-only, pixel-faithful export.
- Bumped both plugin discovery surfaces to version `1.2.0` and advertised editable PowerPoint delivery while retaining the existing Marp, LaTeX, Mermaid, footnote, NAVER/네이버, CSS/design-guide, Claude Code, and Codex positioning.

## TDD evidence

### RED

After adding the metadata/eval contract tests and before changing production JSON:

- `test_plugin_metadata_advertises_editable_powerpoint_at_version_1_2_0` failed because `plugin.json` was still `1.1.0`.
- `test_pptx_evals_cover_editable_defaults_conversion_and_explicit_flattening` failed because the corpus still contained only `build-pptx` and none of the three required eval names.
- Result: 14 tests run, 2 expected failures.

### GREEN

After updating the eval corpus and manifests:

- Focused/full unittest module: 14 tests passed, 0 failures.
- All three edited JSON files parse successfully with `python3 -m json.tool`.
- `git diff --check` passes.

## Eval contract coverage

The two editable scenarios now require:

- native editable text, table/chart, shape, and connector objects;
- no full-slide flattening of information-bearing content;
- OOXML inspection with `inspect_editability.py --require-editable`;
- one message per slide, concise visible copy, and detailed evidence/sources in speaker notes;
- semantic visual selection for schedules, communication flows, trends, distributions, composition, comparisons, and decisions;
- appropriately sized charts and full-size rendering of every slide;
- iterative repair of overlap, bounds invasion, clipping, title wrapping, severe shrink, excessive whitespace, and undersized charts.

The explicit flattened scenario permits `marp --pptx` only because the prompt says the file is view-only and need not be edited. It requires disclosure that the result is image-based and its contents are not individually editable, plus every-slide visual QA.

## Environment and scope

- Python detection: no project `.venv` and no `pyproject.toml`; used system `python3` according to repository instructions.
- Worktree: existing linked worktree on `feat/editable-pptx-guidance`; no additional worktree created.
- No HTML/PDF behavior or Task 3 guidance was modified.
- Python cache directories created by tests were removed before commit.

## Concerns

- The eval assertions define objective delivery checks but do not execute full agent benchmark runs; those remain Task 5 of the implementation plan.
