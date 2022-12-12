import define1 from "./a6c00de7c09bdfa1@327.js";

function _1(md){return(
md`# Simple Graph

The simplest starting point for working with D3.`
)}

function _layout(FileAttachment){return(
FileAttachment("DRB1-3123_sorted.lay.tsv").tsv()
)}



function _gfa(FileAttachment){return(
FileAttachment("DRB1-3123_sorted.gfa").tsv({array: true})
)}

function _edges(gfa,nodes)
{ 

  let edges = [];
  for (let i = 1; i < gfa.length; i++) {
    let g=gfa[i]
    
    if (g[0] == "L"){
      let n1 = parseInt(g[1])
      let n2 = parseInt(g[3])
      
      let node_coord1=nodes[n1-1][1]
      let node_coord2=nodes[n2-1][0]

      //console.log(node_coord1, node_coord2)

      edges.push([node_coord1, node_coord2, n1,n2])
    }
  }

  return edges
}


function _7(d3,width,height,nodes,edges)
{  
  let scaleX=12
  let scaleY=10
  
  const svg = d3.create("svg")
      .attr("width", width)
      .attr("height", height);

  for (let i = 1; i < nodes.length; i++) {

    svg.append("line")          // attach a line
        .style("stroke", "red")  // colour the line
        .attr("y1", nodes[i][0][1]/scaleY)
        .attr("x1", nodes[i][0][0]/scaleX)
        .attr("y1", nodes[i][0][1]/scaleY)
        .attr("x2", nodes[i][1][0]/scaleX)
        .attr("y2", nodes[i][1][1]/scaleY)

  }

  
  for (let i = 1; i < edges.length; i++) {

    svg.append("line")          // attach a line
        .style("stroke", "black")  // colour the line
        .style("stroke-width", 5)
        .attr("x1", edges[i][0][0]/scaleX)
        .attr("y1", edges[i][0][1]/scaleY)
        .attr("x2", edges[i][1][0]/scaleX)
        .attr("y2", edges[i][1][1]/scaleY)

  }

  
  //svg
  //  .selectAll("circle")
  //  .data(layout)
  //  .join("circle")
  //    .attr("cx", d => d.X/scaleX)
  //    .attr("cy", d => d.Y/scaleY)
  //    .attr("r", d => Math.random() )
  //    .attr("fill", "skyblue");


  
  return svg.node();
}


function _height(){return(
500
)}

function _width(){return(
1200
)}

function _10(miserables){return(
miserables
)}

function _graphlinks(gfa)
{
  let links = [];
  for (let i = 1; i < gfa.length; i++) {
    let g=gfa[i]

    if (g[0] == "L"){
      let newlink = {}
      newlink["source"] = g[1]
      newlink["target"] = g[3]
      newlink["value"] = 10
      links.push(newlink)
    }
  }

  return links

}


function _graph(layout,graphlinks)
{
  let graph={}
  graph["nodes"] = layout
  graph["links"] = graphlinks
  return graph
}


function _chart3(ForceGraph,miserables,width,invalidation){return(
ForceGraph(miserables, {
  nodeId: d => d.id,
  nodeGroup: d => d.group,
  nodeTitle: d => `${d.id}\n${d.group}`,
  linkStrokeWidth: l => Math.sqrt(l.value),
  width,
  height: 600,
  invalidation // a promise to stop the simulation when the cell is re-run
})
)}

