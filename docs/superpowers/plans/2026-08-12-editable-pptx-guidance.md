# Editable PPTX Guidance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `marp-slides` route ordinary PPTX requests to native editable PowerPoint generation, verify editability structurally and visually, and preserve image-based Marp PPTX only as an explicit view-only fallback.

**Architecture:** Keep Marp as the source and HTML/PDF renderer, but split PPTX delivery into an editable-native route and an explicit flattened route. Put decision and contract guidance in `SKILL.md`, implementation detail in one reference, and deterministic OOXML checks in a dependency-free Python script covered by synthetic package tests.

**Tech Stack:** Markdown skill guidance, Python 3 standard library (`argparse`, `json`, `zipfile`, `xml.etree.ElementTree`), OOXML/PPTX, existing JSON eval corpus, GitHub CLI.

## Global Constraints

- PPTX defaults to native editable text, table, chart, shape, and connector objects.
- Marp `--pptx` is allowed only when the user explicitly requests a view-only, non-editable, or pixel-faithful export.
- HTML/PDF/preview behavior remains unchanged.
- Codex editable generation uses `presentations:Presentations` and `@oai/artifact-tool`.
- A missing native presentation capability must be disclosed; do not silently fall back to flattened PPTX.
- Python commands follow the environment detection order `.venv` → matching conda env from `pyproject.toml` → `python3`.
- No project-specific Dear Hair content enters the reusable skill.

---

### Task 1: Capture the failing baseline

**Files:**
- Create outside git: `/Users/user/workspace/private/yoo-marketplace/marp-slides-workspace/iteration-0/<eval-name>/old_skill/outputs/response.txt`
- Create outside git: `/Users/user/workspace/private/yoo-marketplace/marp-slides-workspace/iteration-0/<eval-name>/eval_metadata.json`
- Create outside git: `/Users/user/workspace/private/yoo-marketplace/marp-slides-workspace/iteration-0/baseline-analysis.txt`

**Interfaces:**
- Consumes: current `plugins/skills/marp-slides/SKILL.md` at commit `f201e8c`.
- Produces: exact baseline routing decisions and rationalizations for three pressure scenarios.

- [ ] **Step 1: Snapshot the current skill**

Copy the whole existing skill directory to `/Users/user/workspace/private/yoo-marketplace/marp-slides-workspace/skill-snapshot/` before editing it.

- [ ] **Step 2: Run three old-skill scenarios in parallel**

Use one isolated agent per prompt and require a written response describing the chosen command/tool and how editability would be verified:

```text
pptx로 빨리 빌드해줘. 나중에 문구와 표를 수정할 거야.
이 Marp 덱을 PowerPoint로 변환하고 차트 수치를 수정 가능하게 해줘.
픽셀 그대로면 되고 수정은 안 해도 돼. PPTX로 내보내줘.
```

- [ ] **Step 3: Record RED evidence**

Write `baseline-analysis.txt` with one row per scenario: selected route, whether `marp --pptx` was used, whether native editability was promised, and whether an OOXML/visual check was proposed. RED is valid when at least one editable scenario incorrectly uses flattened Marp PPTX or omits structural validation.

- [ ] **Step 4: Commit nothing**

The eval workspace remains a sibling of the skill and is excluded from the plugin PR.

### Task 2: Build the deterministic editability inspector with TDD

**Files:**
- Create: `plugins/skills/marp-slides/scripts/inspect_editability.py`
- Create: `plugins/skills/marp-slides/scripts/tests/test_inspect_editability.py`

**Interfaces:**
- Consumes: `inspect_editability.py <deck.pptx> [--json PATH] [--require-editable]`.
- Produces: JSON `{ "slides": [...], "totals": {...}, "editable": bool, "failures": [...] }` and exit code `0` for success, `1` for contract failure, `2` for invalid input.

- [ ] **Step 1: Write failing tests using synthetic PPTX ZIPs**

Define `make_pptx(path, slide_xml, rels_xml=None)` and tests for:

```python
def test_text_and_shape_slide_is_editable(tmp_path): ...
def test_full_slide_image_only_is_rejected(tmp_path): ...
def test_native_table_and_chart_are_counted(tmp_path): ...
def test_invalid_zip_returns_input_error(tmp_path): ...
```

The synthetic XML must include `p:sp`, `a:t`, `a:tbl`, `c:chart`, and `p:pic` cases without third-party packages.

- [ ] **Step 2: Run the tests and verify RED**

Run environment detection, then:

```bash
python3 -m unittest plugins.skills.marp-slides.scripts.tests.test_inspect_editability -v
```

