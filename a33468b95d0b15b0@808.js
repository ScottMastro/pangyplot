// https://observablehq.com/@d3/color-legend@808
function _1(md){return(
md`# Color Legend

A simple legend for a [color scale](/@d3/color-schemes). Supports [continuous](/@d3/continuous-scales), [sequential](/@d3/sequential-scales), [diverging](/@d3/diverging-scales), [quantize, quantile, threshold](/@d3/quantile-quantize-and-threshold-scales) and [ordinal](/@d3/d3-scaleordinal) scales. To use:

~~~js
import {Legend, Swatches} from "@d3/color-legend"
~~~

Then call the legend function as shown below. (For ordinal scales, also consider the swatches function.)`
)}

function _2(Legend,d3){return(
Legend(d3.scaleSequential([0, 100], d3.interpolateViridis), {
  title: "Temperature (°F)"
})
)}

function _3(Legend,d3){return(
Legend(d3.scaleSequentialSqrt([0, 1], d3.interpolateTurbo), {
  title: "Speed (kts)"
})
)}

function _4(Legend,d3){return(
Legend(d3.scaleDiverging([-0.1, 0, 0.1], d3.interpolatePiYG), {
  title: "Daily change",
  tickFormat: "+%"
})
)}

function _5(Legend,d3){return(
Legend(d3.scaleDivergingSqrt([-0.1, 0, 0.1], d3.interpolateRdBu), {
  title: "Daily change",
  tickFormat: "+%"
})
)}

function _6(Legend,d3){return(
Legend(d3.scaleSequentialLog([1, 100], d3.interpolateBlues), {
  title: "Energy (joules)",
  ticks: 10
})
)}

function _7(Legend,d3){return(
Legend(d3.scaleSequentialQuantile(d3.range(100).map(() => Math.random() ** 2), d3.interpolateBlues), {
  title: "Quantile",
  tickFormat: ".2f"
})
)}

function _8(Legend,d3){return(
Legend(d3.scaleSqrt([-100, 0, 100], ["blue", "white", "red"]), {
  title: "Temperature (°C)"
})
)}

function _9(Legend,d3){return(
Legend(d3.scaleQuantize([1, 10], d3.schemePurples[9]), {
  title: "Unemployment rate (%)"
})
)}

function _10(Legend,d3){return(
Legend(d3.scaleQuantile(d3.range(1000).map(d3.randomNormal(100, 20)), d3.schemeSpectral[9]), {
  title: "Height (cm)",
  tickFormat: ".0f"
})
)}

function _11(Legend,d3){return(
Legend(d3.scaleThreshold([2.5, 3.1, 3.5, 3.9, 6, 7, 8, 9.5], d3.schemeRdBu[9]), {
  title: "Unemployment rate (%)",
  tickSize: 0
})
)}

function _12(Legend,d3){return(
Legend(d3.scaleOrdinal(["<10", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "≥80"], d3.schemeSpectral[10]), {
  title: "Age (years)",
  tickSize: 0
})
)}

function _13(md){return(
md`But wait, there’s more!

How about swatches for ordinal color scales? Both variable-width swatches and [column layout](https://developer.mozilla.org/en-US/docs/Web/CSS/columns) are supported.`
)}

function _14(Swatches,d3){return(
Swatches(d3.scaleOrdinal(["blueberries", "oranges", "apples"], d3.schemeCategory10))
)}

function _15(Swatches,d3){return(
Swatches(d3.scaleOrdinal(["Wholesale and Retail Trade", "Manufacturing", "Leisure and hospitality", "Business services", "Construction", "Education and Health", "Government", "Finance", "Self-employed", "Other"], d3.schemeTableau10), {
  columns: "180px"
})
)}

function _16(md){return(
md`---

## Implementation`
)}