function _ForceGraph2(d3,DOM){return(
function ForceGraph({
  nodes, // an iterable of node objects (typically [{id}, …])
  links // an iterable of link objects (typically [{source, target}, …])
}, {
  nodeId = d => d.id, // given d in nodes, returns a unique identifier (string)
  nodeGroup, // given d in nodes, returns an (ordinal) value for color
  nodeGroups, // an array of ordinal values representing the node groups
  nodeFill = "currentColor", // node stroke fill (if not using a group color encoding)
  nodeStroke = "#fff", // node stroke color
  nodeStrokeWidth = 1.5, // node stroke width, in pixels
  nodeStrokeOpacity = 1, // node stroke opacity
  nodeRadius = 5, // node radius, in pixels
  nodeStrength,
  linkSource = ({source}) => source, // given d in links, returns a node identifier string
  linkTarget = ({target}) => target, // given d in links, returns a node identifier string
  linkStroke = "#999", // link stroke color
  linkStrokeOpacity = 0.6, // link stroke opacity
  linkStrokeWidth = 1.5, // given d in links, returns a stroke width in pixels
  linkStrokeLinecap = "round", // link stroke linecap
  linkStrength,
  colors = d3.schemeTableau10, // an array of color strings, for the node groups
  width = 640, // outer width, in pixels
  height = 400, // outer height, in pixels
  invalidation // when this promise resolves, stop the simulation,
} = {}) {
  // Compute values.
  const N = d3.map(nodes, nodeId).map(intern);
  const LS = d3.map(links, linkSource).map(intern);
  const LT = d3.map(links, linkTarget).map(intern);
  const G = nodeGroup == null ? null : d3.map(nodes, nodeGroup).map(intern);
  const W = typeof linkStrokeWidth !== "function" ? null : d3.map(links, linkStrokeWidth);
  const L = typeof linkStroke !== "function" ? null : d3.map(links, linkStroke);

  // Replace the input nodes and links with mutable objects for the simulation.
  nodes = d3.map(nodes, (_, i) => ({id: N[i]}));
  links = d3.map(links, (_, i) => ({source: LS[i], target: LT[i]}));

  // Compute default domains.
  if (G && nodeGroups === undefined) nodeGroups = d3.sort(G);

  // Construct the scales.
  const color = nodeGroup == null ? null : d3.scaleOrdinal(nodeGroups, colors);

  // Construct the forces.
  const forceNode = d3.forceManyBody();
  const forceLink = d3.forceLink(links).id(({index: i}) => N[i]);
  if (nodeStrength !== undefined) forceNode.strength(nodeStrength);
  if (linkStrength !== undefined) forceLink.strength(linkStrength);

  const simulation = d3.forceSimulation(nodes)
    .force("link", forceLink)
    .force("charge", forceNode)
    .force("center",  d3.forceCenter(width/2, height/2))
    .on("tick", ticked);

  const context = DOM.context2d(width, height);

  function ticked() {
    context.clearRect(0, 0, width, height);

    context.save();
    context.globalAlpha = linkStrokeOpacity;
    for (const [i, link] of links.entries()) { 
      context.beginPath();        
      drawLink(link);
      context.strokeStyle = L ? L[i]: linkStroke;
      context.lineWidth = W ? W[i]: linkStrokeWidth;
      context.stroke();
    }
    context.restore();

    context.save();
    context.strokeStyle = nodeStroke;
    context.globalAlpha = nodeStrokeOpacity;
    for (const [i, node] of nodes.entries()) {
      context.beginPath();
      drawNode(node) 
      context.fillStyle = G ? color(G[i]): nodeFill;
      context.strokeStyle = nodeStroke;
      context.fill();
      context.stroke();
    }
    context.restore();
  }

  function drawLink(d) {
    context.moveTo(d.source.x, d.source.y);
    context.lineTo(d.target.x, d.target.y);
  }

  function drawNode(d) {
    context.moveTo(d.x + nodeRadius, d.y);
    context.arc(d.x, d.y, nodeRadius, 0, 2 * Math.PI);
  }  

  if (invalidation != null) invalidation.then(() => simulation.stop());

  function intern(value) {
    return value !== null && typeof value === "object" ? value.valueOf() : value;
  }

  function drag(simulation) {    
    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }
    
    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }
    
    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }

    function dragsubject(event) {
      return simulation.find(event.sourceEvent.offsetX, event.sourceEvent.offsetY);
    }
    
    return d3.drag()
      .subject(dragsubject)
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended);
  }

  return Object.assign(d3.select(context.canvas).call(drag(simulation)).node(), {scales: {color}});
}
)}

function _drag(d3){return(
simulation => {
  
  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }
  
  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }
  
  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
  
  return d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended);
}
)}

