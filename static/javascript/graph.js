const BACKGROUND_COLOR="#101020"
const VELOCITY_DECAY=0.2
const MIN_ZOOM=0.01
const MAX_ZOOM=1e10
var LAST_ZOOM = 1;
var HIGHLIGHT_NODES = [];

function force(alpha) {
    for (let i = 0, n = nodes.length, node, k = alpha * 0.1; i < n; ++i) {
      node = nodes[i];
      node.vx -= node.x * k;
      node.vy -= node.y * k;
    }
  }

function linkWidth(link) {
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

function explode_node(node, graph) {
    console.log(node);

    if (!node["expand_nodes"]){ return }
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
}

function draw_gene_outline(ctx, graphData){

    let nodes = graphData["nodes"]
    for (let i = 0, n = nodes.length, node; i < n; ++i) {
        node = nodes[i];

        node.annotations.sort(function(a, b) { return a - b; });

        for (let j = 0, m = node.annotations.length; j < m; ++j) {
            if (annotationDict[node.annotations[j]].type == "gene"){
                highlight_node(node, ctx, 0, Math.max(40, 40*(1/LAST_ZOOM/10)), intToColor(node.annotations[j]));
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
                highlight_link(link, ctx, 0, Math.max(80, 80*(1/LAST_ZOOM/10)), intToColor(link.annotations[j]));
            }
        }
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

    draw_gene_outline(ctx, graphData);

    ctx.restore();
}

function post_render(ctx, graphData){

    ctx.save();

    ctx.shadowColor = 'rgba(0, 0, 0, 0.8)'; 
    ctx.shadowBlur = 4; 
    ctx.shadowOffsetX = 5; ctx.shadowOffsetY = 5;

    draw_gene_name(ctx, graphData);

    for (let i = 0, n = HIGHLIGHT_NODES.length, node; i < n; ++i) {
        node = HIGHLIGHT_NODES[i];
        draw_circle_outline(ctx, node.x, node.y, node.size+10, "red", lineWidth=3, fill="rgba(0, 0, 0, 0)");

        if (node.pos != null){
            let text = node.chrom+":"+node.pos;
            add_text(text, ctx, node.x + 20, node.y, 24, "red", align="left");
        }
    }

    ctx.restore();
}


function draw_graph(graph){

    const canvas = document.getElementById('graph');

    annotationDict = {}
    for (let i = 0, n = graph.annotations.length; i < n; ++i) {
        annotationDict[graph.annotations[i].index] = graph.annotations[i];
    }
    for (let i = 0, n = graph.nodes.length; i < n; ++i) {
        graph.nodes[i]["color"] = intToColor(graph.nodes[i]["group"])
    }
    
    const updateGraphData = () => {
        Graph.graphData({ nodes: graph["nodes"], links: graph["links"] });
    };
    
    //.linkDirectionalParticles(4)
    console.log(graph);

    const Graph = ForceGraph()
    (document.getElementById('graph'))
        .graphData(graph)
        .backgroundColor(BACKGROUND_COLOR)
        .minZoom(MIN_ZOOM)
        .maxZoom(MAX_ZOOM)
        .d3VelocityDecay(VELOCITY_DECAY)

        .nodeVal(node => node["size"])
        .nodeRelSize(6)
        .nodeId('id')
        .nodeLabel('id')
        .linkColor(link => intToColor(link.group))
        .linkWidth(linkWidth)
                .nodeCanvasObject(highlight_node)

        .nodeCanvasObject((node, ctx) => node_paint(node, ctx)) 
        .autoPauseRedraw(false) // keep redrawing after engine has stopped
        .onNodeClick(node => {explode_node(node, graph); updateGraphData()})

    function highlight_node(node){
        HIGHLIGHT_NODES = (node) ? [node] : [] ;
    }

    Graph.onNodeHover(highlight_node);
    

    Graph.onRenderFramePre((ctx, scale) => { pre_render(ctx, Graph.graphData()); })
    Graph.onRenderFramePost((ctx, scale) => {post_render(ctx, Graph.graphData()); })

    // --- FORCES ---

    function link_force_distance(link) {
        return (link.type == "edge") ? 5 : link.length ;
    }

    Graph.d3Force('link').distance(link_force_distance).strength(0.5).iterations(2)
    Graph.d3Force('collide', d3.forceCollide(50).radius(20))    
    Graph.d3Force('charge').strength(-30).distanceMax(500)
    
}

function fetch(chromosome, start, end) {

    let url = "/select?chromosome=" + chromosome;
    url = url + "&start=" + start;
    url = url + "&end=" + end;

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var data = JSON.parse(xmlHttp.response)
            draw_graph(data)
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send();
}

fetch("chrM", 0, 142775343);

