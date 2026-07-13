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
  /* --- larger font + vertical balance --- */
  section:not(.lead):not(.highlight) {
    padding: 88px 60px 52px 60px; font-size: 1.15em;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;   /* vertical centering — fill the slide */
    align-items: stretch !important;
  }
  section p { margin: 0.5em 0; line-height: 1.55; }
  section ul, section ol { margin: 0.45em 0; padding-left: 1.15em; }
  section li { line-height: 1.55; margin: 0.3em 0; }
  /* --- table density (prevent PDF clipping) --- */
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
 (Only for decks describing a codebase) Pin the commit this deck describes.
 To refresh:  git rev-parse --short HEAD  &&  git log -1 --format=%cd --date=short
 Use the commit of the *described code*, not the docs-branch merge commit.
==============================================================================
-->

<!-- _class: lead -->

# Presentation Title

## One-sentence subtitle — what it does

### Team / Project · Issue ID

<div class="footnote">

Project · Repository URL · Code baseline {{sha}} ({{YYYY-MM-DD}})

</div>

---

# Agenda

1. **One-slide summary** — what we are building
2. **Motivation** — why it matters
3. **Key concepts** — terms and structure
4. **Architecture overview**
5. **Pipeline / implementation details**
6. **Current status & roadmap**

---

<!-- _class: highlight -->

# One-slide summary

## The single sentence the audience should remember

**What we build** — one-paragraph summary

- **Before**: current approach and its limits
- **Ours**: what changes

**Expected impact**

- Impact 1
- Impact 2

---

# Motivation — side-by-side contrast (problem / solution)

<div class="cols">
<div>

### Today (problem)

<pre class="mermaid">
graph TD
A["Input"] --> B["Same thing"]
A --> C["Similar thing"]
</pre>

One or two sentences describing the problem.

</div>
<div>

### What we propose (solution)

<pre class="mermaid">
graph TD
A["Input"] --> B["Domain 1"]
A --> C["Domain 2"]
A --> D["Domain 3"]
</pre>

One or two sentences describing the solution. **Bold the key terms**.

</div>
</div>

---

# Key concepts — pill tags + card takeaway

Concept paragraph. Use <span class="pill">tag · side label</span> as pills.

<div class="cols">
<div>

### Concept A <span class="pill">trait summary</span>

**① Step** — description
**② Step** — description

</div>
<div>

### Concept B <span class="pill">trait summary</span>

**① Step** — description
**② Step** — description

</div>
</div>

<div class="card">

Put the slide's **single key takeaway** in a card — the left accent border draws the eye.

</div>

---

# Architecture overview — mermaid flowchart

<pre class="mermaid">
flowchart LR
subgraph OFF["① Batch"]
direction TB
O1["Input"] --> O2["Process"]
end
O2 --> DB[("Store")]
DB --> ON["② Serving"]
</pre>

- 2–3 key bullets below the diagram
- **Bold** the numbers (e.g. ~ms, ~70x)

<p class="muted">Side notes and captions go in muted — keep the main flow clean</p>

---

<!-- _class: compact -->

# Dense slide — use compact when there are 2+ tables

| Item | Value A | Value B |
|------|--------:|--------:|
| Row 1 | 1 | 2 |
| Row 2 | 3 | 4 |

<div class="cols">
<div>

<pre class="mermaid tall">
sequenceDiagram
    autonumber
    participant A as Caller
    participant B as Server
    A->>B: Request
    B-->>A: Response
</pre>

</div>
<div>

- Put sequence diagrams in one `.cols` column with the `tall` class for vertical room
- Put explanations or tables in the other column

</div>
</div>

<p class="muted">Reproduction info — measurement setup, code baseline sha, date — goes in a muted caption</p>

---

# Current status & roadmap

<div class="cols">
<div>

### ✅ Done

- Item — one-line evidence
- Item — one-line evidence

</div>
<div>

### 🚀 Next (in order)

1. Task 1
2. Task 2

<div class="card">
One card paragraph: where we are + the very next step.
</div>

</div>
</div>

---

<!-- _class: lead -->

# Thank You

## Project — one-line intro

### Contact · Details: README.md / Issue ID

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
