var FORCE_GRAPH = null;
var ZOOM_FACTOR = 1;

const VELOCITY_DECAY=0.1;
//const VELOCITY_DECAY=1;
const HOVER_PRECISION=10;
const NODE_MID_SIZE=15;
const NODE_END_SIZE=30;


function getLinkWidth(link) {
    if (link.count != null){
        return Math.min(Math.max(3, 3*ZOOM_FACTOR*link.count/2), 6);
    }
    return Math.max(3, 3*ZOOM_FACTOR*link.width);
}
function getNodeSize(node){
    switch (node.class) {
        case "end":
            return NODE_END_SIZE;
        case "mid":
            return NODE_MID_SIZE;
        default:
            return NODE_END_SIZE;
    }    
}

function paintNode(node, ctx) {

    let x = node.x; let y = node.y;
    let shape = node.type === "null" ? 1 : 0
    let size = getNodeSize(node);
    let color = getNodeColor(node);
    [
        () => { draw_circle(ctx, x, y, size, color); },
        () => { draw_circle_outline(ctx, x, y, size, color, lineWidth=5); },
        () => { draw_square(ctx, x, y, size, color); },
        () => { draw_cross(ctx, x, y, size, color); },
        () => { draw_triangle(ctx, x, y, size, color); }
    ][shape]();
}

function pre_render(ctx, graphData){
    ZOOM_FACTOR = ctx.canvas.__zoom["k"];
    ctx.save();

    FORCE_GRAPH.backgroundColor(_getBackgroundColor());

    drawGeneOutline(ctx, graphData);

    ctx.restore();
}


function post_render(ctx, graphData){
    ctx.save();

    // TODO
    //draw_gene_name(ctx, graphData);

    higlightSelectedNode(ctx, graphData);

    ctx.restore();
}



function updateGraphData(graph) {
    FORCE_GRAPH.graphData({ nodes: graph.nodes, links: graph.links });
};


function _getGraphHeight(){return window.innerHeight*0.8}
function _getGraphWidth(){return window.innerWidth*0.8}


window.addEventListener('resize', () => {
    FORCE_GRAPH
        .height(_getGraphHeight())
        .width(_getGraphWidth());
});




function _getBackgroundColor(){
    return getBackgroundColor();
}
function _getLinkColor(link){
    return getLinkColor(link);
}
function _getNodeColor(node){
    return getNodeColor(node);

}

function renderGraph(graph){

    //graph = shift_coord(graph)

    console.log("forceGraph:", graph);

    // todo https://github.com/vasturiano/d3-force-registry

    const canvasElement = document.getElementById("graph");

    FORCE_GRAPH = ForceGraph()(canvasElement)
        .graphData(graph)
        .nodeId("__nodeid")
        .height(_getGraphHeight())
        .width(_getGraphWidth())
        .backgroundColor(_getBackgroundColor())
        .linkColor(link => _getLinkColor(link))
        .nodeColor(node => _getNodeColor(node))
        .linkWidth(getLinkWidth)
        .nodeVal(node => getNodeSize(node))
        .autoPauseRedraw(false) // keep drawing after engine has stopped

        .d3VelocityDecay(VELOCITY_DECAY)

        .nodeRelSize(HOVER_PRECISION)
        .nodeCanvasObject((node, ctx) => paintNode(node, ctx)) 
        .nodeLabel("__nodeid")


        //.linkDirectionalParticles(4)
        //.linkHoverPrecision(HOVER_PRECISION)

    //    .nodeCanvasObject(highlight_node)

    //    .minZoom(MIN_ZOOM)
    //    .maxZoom(MAX_ZOOM)

    console.log(FORCE_GRAPH);
    addMouseListener(FORCE_GRAPH, canvasElement);


    //FORCE_GRAPH.onRenderFramePre((ctx) => { calculateFPS(); })

    FORCE_GRAPH.onEngineTick(() => {
        debugInformationUpdate(FORCE_GRAPH.graphData());
    })

    FORCE_GRAPH.onRenderFramePre((ctx) => { pre_render(ctx, FORCE_GRAPH.graphData()); })
    FORCE_GRAPH.onRenderFramePost((ctx) => { post_render(ctx, FORCE_GRAPH.graphData()); })
    
    
    // --- FORCES ---

    function link_force_distance(link) {
        return (link.type === "edge") ? 10 : link.length ;
    }
    

    FORCE_GRAPH.d3Force('link').distance(link_force_distance).strength(0.5).iterations(1)
    FORCE_GRAPH.d3Force('collide', d3.forceCollide(50).radius(50));
    FORCE_GRAPH.d3Force('charge').strength(-500).distanceMax(1000);




    //FORCE_GRAPH.onEngineStop(() => FORCE_GRAPH.zoomToFit(0));

}

document.addEventListener("updatedGraphData", function(event) {
    renderGraph(event.detail.graph);
});




// ==================================================

/*
function link_force_distance(link) {
    return (link.type === "edge") ? 10 : link.length ;
}

    FORCE_GRAPH.d3Force('link', null);   // Disable link force
    FORCE_GRAPH.d3Force('charge', null); // Disable charge force
    FORCE_GRAPH.d3Force('center', null); // Disable center force


FORCE_GRAPH.d3Force('link').distance(link_force_distance).strength(0.5).iterations(1)
FORCE_GRAPH.d3Force('collide', d3.forceCollide(50).radius(50))    
FORCE_GRAPH.d3Force('charge').strength(-500).distanceMax(1000)
*/