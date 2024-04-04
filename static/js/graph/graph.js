// global
var GRAPH_GENOME=null;
var GRAPH_CHROM=null;
var GRAPH_START_POS=null;
var GRAPH_END_POS=null;

const FORCE_GRAPH_HEIGHT_PROPORTION = 0.8;
const FORCE_GRAPH_WIDTH_PROPORTION = 0.8;

DEBUG=true


function getGraphCoordinates(){
    return {genome: GRAPH_GENOME,
            chromosome:GRAPH_CHROM,
            start:GRAPH_START_POS,
            end:GRAPH_END_POS};
}


// todo https://github.com/vasturiano/d3-force-registry

function getCanvasWidth(){
    return window.innerWidth*FORCE_GRAPH_WIDTH_PROPORTION;
}
function getCanvasHeight(){
    return window.innerHeight*FORCE_GRAPH_HEIGHT_PROPORTION;
}

function renderGraph(graph){

    console.log("forceGraph:", graph);

    const canvasElement = document.getElementById("graph");
    var forceGraph = ForceGraph()(canvasElement)
        .graphData(graph)
        .nodeId("__nodeid")
        .height(getCanvasHeight())
        .width(getCanvasWidth())
        .backgroundColor(getBackgroundColor())
        .linkColor(link => getLinkColor(link))
        .nodeColor(node => getNodeColor(node))
        .nodeVal(NODE_SIZE)
        .nodeRelSize(HOVER_PRECISION)
        .autoPauseRedraw(false) // keep drawing after engine has stopped
        .d3VelocityDecay(0.1)
        .d3AlphaDecay(0.0228)
        .nodeCanvasObject((node, ctx) => renderManagerPaintNode(ctx, node, forceGraph)) 
        .linkCanvasObject((link, ctx) => renderManagerPaintLink(ctx, link, forceGraph)) 
        .nodeLabel("__nodeid")
        .onNodeDrag((node, translate) => inputManagerNodeDragged(node, translate, forceGraph))
        .onNodeClick((node, event) => inputManagerNodeClicked(node, event, forceGraph))

        //.linkDirectionalParticles(4)

    //    .minZoom(MIN_ZOOM)
    //    .maxZoom(MAX_ZOOM)

    inputManagerSetupInputListeners(forceGraph, canvasElement);


    window.addEventListener('resize', () => {
        forceGraph
            .height(getCanvasHeight())
            .width(getCanvasWidth());
    });

    console.log("forceGraph:", forceGraph);

    forceGraph.onEngineTick(() => {
        debugInformationUpdate(forceGraph.graphData());
    })

    forceGraph.onRenderFramePre((ctx) => { renderManagerPreRender(ctx, forceGraph, getCanvasWidth(), getCanvasHeight()); })
    forceGraph.onRenderFramePost((ctx) => { renderManagerPostRender(ctx, forceGraph); })
    
    
    // --- FORCES ---

    function link_force_distance(link) {
        return (link.type === "edge") ? 10 : link.length ;
    }

    const nodes = graph.nodes;
    // Create and add the custom force
    //forceGraph.d3Force('spreadX', d3.forceX().strength(0).x((d, i) => (i / forceGraph.graphData().nodes.length)));
    
    forceGraph.d3Force('link').distance(100).strength(0.9)
    forceGraph.d3Force('collide', d3.forceCollide(50).radius(50));
    forceGraph.d3Force('charge').strength(-500).distanceMax(1000);

    const pause = false;
    if(pause){
        forceGraph.d3AlphaDecay(1)
        forceGraph.d3Force('link', null);   // Disable link force
        forceGraph.d3Force('charge', null); // Disable charge force
        forceGraph.d3Force('collide', null); // Disable center force
    }
    graphSettingEngineSetup(forceGraph);
}

document.addEventListener("updatedGraphData", function(event) {
    renderGraph(event.detail.graph);
});


// ==================================================

/*
function link_force_distance(link) {
    return (link.type === "edge") ? 10 : link.length ;
}



FORCE_GRAPH.d3Force('link').distance(link_force_distance).strength(0.5).iterations(1)
FORCE_GRAPH.d3Force('collide', d3.forceCollide(50).radius(50))    
FORCE_GRAPH.d3Force('charge').strength(-500).distanceMax(1000)
*/

function processGraphData(rawGraph){

    const nodeResult = processNodes(rawGraph.nodes);
    const links = processLinks(rawGraph.links);
    
    const graph = {"nodes": nodeResult.nodes, "links": links.concat(nodeResult.nodeLinks)}

    const normalizedGraph = normalizeGraph(graph);

    document.dispatchEvent(new CustomEvent("updatedGraphData", { detail: { graph: normalizedGraph } }));
}

function fetchGraph(genome, chromosome, start, end) {
    const url = buildUrl('/select', { genome, chromosome, start, end });

    fetchData(url, 'graph').then(fetchedData => {
        processGraphData(fetchedData);
    });
}
function fetchAndConstructGraph(genome, chrom, start, end){
    if (genome === GRAPH_GENOME && 
        chrom === GRAPH_CHROM &&
        start === GRAPH_START_POS &&
        end === GRAPH_END_POS){
        return;
    }

    GRAPH_GENOME = genome;
    GRAPH_CHROM = chrom;
    GRAPH_START_POS = start;
    GRAPH_END_POS = end;

    console.log("CONSTRUCTING:", genome,chrom,start,end);
    
    fetchGenes(genome, chrom, start, end);
    fetchGraph(genome, chrom, start, end);
}

document.addEventListener('constructGraph', function(event) {
    const graphElement = document.getElementById('graph-container')    
    graphElement.classList.remove("graph-container-empty");
    graphElement.scrollIntoView({ behavior: 'smooth' });

    fetchAndConstructGraph(event.detail.genome, event.detail.chrom, event.detail.start, event.detail.end);
});


document.addEventListener('DOMContentLoaded', function () {
    //PRSS region
    //const data = { chrom: "chr7", start: "144084904", end: "144140209", source: "testing"  };
    // chr18 region
    //const data = { genome: "CHM13", chrom: "chr18", start: "47506000", end: "47600000",  source: "testing" };


    // muc4 region
    let start=198347210
    let end=198855552
    const data = { genome: "CHM13", chrom: "chr3", start: start, end: start+40000,  source: "testing" };
    
    //document.dispatchEvent( new CustomEvent('selectedCoordinatesChanged', { detail: data }));
    document.dispatchEvent(new CustomEvent("constructGraph", { detail: data }));

});