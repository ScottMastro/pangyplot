var FORCE_GRAPH = null;
var ZOOM_FACTOR = 1;
const ZOOM_INTENSITY = 0.2;

DEBUG=true

const VELOCITY_DECAY=0.1;
//const VELOCITY_DECAY=1;
const NODE_SIZE=50;
const LINK_SIZE=10;
const HOVER_PRECISION=2;

function getLinkWidth(link) {
    if (link.class === "node"){
        return NODE_SIZE;
    }
    return LINK_SIZE;
}

function nodeEffectiveRange(){
    return Math.max(10, (HOVER_PRECISION/ZOOM_FACTOR));
}

function paintNode(node, ctx) {
    let x = node.x; let y = node.y;
    let shape = node.type === "null" ? 1 : 0
    let size = NODE_SIZE;

    if(DEBUG){
        draw_circle_outline2(ctx, x, y, nodeEffectiveRange()*NODE_SIZE/8 , "orange", 1, null)
    }
    if (!node.isSingleton){
        return;
    }

    let color = getNodeColor(node);
    [
        () => { draw_circle(ctx, x, y, size, color); },
        () => { draw_circle_outline(ctx, x, y, size, color, lineWidth=5); },
        () => { draw_square(ctx, x, y, size, color); },
        () => { draw_cross(ctx, x, y, size, color); },
        () => { draw_triangle(ctx, x, y, size, color); }
    ][shape]();
}

function zoomIn() {
    const currentZoom = FORCE_GRAPH.zoom();
    const newZoom = currentZoom * (1 + ZOOM_INTENSITY);
    FORCE_GRAPH.zoom(newZoom);
}

function zoomOut() {
    const currentZoom = FORCE_GRAPH.zoom();
    const newZoom = currentZoom * (1 - ZOOM_INTENSITY);
    FORCE_GRAPH.zoom(newZoom);
}

function paintLink(link, ctx){
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(link.source.x, link.source.y);
    ctx.lineWidth = getLinkWidth(link); 
    ctx.lineTo(link.target.x, link.target.y);
    ctx.lineCap = 'round';
    ctx.strokeStyle = getLinkColor(link);
    ctx.stroke();
    ctx.restore();
}

function pre_render(ctx, graphData){
    ZOOM_FACTOR = ctx.canvas.__zoom["k"];

    ctx.save();
    drawGeneOutline(ctx, graphData);

    highlightSelectedNodes(ctx, graphData);

    FORCE_GRAPH.backgroundColor(getBackgroundColor());
    FORCE_GRAPH.nodeRelSize(nodeEffectiveRange())


    ctx.restore();
}

function post_render(ctx, graphData){
    ctx.save();

    // TODO
    //draw_gene_name(ctx, graphData);

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


function onNodeDragHandler(node){
    nodeDraggedInput(node);
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
        .backgroundColor(getBackgroundColor())
        .linkColor(link => getLinkColor(link))
        .nodeColor(node => getNodeColor(node))
        .nodeVal(NODE_SIZE)
        .nodeRelSize(HOVER_PRECISION)
        .autoPauseRedraw(false) // keep drawing after engine has stopped
        .d3VelocityDecay(VELOCITY_DECAY)

        .nodeCanvasObject((node, ctx) => paintNode(node, ctx)) 
        .linkCanvasObject((link, ctx) => paintLink(link, ctx)) 
        .nodeLabel("__nodeid")
        .onNodeDrag(onNodeDragHandler)

        //.linkDirectionalParticles(4)

    //    .minZoom(MIN_ZOOM)
    //    .maxZoom(MAX_ZOOM)

    console.log(FORCE_GRAPH);
    addInputListeners(FORCE_GRAPH, canvasElement);

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