
var FORCE_GRAPH = null;
var ZOOM_FACTOR = 1;

const VELOCITY_DECAY=0.1;
//const VELOCITY_DECAY=1;
const HOVER_PRECISION=10;
const NODE_MID_SIZE=15;
const NODE_END_SIZE=30;
const HIGHLIGHT_SIZE=60;

function getGraphHeight(){return window.innerHeight*0.8}
function getGraphWidth(){return window.innerWidth*0.8}

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

    FORCE_GRAPH.backgroundColor(getBackgroundColor());

    draw_gene_outline(ctx, graphData);

    ctx.restore();
}


function updateGraphData(graph) {
    FORCE_GRAPH.graphData({ nodes: graph.nodes, links: graph.links });
};

function draw_graph(graph){

    //graph = shift_coord(graph)

    console.log("forceGraph:", graph);

    // todo https://github.com/vasturiano/d3-force-registry

    const canvasElement = document.getElementById("graph");

    FORCE_GRAPH = ForceGraph()(canvasElement)
        .graphData(graph)
        .nodeId("__nodeid")
        .height(getGraphHeight())
        .width(getGraphWidth())
        .backgroundColor(getBackgroundColor())
        .linkColor(link => getLinkColor(link))
        .nodeColor(node => getNodeColor(node))
        .linkWidth(getLinkWidth)
        .nodeVal(node => getNodeSize(node))

        .d3VelocityDecay(VELOCITY_DECAY)

        
        .onNodeHover(highlight_node)
        .nodeRelSize(HOVER_PRECISION)
        .nodeCanvasObject((node, ctx) => paintNode(node, ctx)) 
        .onNodeClick(node => {node_click(node)})
        .nodeLabel("__nodeid")


        //.linkDirectionalParticles(4)
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
        else if (link.class === "node"){
            HIGHLIGHT_NODE = [id_split(link.source.__nodeid)] ;
        }
    }

    FORCE_GRAPH.onRenderFramePre((ctx) => { pre_render(ctx, FORCE_GRAPH.graphData()); })
    FORCE_GRAPH.onRenderFramePost((ctx) => { post_render(ctx, FORCE_GRAPH.graphData()); })
    // --- FORCES ---

    function link_force_distance(link) {
        return (link.type === "edge") ? 10 : link.length ;
    }

    FORCE_GRAPH.d3Force('link').distance(link_force_distance).strength(0.5).iterations(1)
    FORCE_GRAPH.d3Force('collide', d3.forceCollide(50).radius(50))    
    FORCE_GRAPH.d3Force('charge').strength(-500).distanceMax(1000)
    
    //FORCE_GRAPH.onEngineStop(() => FORCE_GRAPH.zoomToFit(0));

}