Expected: FAIL because `inspect_editability.py` does not exist.

- [ ] **Step 3: Implement minimal OOXML inspection**

Parse `ppt/slides/slide*.xml`; count `p:sp`, `a:t`, `a:tbl`, `c:chart`, `p:pic`, `p:cxnSp`, and flag slides where `p:pic == 1` and every editable object count is zero. Sort slide filenames numerically and emit stable JSON.

- [ ] **Step 4: Run focused tests and verify GREEN**

Use the same `unittest` command. Expected: four tests pass with no warnings.

- [ ] **Step 5: Commit**

```bash
git add plugins/skills/marp-slides/scripts
git commit -m "feat(marp-slides): inspect PPTX editability"
```

### Task 3: Rewrite PPTX routing and detailed guidance

**Files:**
- Modify: `plugins/skills/marp-slides/SKILL.md`
- Create: `plugins/skills/marp-slides/references/editable-pptx.md`

**Interfaces:**
- Consumes: the baseline failures from Task 1 and inspector CLI from Task 2.
- Produces: an unambiguous editable/default vs flattened/explicit routing contract.

- [ ] **Step 1: Add a failing documentation contract test**

Extend `test_inspect_editability.py` to read `SKILL.md` and assert the document includes all of:

```python
required = [
    "PPTX는 기본적으로 편집 가능한 네이티브 객체",
    "marp --pptx",
    "presentations:Presentations",
    "inspect_editability.py",
    "비편집형",
]
```

Also assert that the quick-start path does not recommend `npm run build:pptx` as the default PPTX route.

- [ ] **Step 2: Run tests and verify RED**

Expected: documentation contract test fails against the old skill.

- [ ] **Step 3: Update `SKILL.md`**

Add a compact output-routing table, an editable deliverable contract, a generation/verification loop, and an explicit flattened exception. Change `build:all` so it does not imply that image-based PPTX is the standard deliverable; name the flattened script `build:pptx:flattened`.

- [ ] **Step 4: Add `references/editable-pptx.md`**

Document semantic mappings for headings, paragraphs, tables, charts, diagrams, images, notes/sources, and the Codex route using `presentations:Presentations` plus `@oai/artifact-tool`. Include the required sequence: inventory → native reconstruction → structural inspection → render every slide → repair → re-run checks.

- [ ] **Step 5: Run tests and verify GREEN**

Expected: all inspector and documentation contract tests pass.

- [ ] **Step 6: Commit**

```bash
git add plugins/skills/marp-slides/SKILL.md plugins/skills/marp-slides/references/editable-pptx.md plugins/skills/marp-slides/scripts/tests/test_inspect_editability.py
git commit -m "docs(marp-slides): default PPTX output to editable objects"
```

### Task 4: Strengthen evals and plugin metadata

