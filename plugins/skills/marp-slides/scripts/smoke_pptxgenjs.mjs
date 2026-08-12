import { createRequire } from "node:module";

// PptxGenJS 4.0.1 advertises an ESM entry whose .js file lacks a package
// `type: module` marker. Select its supported CommonJS export explicitly so
// Node 18 behaves consistently on macOS, Linux, and Windows.
const require = createRequire(import.meta.url);
const pptxgen = require("pptxgenjs");

const output = process.argv[2] ?? "pptxgenjs-smoke.pptx";
const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "marp-slides smoke";
pptx.subject = "Cross-platform native editability smoke test";
pptx.title = "PptxGenJS native object smoke test";

const slide = pptx.addSlide();
slide.addText("Native editable objects", {
  x: 0.6,
  y: 0.35,
  w: 12.1,
  h: 0.5,
  fontSize: 24,
  bold: true,
  color: "111827",
});
slide.addTable(
  [
    ["Object", "Editable"],
    ["Text", "Yes"],
    ["Chart", "Yes"],
  ],
  { x: 0.65, y: 1.2, w: 4.2, h: 2.1, fontSize: 14, border: { color: "CBD5E1", pt: 1 } },
);
slide.addChart(
  pptx.ChartType.bar,
  [{ name: "Objects", labels: ["Text", "Table", "Chart"], values: [1, 1, 1] }],
  {
    x: 5.2,
    y: 1.15,
    w: 7.2,
    h: 4.8,
    showLegend: false,
    showTitle: true,
    title: "Native chart",
    catAxisLabelFontSize: 12,
    valAxisLabelFontSize: 12,
  },
);
slide.addShape(pptx.ShapeType.line, {
  x: 1.1,
  y: 3.8,
  w: 3.1,
  h: 0,
  line: { color: "2563EB", width: 2, beginArrowType: "none", endArrowType: "triangle" },
});
slide.addNotes("Smoke test speaker notes: native text, table, and chart must remain editable.");

await pptx.writeFile({ fileName: output });
console.log(output);
