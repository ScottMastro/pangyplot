const GRAPH_ID = "graph"
const GRAPH_CONTAINER_ID="force-graph-container"
const CANVAS = document.getElementById(GRAPH_ID);
const LIGHTNESS_SCALE=0.0

var forceGraph = null

var X_COORD_SHIFT = 0
var Y_COORD_SHIFT = 0
var X_COORD_SCALE = 1
var Y_COORD_SCALE = 1

const BACKGROUND_COLOR="#101020"
const VELOCITY_DECAY=0.2
const MIN_ZOOM=0.01
const MAX_ZOOM=1e10
var LAST_ZOOM = 1;
var HIGHLIGHT_NODES = [];


REF_COLOR="#3C5E81"
LINK_COLOR="#969696"
HIGHLIGHT_LINK_COLOR="#FF0000"

function force(alpha) {
    for (let i = 0, n = nodes.length, node, k = alpha * 0.1; i < n; ++i) {
      node = nodes[i];
      node.vx -= node.x * k;
      node.vy -= node.y * k;
    }
  }

function linkWidth(link) {
    if (link.count != null){

        return Math.min(Math.max(2, LAST_ZOOM*link.count/2), 6);

    }

    return Math.max(2, LAST_ZOOM*link.width);
}

function node_paint(node, ctx) {
    let shape = node.shape || 0;
    let x = node.x; let y = node.y;
    let size = node.size;
    let color = intToColor(node.group);

    [
        () => { draw_circle(ctx, x, y, size, color); },
        () => { draw_square(ctx, x, y, size, color); },
        () => { draw_circle_outline(ctx, x, y, size, color, lineWidth=3); },
        () => { draw_cross(ctx, x, y, size, color); },
        () => { draw_triangle(ctx, x, y, size, color); }
    ][shape]();
}

function explode_node(node, update=true) {
    var graph = forceGraph.graphData()

    if (!node["expand_nodes"]){ return }
    if (node["expanded"]){ return }

    node["expanded"] = true;
    HIGHLIGHT_NODES = [] ;

    newNodes = node["expand_nodes"]
    for (let i = 0, n = newNodes.length; i < n; ++i) {
        newNode = newNodes[i];
        newNode.x = node.x;
        newNode.y = node.y;
    }

    graph["links"] = graph["links"].filter(l => l.source !== node && l.target !== node);
    graph["nodes"] = graph["nodes"].filter(n => n !== node);

    graph["nodes"] = graph["nodes"].concat(newNodes);
    graph["links"] = graph["links"].concat(node["expand_links"]);

    if(update){
        updateGraphData(graph);
    }
}

function explode_nodes(nodes){
    nodes.forEach(node => {
        explode_node(node, update=false);
    });
    updateGraphData(forceGraph.graphData());
}

function draw_gene_outline(ctx, graphData){

    let nodes = graphData["nodes"]
    for (let i = 0, n = nodes.length, node; i < n; ++i) {
        node = nodes[i];

        node.annotations.sort(function(a, b) { return a - b; });

        for (let j = 0, m = node.annotations.length; j < m; ++j) {
            if (annotationDict[node.annotations[j]].type == "gene"){
                color = intToColor(node.annotations[j], lightness=LIGHTNESS_SCALE);
                highlight_node(node, ctx, 0, Math.max(40, 40*(1/LAST_ZOOM/10)), color);
            }
        }
    }
    
    let links = graphData["links"]
    for (let i = 0, n = links.length, link; i < n; ++i) {
            link = links[i];

            link.annotations.sort(function(a, b) {
            return a - b;
            });

        for (let j = 0, m = link.annotations.length; j < m; ++j) {
            if (annotationDict[link.annotations[j]].type == "gene"){
                color = intToColor(link.annotations[j], lightness=LIGHTNESS_SCALE);
                highlight_link(link, ctx, 0, Math.max(80, 80*(1/LAST_ZOOM/10)), color);
            }
        }
    }
}

function get_link_color(link){

    if (link.type == "node"){        
        if (link.group == 1){
            return REF_COLOR;
        }
    }
    if (link.type == "edge"){
        if(should_highlight_link(link)){
            return HIGHLIGHT_LINK_COLOR;
        }
        return LINK_COLOR;
    }
   
   return intToColor(link.group)
    
}

function draw_gene_name(ctx, graphData){

    annotationNodesX = {};
    annotationNodesY = {};

    let nodes = graphData.nodes;
    for (let i = 0, n = nodes.length, node; i < n; ++i) {
        node = nodes[i];

        for (let j = 0, m = node.annotations.length, k; j < m; ++j) {
            k = node.annotations[j]

            if (!annotationNodesX.hasOwnProperty(k)) {
                annotationNodesX[k] = [];
                annotationNodesY[k] = [];
            }
            annotationNodesX[k].push(node.x)
            annotationNodesY[k].push(node.y);
        } 
    }

    for (var k in annotationNodesX) {

        if (annotationDict[k].type != "gene"){
            continue;
        }

        var n = annotationNodesX[k].length
        var sumX = annotationNodesX[k].reduce(function(a, b){
            return a + b;
        }, 0);
        var sumY = annotationNodesY[k].reduce(function(a, b){
            return a + b;
        }, 0);

        let x = sumX/n; let y = sumY/n;
        let size = Math.max(72, 72*(1/LAST_ZOOM/10));
    
        add_text(annotationDict[k].gene, ctx, x, y, size, "lightgrey");
    }

}