function _Legend(d3){return(
function Legend(color, {
  title,
  tickSize = 6,
  width = 320, 
  height = 44 + tickSize,
  marginTop = 18,
  marginRight = 0,
  marginBottom = 16 + tickSize,
  marginLeft = 0,
  ticks = width / 64,
  tickFormat,
  tickValues
} = {}) {

  function ramp(color, n = 256) {
    const canvas = document.createElement("canvas");
    canvas.width = n;
    canvas.height = 1;
    const context = canvas.getContext("2d");
    for (let i = 0; i < n; ++i) {
      context.fillStyle = color(i / (n - 1));
      context.fillRect(i, 0, 1, 1);
    }
    return canvas;
  }

  const svg = d3.create("svg")
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [0, 0, width, height])
      .style("overflow", "visible")
      .style("display", "block");

  let tickAdjust = g => g.selectAll(".tick line").attr("y1", marginTop + marginBottom - height);
  let x;

  // Continuous
  if (color.interpolate) {
    const n = Math.min(color.domain().length, color.range().length);

    x = color.copy().rangeRound(d3.quantize(d3.interpolate(marginLeft, width - marginRight), n));

    svg.append("image")
        .attr("x", marginLeft)
        .attr("y", marginTop)
        .attr("width", width - marginLeft - marginRight)
        .attr("height", height - marginTop - marginBottom)
        .attr("preserveAspectRatio", "none")
        .attr("xlink:href", ramp(color.copy().domain(d3.quantize(d3.interpolate(0, 1), n))).toDataURL());
  }

  // Sequential
  else if (color.interpolator) {
    x = Object.assign(color.copy()
        .interpolator(d3.interpolateRound(marginLeft, width - marginRight)),
        {range() { return [marginLeft, width - marginRight]; }});

    svg.append("image")
        .attr("x", marginLeft)
        .attr("y", marginTop)
        .attr("width", width - marginLeft - marginRight)
        .attr("height", height - marginTop - marginBottom)
        .attr("preserveAspectRatio", "none")
        .attr("xlink:href", ramp(color.interpolator()).toDataURL());

    // scaleSequentialQuantile doesn’t implement ticks or tickFormat.
    if (!x.ticks) {
      if (tickValues === undefined) {
        const n = Math.round(ticks + 1);
        tickValues = d3.range(n).map(i => d3.quantile(color.domain(), i / (n - 1)));
      }
      if (typeof tickFormat !== "function") {
        tickFormat = d3.format(tickFormat === undefined ? ",f" : tickFormat);
      }
    }
  }

  // Threshold
  else if (color.invertExtent) {
    const thresholds
        = color.thresholds ? color.thresholds() // scaleQuantize
        : color.quantiles ? color.quantiles() // scaleQuantile
        : color.domain(); // scaleThreshold

    const thresholdFormat
        = tickFormat === undefined ? d => d
        : typeof tickFormat === "string" ? d3.format(tickFormat)
        : tickFormat;

    x = d3.scaleLinear()
        .domain([-1, color.range().length - 1])
        .rangeRound([marginLeft, width - marginRight]);

    svg.append("g")
      .selectAll("rect")
      .data(color.range())
      .join("rect")
        .attr("x", (d, i) => x(i - 1))
        .attr("y", marginTop)
        .attr("width", (d, i) => x(i) - x(i - 1))
        .attr("height", height - marginTop - marginBottom)
        .attr("fill", d => d);

    tickValues = d3.range(thresholds.length);
    tickFormat = i => thresholdFormat(thresholds[i], i);
  }

  // Ordinal
  else {
    x = d3.scaleBand()
        .domain(color.domain())
        .rangeRound([marginLeft, width - marginRight]);

    svg.append("g")
      .selectAll("rect")
      .data(color.domain())
      .join("rect")
        .attr("x", x)
        .attr("y", marginTop)
        .attr("width", Math.max(0, x.bandwidth() - 1))
        .attr("height", height - marginTop - marginBottom)
        .attr("fill", color);

    tickAdjust = () => {};
  }

  svg.append("g")
      .attr("transform", `translate(0,${height - marginBottom})`)
      .call(d3.axisBottom(x)
        .ticks(ticks, typeof tickFormat === "string" ? tickFormat : undefined)
        .tickFormat(typeof tickFormat === "function" ? tickFormat : undefined)
        .tickSize(tickSize)
        .tickValues(tickValues))
      .call(tickAdjust)
      .call(g => g.select(".domain").remove())
      .call(g => g.append("text")
        .attr("x", marginLeft)
        .attr("y", marginTop + marginBottom - height - 6)
        .attr("fill", "currentColor")
        .attr("text-anchor", "start")
        .attr("font-weight", "bold")
        .attr("class", "title")
        .text(title));

  return svg.node();
}
)}

