function _1(md){return(
md`# Example Components

This notebook contains shared utilities for [D3 charts](/collection/@d3/charts).`
)}

function _name(Inputs){return(
Inputs.text({label: "Name", value: "ExampleChart"})
)}

function _3(howto,name){return(
howto(name, {open: true})
)}

function _4(howto,name){return(
howto(name, {open: true, specifier: "@d3/example", imports: {d3: "d3", d3Sankey: "d3-sankey"}})
)}

function _currentSpecifier()
{
  const {pathname} = new URL(document.baseURI);
  return pathname.slice(pathname.startsWith("/d/") ? 3 : 1);
}


function _howto(currentSpecifier,htl,md,Inputs){return(
function howto(name, options = {}) {
  if (typeof options === "string") options = {specifier: options};
  const {open, imports = {d3: "d3"}, specifier = currentSpecifier} = options;
  if (!name) throw new Error("missing name");
  return htl.html`<details open=${open} style="max-width: 640px; background: #fffced; box-sizing: border-box; padding: 10px 20px;"><summary style="font-weight: bold; cursor: pointer; outline: none;">How do I use this code? 🤔</summary>
<div style="margin-bottom: -1em;">${md`
**To use this chart outside of Observable,** ${specifier === currentSpecifier ? "" : `go to the <a href=/${specifier}?collection=@d3/charts target=_blank>${specifier} notebook</a>, then `}copy-paste the entire function ${name} ${specifier === currentSpecifier ? "below " : ""}including the copyright notice into your application. You’ll also need to install (*e.g.*, <code>yarn add ${Object.values(imports).join(" ")}</code>) and import (*e.g.*, ${Object.entries(imports).map(([name, value]) => `<code>import \\* as ${name} from "${value}"</code>`).join(", ")}) D3; see [D3’s README](https://github.com/d3/d3/blob/main/README.md) for details. To render a chart, pass ${name} an array of <i>data</i> and any desired <i>options</i>; it will return an SVG element that you can insert into the DOM.

**To use this chart on Observable,** [import it](/@observablehq/introduction-to-imports) into your notebook:

~~~js
import {${name}} from "${specifier}"
~~~

${Inputs.button("Copy code", {reduce: () => navigator.clipboard.writeText(`import {${name}} from "${specifier}"`)})}

Then call ${name}(*data*, *options*) as shown above.

To customize this chart, click the <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path fill-rule="evenodd" clip-rule="evenodd" d="M4.5 1.75C3.80964 1.75 3.25 2.30964 3.25 3C3.25 3.69036 3.80964 4.25 4.5 4.25C5.19036 4.25 5.75 3.69036 5.75 3C5.75 2.30964 5.19036 1.75 4.5 1.75ZM1.75 3C1.75 1.48122 2.98122 0.25 4.5 0.25C6.01878 0.25 7.25 1.48122 7.25 3C7.25 4.16599 6.52434 5.1625 5.5 5.56253V7H8.5C9.4199 7 10.1947 6.37895 10.4281 5.53327C9.44188 5.11546 8.75 4.13853 8.75 3C8.75 1.48122 9.98122 0.25 11.5 0.25C13.0188 0.25 14.25 1.48122 14.25 3C14.25 4.18168 13.5047 5.18928 12.4585 5.57835C12.1782 7.51343 10.5127 9 8.5 9H5.5V10.4375C6.52434 10.8375 7.25 11.834 7.25 13C7.25 14.5188 6.01878 15.75 4.5 15.75C2.98122 15.75 1.75 14.5188 1.75 13C1.75 11.834 2.47566 10.8375 3.5 10.4375L3.5 9V7V5.56253C2.47566 5.1625 1.75 4.16599 1.75 3ZM4.5 11.75C3.80964 11.75 3.25 12.3096 3.25 13C3.25 13.6904 3.80964 14.25 4.5 14.25C5.19036 14.25 5.75 13.6904 5.75 13C5.75 12.3096 5.19036 11.75 4.5 11.75ZM10.25 3C10.25 2.30964 10.8096 1.75 11.5 1.75C12.1904 1.75 12.75 2.30964 12.75 3C12.75 3.69036 12.1904 4.25 11.5 4.25C10.8096 4.25 10.25 3.69036 10.25 3Z"></path></svg> Fork button at the top of the page to create your own copy of this notebook and save your changes. To run a cell, click the play button <svg width="16" height="16" stroke="currentColor" stroke-linejoin="round" stroke-width="1.6" fill="currentColor" viewBox="-1 0 16 16"><path d=" M11.7206 6.94335 C12.2406 7.34365 12.2406 8.12786 11.7206 8.52816L5.60999 13.2321 C4.95242 13.7383 4 13.2696 4 12.4397L4 3.03178 C4 2.20194 4.95243 1.73318 5.60999 2.23937L11.7206 6.94335Z " class="jsx-3927078970"></path></svg> in the top-right corner of the editor, or use Command-S (<span style="font: 14px var(--sans-serif);">⌘S</span>) or Shift-Enter (<span style="font: 14px var(--sans-serif);">⇧↩</span>).

If you have any questions or suggestions, please sign-in to leave a comment. Click the cell menu <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor" class="pointer"><circle r="1.5" cx="8" cy="2.5"></circle><circle r="1.5" cx="8" cy="7.5"></circle><circle r="1.5" cx="8" cy="12.5"></circle></svg> to the left of any cell, then click <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="w1 h1 mr1" stroke="currentColor" stroke-width="2"><path d="M13 3L9 3L3 3C2.44772 3 2 3.44772 2 4L2 11C2 11.5523 2.44772 12 3 12L7.5 12L9.5 14L11.5 12L13 12C13.5523 12 14 11.5523 14 11L14 4C14 3.44772 13.5523 3 13 3Z"></path><line x1="5" y1="6" x2="10" y2="6"></line><line x1="5" y1="9" x2="11" y2="9"></line></svg> Add comment.
`}</div>
</details>`;
}
)}

function _7(altplot){return(
altplot(`Plot.barY(alphabet, {x: "letter", y: "frequency"}).plot()`, {open: true})
)}

function _altplot(htl,md,Inputs){return(
function altplot(code = "", {open} = {}) {
  return htl.html`<details open=${open} style="max-width: 640px; background: #fffced; box-sizing: border-box; padding: 10px 20px;"><summary style="font-weight: bold; cursor: pointer; outline: none;">Is there an easier way? 🤯</summary>
<div style="margin-bottom: -1em;">${md`
Yes! While D3’s low-level abstraction is expressive, you might find it overkill for basic charts. For exploratory data analysis, or just to visualize data quickly, consider [Observable Plot](/@observablehq/plot) instead. Plot is free, [open-source](https://github.com/observablehq/plot), built on top of D3, and maintained by the same people as D3.

For example, the above chart can be written as:

~~~js
${code}
~~~

${Inputs.button("Copy code", {reduce: () => navigator.clipboard.writeText(code)})}

Try pasting this code into a new cell to see.

`}</div>
</details>`;
}
)}

function _linkplot(htl,md){return(
function linkplot(link = "", {open, title} = {}) {
  return htl.html`<details open=${open} style="max-width: 640px; background: #fffced; box-sizing: border-box; padding: 10px 20px;"><summary style="font-weight: bold; cursor: pointer; outline: none;">Is there an easier way? 🤯</summary>
<div style="margin-bottom: -1em;">${md`
Yes! While D3’s low-level abstraction is expressive, you might find it overkill for basic charts. For exploratory data analysis, or just to visualize data quickly, consider [Observable Plot](/@observablehq/plot) instead. Plot is free, [open-source](https://github.com/observablehq/plot), built on top of D3, and maintained by the same people as D3.

For example, <a href=${link}>${title || link}</a> reproduces the above chart, with Plot.

`}</div>
</details>`;
}
)}

export default function define(runtime, observer) {
  const main = runtime.module();
  main.variable(observer()).define(["md"], _1);
  main.variable(observer("viewof name")).define("viewof name", ["Inputs"], _name);
  main.variable(observer("name")).define("name", ["Generators", "viewof name"], (G, _) => G.input(_));
  main.variable(observer()).define(["howto","name"], _3);
  main.variable(observer()).define(["howto","name"], _4);
  main.variable(observer("currentSpecifier")).define("currentSpecifier", _currentSpecifier);
  main.variable(observer("howto")).define("howto", ["currentSpecifier","htl","md","Inputs"], _howto);
  main.variable(observer()).define(["altplot"], _7);
  main.variable(observer("altplot")).define("altplot", ["htl","md","Inputs"], _altplot);
  main.variable(observer("linkplot")).define("linkplot", ["htl","md"], _linkplot);
  return main;
}
