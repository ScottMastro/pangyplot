const LIGHTNESS_SCALE=0.0;

var GETTING_SUBGRAPH = new Set();

var X_COORD_SHIFT = 0;
var Y_COORD_SHIFT = 0;
var X_COORD_SCALE = 1;
var Y_COORD_SCALE = 1;

const MIN_ZOOM=0.01;
const MAX_ZOOM=1e10;
var HIGHLIGHT_NODE = null;










function draw_gene_outline(ctx, graph){
    
    var hsize = Math.max(HIGHLIGHT_SIZE, HIGHLIGHT_SIZE*(1/ZOOM_FACTOR/10))
    
    graph.nodes.forEach(node => {

        getNodeAnnotations(node).forEach(geneId => {
            color = str_to_color(geneId, lightness=LIGHTNESS_SCALE);
            highlight_node(node, ctx, 0, hsize, color);
        });
     });

    hsize = Math.max(HIGHLIGHT_SIZE+40, (HIGHLIGHT_SIZE+40)*(1/ZOOM_FACTOR/10))
    graph.links.forEach(link => {
        getLinkAnnotations(link).forEach(geneId => {
            color = str_to_color(geneId, lightness=LIGHTNESS_SCALE);
            highlight_link(link, ctx, 0, hsize, color);
        });
     });
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
        let size = Math.max(72, 72*(1/ZOOM_FACTOR/10));
    
        add_text(annotationDict[k].gene, ctx, x, y, size, "lightgrey");
    }

}





function post_render(ctx, graphData){

    ctx.save();

    ctx.shadowColor = 'rgba(0, 0, 0, 0.8)'; 
    ctx.shadowBlur = 4; 
    ctx.shadowOffsetX = 5; ctx.shadowOffsetY = 5;

    // TODO
    //draw_gene_name(ctx, graphData);

    if (HIGHLIGHT_NODE != null){
        highlight = nodeidSplit(HIGHLIGHT_NODE);
        updateGraphInfo(highlight)

        let nodes = graphData.nodes;
        var node;
        for (let i = 0, n = nodes.length; i < n; ++i) {
            node = nodes[i];
            if (highlight === node.nodeid){
                var color = "grey";
                if (HIGHLIGHT_NODE === node.__nodeid){
                    color="red";
                }
                draw_circle_outline(ctx, node.x, node.y, Math.max(HIGHLIGHT_SIZE, HIGHLIGHT_SIZE/ZOOM_FACTOR/10), color, lineWidth=3/ZOOM_FACTOR, fill="rgba(0, 0, 0, 0)");
            }
            
        }
    }

    ctx.restore();
}




window.addEventListener('resize', () => {
    FORCE_GRAPH
        .height(get_graph_height())
        .width(get_graph_width());
});

document.addEventListener("updatedGraphData", function(event) {
    draw_graph(event.detail.graph);
});

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

function explode_node(node, update=true) {
    if (node["type"] == "segment"){ return }
    if (node["type"] == "null"){ return }

    if (! GETTING_SUBGRAPH.has(node.nodeid)){
        fetchSubgraph(node)
    }
}

function explode_nodes(nodes){
    nodes.forEach(node => {
        explode_node(node, update=false);
    });
}

function explode_complex_nodes(nodes){
    nodes.forEach(node => {
        explode_node(node, update=false);
    });
}


function node_click(node) {
    if (node["type"] == "null"){ return }
    if (node["type"] == "segment"){ 
        let query = "MATCH (n:Segment) WHERE ID(n) = " + node.nodeid + " RETURN n"
        navigator.clipboard.writeText(query);
        
    }
    else{
        explode_node(node)
    }
}

function showLoader() {
    document.querySelector('.loader').style.display = 'block';
    document.querySelector('.loader-filter').style.display = 'block';
}

function hideLoader() {
    document.querySelector('.loader').style.display = 'none';
    document.querySelector('.loader-filter').style.display = 'none';
}
hideLoader()