function _legend(Legend){return(
function legend({color, ...options}) {
  return Legend(color, options);
}
)}

function _Swatches(d3,htl){return(
function Swatches(color, {
  columns = null,
  format,
  unknown: formatUnknown,
  swatchSize = 15,
  swatchWidth = swatchSize,
  swatchHeight = swatchSize,
  marginLeft = 0
} = {}) {
  const id = `-swatches-${Math.random().toString(16).slice(2)}`;
  const unknown = formatUnknown == null ? undefined : color.unknown();
  const unknowns = unknown == null || unknown === d3.scaleImplicit ? [] : [unknown];
  const domain = color.domain().concat(unknowns);
  if (format === undefined) format = x => x === unknown ? formatUnknown : x;

  function entity(character) {
    return `&#${character.charCodeAt(0).toString()};`;
  }

  if (columns !== null) return htl.html`<div style="display: flex; align-items: center; margin-left: ${+marginLeft}px; min-height: 33px; font: 10px sans-serif;">
  <style>

.${id}-item {
  break-inside: avoid;
  display: flex;
  align-items: center;
  padding-bottom: 1px;
}

.${id}-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: calc(100% - ${+swatchWidth}px - 0.5em);
}

.${id}-swatch {
  width: ${+swatchWidth}px;
  height: ${+swatchHeight}px;
  margin: 0 0.5em 0 0;
}

  </style>
  <div style=${{width: "100%", columns}}>${domain.map(value => {
    const label = `${format(value)}`;
    return htl.html`<div class=${id}-item>
      <div class=${id}-swatch style=${{background: color(value)}}></div>
      <div class=${id}-label title=${label}>${label}</div>
    </div>`;
  })}
  </div>
</div>`;

  return htl.html`<div style="display: flex; align-items: center; min-height: 33px; margin-left: ${+marginLeft}px; font: 10px sans-serif;">
  <style>

.${id} {
  display: inline-flex;
  align-items: center;
  margin-right: 1em;
}

.${id}::before {
  content: "";
  width: ${+swatchWidth}px;
  height: ${+swatchHeight}px;
  margin-right: 0.5em;
  background: var(--color);
}

  </style>
  <div>${domain.map(value => htl.html`<span class="${id}" style="--color: ${color(value)}">${format(value)}</span>`)}</div>`;
}
)}

function _swatches(Swatches){return(
function swatches({color, ...options}) {
  return Swatches(color, options);
}
)}

export default function define(runtime, observer) {
  const main = runtime.module();
  main.variable(observer()).define(["md"], _1);
  main.variable(observer()).define(["Legend","d3"], _2);
  main.variable(observer()).define(["Legend","d3"], _3);
  main.variable(observer()).define(["Legend","d3"], _4);
  main.variable(observer()).define(["Legend","d3"], _5);
  main.variable(observer()).define(["Legend","d3"], _6);
  main.variable(observer()).define(["Legend","d3"], _7);
  main.variable(observer()).define(["Legend","d3"], _8);
  main.variable(observer()).define(["Legend","d3"], _9);
  main.variable(observer()).define(["Legend","d3"], _10);
  main.variable(observer()).define(["Legend","d3"], _11);
  main.variable(observer()).define(["Legend","d3"], _12);
  main.variable(observer()).define(["md"], _13);
  main.variable(observer()).define(["Swatches","d3"], _14);
  main.variable(observer()).define(["Swatches","d3"], _15);
  main.variable(observer()).define(["md"], _16);
  main.variable(observer("Legend")).define("Legend", ["d3"], _Legend);
  main.variable(observer("legend")).define("legend", ["Legend"], _legend);
  main.variable(observer("Swatches")).define("Swatches", ["d3","htl"], _Swatches);
  main.variable(observer("swatches")).define("swatches", ["Swatches"], _swatches);
  return main;
}