function _17(d,location,md){return(
md`{
  const links = graph.links.map(d => Object.create(d)); 
  const nodes = graph.nodes.map(d => Object.create(d));

  const simulation = d3.forceSimulation(nodes) 
      .force("link", d3.forceLink(links).id(d => d.idx))
      .force("charge", d3.forceManyBody().strength(-10))
      .force("x", d3.forceX(d => d.X/12))
      .force("y", d3.forceY(d => d.Y/10));

  const svg = d3.create("svg")
      .attr("viewBox", [-width / 2, -height / 2, width, height]);
  
  const link = svg.append("g")
      .attr("fill", "none")
      .attr("stroke-width", 1.5)
    .selectAll("path")
    .data(links)
    .join("path")
      .attr("stroke", d => "black")
      .attr("marker-end", d => \`url(${new URL(`#arrow-${d.type}`, location)})\`);

  const node = svg.append("g")
      .attr("fill", "currentColor")
    .selectAll("g")
    .data(nodes)
    .join("g")
      .call(drag(simulation));

  node.append("circle")
      .attr("stroke", "white")
      .attr("stroke-width", 1.5)
      .attr("r", 4);


  simulation.on("tick", () => {
    link.attr("d", linkArc);
    node.attr("transform", d => \`translate(${d.x},${d.y})\`);
  });

  invalidation.then(() => simulation.stop());

  return svg.node();
}`
)}

function _linkArc(){return(
function linkArc(d) {
  const r = Math.hypot(d.target.x - d.source.x, d.target.y - d.source.y);
  return `
    M${d.source.x},${d.source.y}
    A${r},${r} 0 0,1 ${d.target.x},${d.target.y}
  `;
}
)}

export default function define(runtime, observer) {
  const main = runtime.module();
  function toString() { return this.url; }
  const fileAttachments = new Map([
    ["DRB1-3123_sorted.lay.tsv", {url: new URL("./files/af1ccdbf33b2fb6283bfb6fc3cc9198c647cb8ad587ce05571900b3ba67b06d7555b345c25987a827846c379d9aaef5d58d929fb240649d0b762e83c6f29600e.tsv", import.meta.url), mimeType: "text/tab-separated-values", toString}],
    ["DRB1-3123_sorted.gfa", {url: new URL("./files/dc33cce76506a67e7f8fece0f49cb1bb605fb27b76effc5265acc1a68cb98fe5da87eed8266007aeaadff6207ee8d6c4b6c8dbc82d8dd81cf84f64217daddb31.bin", import.meta.url), mimeType: "application/octet-stream", toString}]
  ]);
  main.builtin("FileAttachment", runtime.fileAttachments(name => fileAttachments.get(name)));
  main.variable(observer()).define(["md"], _1);
  const child1 = runtime.module(define1);
  main.import("ForceGraph", child1);
  main.variable(observer("layout")).define("layout", ["FileAttachment"], _layout);
  main.variable(observer("nodes")).define("nodes", ["layout"], _nodes);
  main.variable(observer("gfa")).define("gfa", ["FileAttachment"], _gfa);
  main.variable(observer("edges")).define("edges", ["gfa","nodes"], _edges);
  main.variable(observer()).define(["d3","width","height","nodes","edges"], _7);
  main.variable(observer("height")).define("height", _height);
  main.variable(observer("width")).define("width", _width);
  main.variable(observer()).define(["miserables"], _10);
  main.variable(observer("graphlinks")).define("graphlinks", ["gfa"], _graphlinks);
  main.variable(observer("graph")).define("graph", ["layout","graphlinks"], _graph);
  main.variable(observer("chart3")).define("chart3", ["ForceGraph","miserables","width","invalidation"], _chart3);
  main.variable(observer("ForceGraph2")).define("ForceGraph2", ["d3","DOM"], _ForceGraph2);
  main.variable(observer("drag")).define("drag", ["d3"], _drag);
  main.variable(observer()).define(["d","location","md"], _17);
  main.variable(observer("linkArc")).define("linkArc", _linkArc);
  return main;
}
