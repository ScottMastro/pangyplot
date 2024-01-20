const LIGHTNESS_SCALE=0.0;


var X_COORD_SHIFT = 0;
var Y_COORD_SHIFT = 0;
var X_COORD_SCALE = 1;
var Y_COORD_SCALE = 1;

const MIN_ZOOM=0.01;
const MAX_ZOOM=1e10;













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
    fetchSubgraph(node)
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



