const GRAPH_ID = "graph"
const GRAPH_CONTAINER_ID="force-graph-container"
const CANVAS = document.getElementById(GRAPH_ID);
const LIGHTNESS_SCALE=0.0

var GETTING_SUBGRAPH=false

var forceGraph = null

var X_COORD_SHIFT = 0
var Y_COORD_SHIFT = 0
var X_COORD_SCALE = 1
var Y_COORD_SCALE = 1

const BACKGROUND_COLOR="#101020"
const VELOCITY_DECAY=0.1
const MIN_ZOOM=0.01
const MAX_ZOOM=1e10
var LAST_ZOOM = 1;
var HIGHLIGHT_NODE = null;

const NODE_MID_SIZE=15;
const NODE_END_SIZE=30;
const HIGHLIGHT_SIZE=60;

const CHAIN_COLOR="#F3DE8A";
const BUBBLE_COLOR="#E05263";
const SEGMENT_COLOR="#659157";

const REF_COLOR="#3C5E81";
const LINK_COLOR="#969696";
const HIGHLIGHT_LINK_COLOR="#FF0000";

const HOVER_PRECISION=10

function force(alpha) {
    for (let i = 0, n = nodes.length, node, k = alpha * 0.1; i < n; ++i) {
      node = nodes[i];
      node.vx -= node.x * k;
      node.vy -= node.y * k;
    }
  }



function linkWidth(link) {
    if (link.count != null){

        return Math.min(Math.max(3, 3*LAST_ZOOM*link.count/2), 6);

    }

    return Math.max(3, 3*LAST_ZOOM*link.width);
}

function node_paint(node, ctx) {
    let shape = 0;

    let x = node.x; let y = node.y;
    let size = get_node_size(node);
    let color = get_node_color(node);

    [
        () => { draw_circle(ctx, x, y, size, color); },
        () => { draw_square(ctx, x, y, size, color); },
        () => { draw_circle_outline(ctx, x, y, size, color, lineWidth=3); },
        () => { draw_cross(ctx, x, y, size, color); },
        () => { draw_triangle(ctx, x, y, size, color); }
    ][shape]();
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

    if (link.class == "node"){        
        switch (link.type) {
            case "segment":
                return SEGMENT_COLOR;
            case "bubble":
                return BUBBLE_COLOR;
            case "CHAIN":
                return CHAIN_COLOR;
            default:
                return REF_COLOR;
        }
    }
   
    if (link.class == "edge"){
        if(should_highlight_link(link)){
            return HIGHLIGHT_LINK_COLOR;
        }
        return LINK_COLOR;
    }

   return intToColor(link.group)
    
}

function get_node_color(node){
    switch (node.type) {
        case "segment":
            return SEGMENT_COLOR;
        case "bubble":
            return BUBBLE_COLOR;
        case "CHAIN":
            return CHAIN_COLOR;
        default:
            return REF_COLOR;
    }    
}

function get_node_size(node){
    switch (node.class) {
        case "end":
            return NODE_END_SIZE;
        case "mid":
            return NODE_MID_SIZE;
        default:
            return NODE_END_SIZE;
    }    
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

    if (HIGHLIGHT_NODE != null){
        highlight = nodeid_split(HIGHLIGHT_NODE);
        
        let nodes = graphData.nodes;
        var node; var id;
        for (let i = 0, n = nodes.length; i < n; ++i) {
            node = nodes[i];
            if (highlight == node.nodeid){
                var color = "grey";
                if (HIGHLIGHT_NODE == node.__nodeid){
                    color="red";
                }
                draw_circle_outline(ctx, node.x, node.y, Math.max(HIGHLIGHT_SIZE, HIGHLIGHT_SIZE/LAST_ZOOM/10), color, lineWidth=3/LAST_ZOOM, fill="rgba(0, 0, 0, 0)");
            }
            
        }
    }

    ctx.restore();
}

function updateGraphData(graph) {
    forceGraph.graphData({ nodes: graph.nodes, links: graph.links });
};

function draw_graph(graph){

    //graph = shift_coord(graph)

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
        .nodeId('__nodeid')
        .nodeLabel('__nodeid')
        .linkColor(link => get_link_color(link))
        .nodeColor(node => get_node_color(node))
        .onNodeHover(highlight_node)
        .nodeRelSize(HOVER_PRECISION)
        .linkWidth(linkWidth)
        .nodeCanvasObject((node, ctx) => node_paint(node, ctx)) 
        .onNodeClick(node => {explode_node(node)})

        .nodeVal(node => get_node_size(node))

        //.onLinkHover(highlight_link)
        //.linkHoverPrecision(HOVER_PRECISION)

    //    .nodeCanvasObject(highlight_node)
    //    .autoPauseRedraw(false) // keep redrawing after engine has stopped

    //    .minZoom(MIN_ZOOM)
    //    .maxZoom(MAX_ZOOM)

    function highlight_node(node){
        HIGHLIGHT_NODE = (node == null) ? null : node.__nodeid;
    }

    function highlight_link(link){
        if (link == null){ HIGHLIGHT_NODE = [] }
        else if (link.class == "node"){
            HIGHLIGHT_NODE = [id_split(link.source.__nodeid)] ;
        }
    }

    forceGraph.onRenderFramePre((ctx, scale) => { pre_render(ctx, forceGraph.graphData()); })
    forceGraph.onRenderFramePost((ctx, scale) => {post_render(ctx, forceGraph.graphData()); })
    // --- FORCES ---

    function link_force_distance(link) {
        return (link.type == "edge") ? 10 : link.length ;
    }

    forceGraph.d3Force('link').distance(link_force_distance).strength(0.5).iterations(2)
    forceGraph.d3Force('collide', d3.forceCollide(50).radius(50))    
    forceGraph.d3Force('charge').strength(-500).distanceMax(1000)
    
    //forceGraph.onEngineStop(() => forceGraph.zoomToFit(0));

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
            var data = JSON.parse(xmlHttp.response);

            // TODO
            //update_path_selector(data.paths)

            graph = process_graph(data);
            draw_graph(graph);
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
            var data = JSON.parse(xmlHttp.response);
            console.log(data);
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send();
}

function fetch_subgraph(originNode){
    let url = "/subgraph?type=" + originNode["type"] + "&id=" + originNode["id"];

    GETTING_SUBGRAPH=true
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var subgraph = JSON.parse(xmlHttp.response);

            console.log(subgraph);

            graph = forceGraph.graphData();
            graph = process_subgraph(subgraph, originNode, graph);
            updateGraphData(graph);

            HIGHLIGHT_NODE = null;
            GETTING_SUBGRAPH=false;
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send();

}

function explode_node(node, update=true) {
    if (node["type"] == "segment"){ return }
    if (GETTING_SUBGRAPH){ return }
    
    fetch_subgraph(node)



    //newNodes = node["expand_nodes"]
    //for (let i = 0, n = newNodes.length; i < n; ++i) {
    //    newNode = newNodes[i];
    //    newNode.x = node.x;
    //    newNode.y = node.y;
    //}


    //if(update){
    //    updateGraphData(graph);
    //}
}

function explode_nodes(nodes){
    nodes.forEach(node => {
        explode_node(node, update=false);
    });
    updateGraphData(forceGraph.graphData());
}

fetch("CHM13"+encodeURIComponent('#')+"chr18", 47506000, 47590000);

//fetch("chr7", 144084904, 144140209); //PRSS region

//fetch("chr7", 0, 1440859040);

//fetch_haps("chrM", 0, 142775343);