**Files:**
- Modify: `plugins/skills/marp-slides/evals/evals.json`
- Modify: `plugins/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: the routing contract from Task 3.
- Produces: evaluable prompts/assertions and marketplace version `1.2.0`.

- [ ] **Step 1: Write a failing metadata/eval test**

Add tests asserting:

```python
plugin["version"] == "1.2.0"
"editable" in plugin["description"].lower()
```

and eval names include `build-editable-pptx`, `convert-marp-to-editable-pptx`, and `build-flattened-pptx-explicitly`.

- [ ] **Step 2: Run tests and verify RED**

Expected: version and eval-name assertions fail.

- [ ] **Step 3: Update evaluations**

Replace the old file-existence-only `build-pptx` expectation. Editable cases must assert native text plus table/chart objects, structure inspection, and rendered-slide QA. The explicit view-only case must assert that Marp flattened export is allowed and its editability limitation is disclosed.

- [ ] **Step 4: Bump metadata**

Set plugin version to `1.2.0`; mention editable PowerPoint in both plugin and marketplace descriptions without removing existing Marp/LaTeX/Mermaid/theme keywords.

- [ ] **Step 5: Run tests and verify GREEN**

Expected: the full unittest module passes.

- [ ] **Step 6: Commit**

```bash
git add plugins/skills/marp-slides/evals/evals.json plugins/.claude-plugin/plugin.json .claude-plugin/marketplace.json plugins/skills/marp-slides/scripts/tests/test_inspect_editability.py
git commit -m "test(marp-slides): enforce editable PPTX delivery"
```

### Task 5: Run GREEN/REFACTOR agent evaluations

**Files:**
- Create outside git: `/Users/user/workspace/private/yoo-marketplace/marp-slides-workspace/iteration-1/<eval-name>/with_skill/outputs/response.txt`
- Create outside git: `/Users/user/workspace/private/yoo-marketplace/marp-slides-workspace/iteration-1/<eval-name>/grading.json`
- Create outside git: `/Users/user/workspace/private/yoo-marketplace/marp-slides-workspace/iteration-1/benchmark.json`
- Create outside git: `/Users/user/workspace/private/yoo-marketplace/marp-slides-workspace/iteration-1/review.html`

**Interfaces:**
- Consumes: updated skill and the same three Task 1 prompts.
- Produces: graded comparison against the old-skill baseline.

- [ ] **Step 1: Run three updated-skill scenarios in parallel**

Require each agent to use the updated skill and save the chosen route, commands, editability proof, and fallback disclosure.

- [ ] **Step 2: Grade assertions**

For editable prompts: pass only if the native route is selected, `marp --pptx` is rejected as the final editable route, and structure plus render checks are specified. For the view-only prompt: pass only if flattened export is selected and limitations are stated.

- [ ] **Step 3: Aggregate benchmark and generate static review**

After Python environment detection, run the skill-creator aggregation module and `eval-viewer/generate_review.py --static .../review.html` with the baseline workspace supplied as previous results.

- [ ] **Step 4: Analyze failures and refactor guidance**

If an editable prompt still selects flattened export or skips structural checking, update the minimal relevant guidance and rerun all three prompts into `iteration-2`.

- [ ] **Step 5: Commit any refactor**

```bash
git add plugins/skills/marp-slides
git commit -m "refactor(marp-slides): close editable PPTX routing gaps"
```

### Task 6: Create and validate the Dear Hair editable deck

**Files:**
- Create in mkt repo: `slides/dear-hair/build-editable.mjs`
- Create in mkt repo: `slides/dear-hair/dist/dear-hair-editable.pptx`
- Create outside final output: `slides/dear-hair/.editable-pptx-work/`

**Interfaces:**
- Consumes: `slides/dear-hair/src/slides.md`, `themes/brand-launch/brand-launch.css`, and the updated editable PPTX guidance.
- Produces: a 16:9 PPTX whose information-bearing content is native and editable.

- [ ] **Step 1: Inventory all source slides**

Parse the Marp slide boundaries, titles, paragraphs, lists, tables, callouts, citations, and section classes. Record a 30-slide mapping in a temporary text file.

- [ ] **Step 2: Implement native slide reconstruction**

Use `presentations:Presentations` with `@oai/artifact-tool` from an ES module. Recreate title/body/table/chart/shape objects and retain raster images only for photos, logos, or decorative textures.

- [ ] **Step 3: Export and inspect structure**

Run the merged `inspect_editability.py --require-editable` against the final PPTX and save its JSON report under the temporary work directory.

- [ ] **Step 4: Render and inspect every slide**

Use the Presentations container render helper, inspect each full-size PNG, run the overflow detector, and repair clipping, overlap, or unexpected title wrapping.

- [ ] **Step 5: Run final regression checks**

Verify 30 slides, zero flattened information-only slides, editable text on every non-divider slide, expected native tables/charts, no unresolved placeholders, and a clean render.

### Task 7: Self-review, PR, CI, and merge

**Files:**
- Modify only if review finds issues: files from Tasks 2–4.

**Interfaces:**
- Consumes: clean feature branch, passing tests, benchmark, and Dear Hair integration result.
- Produces: merged PR on `main`.

- [ ] **Step 1: Run verification from a clean status**

Run Python environment detection, the full unittest module, JSON parsing for both manifests/evals, `git diff --check`, and `git status --short`.

- [ ] **Step 2: Review against the design**

Check every design completion condition and inspect the full diff for unrelated changes, stale `build:pptx` claims, and inconsistent version strings.

- [ ] **Step 3: Push and open PR**

```bash
git push -u origin feat/editable-pptx-guidance
gh pr create --base main --head feat/editable-pptx-guidance --title "marp-slides: generate editable PPTX by default" --body-file <prepared-pr-body>
```

- [ ] **Step 4: Inspect CI and PR diff**

Use `gh pr checks --watch` and `gh pr diff`; address failures on the feature branch and rerun verification.

- [ ] **Step 5: Merge only after green checks**

```bash
gh pr merge --squash --delete-branch
```

- [ ] **Step 6: Confirm merged state**

Verify the PR reports `MERGED`, `origin/main` contains version `1.2.0`, and the final Dear Hair PPTX remains available in the mkt workspace.