function pre_render(ctx, graphData){
    LAST_ZOOM = ctx.canvas.__zoom["k"];
    ctx.save();

    // TODO
    //draw_gene_outline(ctx, graphData);

    ctx.restore();
}

function post_render(ctx, graphData){

    ctx.save();

    ctx.shadowColor = 'rgba(0, 0, 0, 0.8)'; 
    ctx.shadowBlur = 4; 
    ctx.shadowOffsetX = 5; ctx.shadowOffsetY = 5;

    // TODO
    //draw_gene_name(ctx, graphData);

    for (let i = 0, n = HIGHLIGHT_NODES.length, node; i < n; ++i) {
        node = HIGHLIGHT_NODES[i];
        draw_circle_outline(ctx, node.x, node.y, node.size+10, "red", lineWidth=3, fill="rgba(0, 0, 0, 0)");

        if (node.pos != null){
            let text = node.chrom+":"+node.pos;
            add_text(text, ctx, node.x + 20, node.y, 24, "red", align="left");
        }
        else if (node.start != null){
            let text = node.chrom+":"+node.start+"-"+node.end;
            add_text(text, ctx, node.x + 20, node.y, 24, "red", align="left");
        }
    }

    ctx.restore();
}

function updateGraphData(graph) {
    forceGraph.graphData({ nodes: graph["nodes"], links: graph["links"] });
};

function draw_graph(graph){

    graph = shift_coord(graph)

    annotationDict = {}
    //for (let i = 0, n = graph.annotations.length; i < n; ++i) {
    //    annotationDict[graph.annotations[i].index] = graph.annotations[i];
    //}
    //for (let i = 0, n = graph.nodes.length; i < n; ++i) {
    //   graph.nodes[i]["color"] = intToColor(graph.nodes[i]["group"])
    //}
    
    //.linkDirectionalParticles(4)
    console.log(graph);

    forceGraph = ForceGraph()(CANVAS)
        .graphData(graph)
        .backgroundColor(BACKGROUND_COLOR)
        .d3VelocityDecay(VELOCITY_DECAY)
        .nodeId('id')
        .nodeLabel('id')
        .nodeRelSize(6)
        .linkColor(link => get_link_color(link))
        .linkWidth(linkWidth)

    //    .nodeVal(node => node["size"])
    //    .nodeCanvasObject(highlight_node)
    //    .nodeCanvasObject((node, ctx) => node_paint(node, ctx)) 
    //    .autoPauseRedraw(false) // keep redrawing after engine has stopped
    //    .onNodeClick(node => {explode_node(node)})

    //    .minZoom(MIN_ZOOM)
    //    .maxZoom(MAX_ZOOM)

    //function highlight_node(node){
    //    HIGHLIGHT_NODES = (node) ? [node] : [] ;
    //}

    //forceGraph.onNodeHover(highlight_node);

    forceGraph.onRenderFramePre((ctx, scale) => { pre_render(ctx, forceGraph.graphData()); })
    forceGraph.onRenderFramePost((ctx, scale) => {post_render(ctx, forceGraph.graphData()); })

    // --- FORCES ---

    //function link_force_distance(link) {
    //    return (link.type == "edge") ? 5 : link.length ;
    //}

    //forceGraph.d3Force('link').distance(link_force_distance).strength(0.5).iterations(2)
    //forceGraph.d3Force('collide', d3.forceCollide(50).radius(20))    
    //forceGraph.d3Force('charge').strength(-500).distanceMax(1000)
    
}

function shift_coord(graph) {
    let minX = Infinity;
    let maxX = -1;
    let minY = Infinity;
    let maxY = -1;


    for (const node of graph.nodes) {
        if (node.x < minX) { minX = node.x; }
        if (node.y < minY) { minY = node.y; }
        if (node.x > maxX) { maxX = node.x; }
        if (node.y > maxY) { maxY = node.y; }
    }

    X_COORD_SHIFT = minX
    Y_COORD_SHIFT = minY
    X_COORD_SCALE = maxX-minX
    Y_COORD_SCALE = maxY-minY

    for (const node of graph.nodes) {
        node.x = (node.x - X_COORD_SHIFT)/X_COORD_SCALE;
        node.y = (node.y - Y_COORD_SHIFT)/Y_COORD_SCALE;
    }

    return graph
}


function fetch(chromosome, start, end) {

    let url = "/select?chromosome=" + chromosome;
    url = url + "&start=" + start;
    url = url + "&end=" + end;

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var data = JSON.parse(xmlHttp.response)
            // TODO
            //update_path_selector(data.paths)
            draw_graph(data)
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send();
}

function fetch_haps(chromosome, start, end) {

    let url = "/haplotypes?chromosome=" + chromosome;
    url = url + "&start=" + start;
    url = url + "&end=" + end;

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var data = JSON.parse(xmlHttp.response)
            console.log(data)
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send();
}

fetch("CHM13#chr18", 7000000, 8000000);

//fetch("chr7", 144084904, 144140209); //PRSS region

//fetch("chr7", 0, 1440859040);

//fetch_haps("chrM", 0, 142775343);