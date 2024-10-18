// global
var GRAPH_GENOME=null;
var GRAPH_CHROM=null;
var GRAPH_START_POS=null;
var GRAPH_END_POS=null;

let forceGraph = null;

const FORCE_GRAPH_HEIGHT_PROPORTION = 0.8;
const FORCE_GRAPH_WIDTH_PROPORTION = 0.8;

DEBUG=true


var GRAPH_SPREAD_X_FORCE=0

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

    const canvasElement = document.getElementById("graph");

    console.log("forceGraph:", graph);

    // Update the graph data without reinitializing the graph
    if (forceGraph) {
        forceGraph.graphData(graph);
        annotationManagerAnnotateGraph(forceGraph.graphData())

        console.log("Graph data updated.");
    } else {

        forceGraph = ForceGraph()(canvasElement)
            .graphData(graph)
            .nodeId("__nodeid")
            .height(getCanvasHeight())
            .width(getCanvasWidth())
            .nodeVal(NODE_SIZE)
            .nodeRelSize(HOVER_PRECISION)
            .autoPauseRedraw(false) // keep drawing after engine has stopped
            .d3VelocityDecay(0.1)
            .cooldownTicks(Infinity)
            .cooldownTime(Infinity)
            .onNodeDragEnd(node => {
                node.fx = node.x;
                node.fy = node.y;
            })
            .d3AlphaDecay(0.0228)
            .nodeCanvasObject((node, ctx) => renderManagerPaintNode(ctx, node)) 
            .linkCanvasObject((link, ctx) => renderManagerPaintLink(ctx, link)) 
            .nodeLabel("__nodeid")
            .onNodeDrag((node, translate) => inputManagerNodeDragged(node, translate, forceGraph))
            .onNodeClick((node, event) => inputManagerNodeClicked(node, event, forceGraph))
            .minZoom(1e-6) //default = 0.01
            .maxZoom(1000) //default = 1000

            //.linkDirectionalParticles(4)

        inputManagerSetupInputListeners(forceGraph, canvasElement);
        annotationManagerAnnotateGraph(forceGraph.graphData())

        window.addEventListener('resize', () => {
            forceGraph
                .height(getCanvasHeight())
                .width(getCanvasWidth());
        });


        console.log("forceGraph:", forceGraph);

        forceGraph.onEngineTick(() => {
            forceGraph.backgroundColor(colorManagerBackgroundColor());

            debugInformationUpdate(forceGraph.graphData());
        })

        forceGraph.onRenderFramePre((ctx) => { renderManagerPreRender(ctx, forceGraph, getCanvasWidth(), getCanvasHeight()); })
        forceGraph.onRenderFramePost((ctx) => { renderManagerPostRender(ctx, forceGraph, getCanvasWidth(), getCanvasHeight()); })
        
        
        // --- FORCES ---

        function link_force_distance(link) {
            return (link.type === "edge") ? 10 : link.length ;
        }

        // Create and add the custom force
        function forceCenterEachNode(alpha) {
            for (let node of forceGraph.graphData().nodes) {
                if (node.isSingleton){
                    node.vx += (node.initX - node.x) * 0.01 * alpha;
                    node.vy += (node.initY - node.y) * 0.01 * alpha;
                } else if (node.class = "end"){
                    node.vx += (node.initX - node.x) * 0.02 * alpha;
                    node.vy += (node.initY - node.y) * 0.02 * alpha;
                } else{
                    node.vx += (node.initX - node.x) * 0.02 * alpha;
                    node.vy += (node.initY - node.y) * 0.02 * alpha;
                }
            }
        }


        function forceSpreadX(alpha) {
            const nodes = forceGraph.graphData().nodes;
        
            let minX = Infinity, maxX = -Infinity;
            for (const node of nodes) {
                if (node.x < minX) minX = node.x;
                if (node.x > maxX) maxX = node.x;
            }
        
            const midX = (minX + maxX) / 2;
            const range = (maxX-minX)/2;
            let i = 0; 
            for (let node of nodes) {
                const targetX = node.x < midX ? minX : maxX;
                const strength = 1 - Math.abs(targetX - node.x)/range;

                node.vx += (node.x < midX ? -1 : 1) * 1000* strength * alpha;

            }
        }
        
        function pullTextToAnchor(alpha) {
            const threshold = 5000; // Define the snapping threshold distance
        
            for (let node of forceGraph.graphData().nodes) {
                if (node.class === "text") {
                    let dx = node.anchorX - node.x;
                    let dy = node.anchorY - node.y;
        
                    // Calculate the current distance between the node and the anchor
                    let distance = Math.sqrt(dx * dx + dy * dy);
        
                    if (distance > threshold) {
                        // Calculate the ratio to snap the node exactly to the threshold distance
                        let snapRatio = threshold / distance;
        
                        // Snap the node to the threshold distance from the anchor
                        node.x = node.anchorX - dx * snapRatio;
                        node.y = node.anchorY - dy * snapRatio;
        
                        // Now apply the velocity based on the new snapped position
                        node.vx += (node.anchorX - node.x) * 0.01;
                        node.vy += (node.anchorY - node.y) * 0.01;
                    } else {
                        // Apply the velocity normally if within the threshold
                        node.vx += (dx * 0.01);
                        node.vy += (dy * 0.01);
                    }
                }
            }
        }
        forceGraph.d3Force('pullToAnchor', pullTextToAnchor);

        
        //todo: try force that keeps nodes apart by certain distance
        //todo: local density check, spread along x axis


        //forceGraph.d3Force('centerEachNode', forceCenterEachNode);
        //forceGraph.d3Force('spreadX', forceSpreadX);
        
        forceGraph.d3Force('center', null);
        forceGraph.d3Force('link').distance(100).strength(0.9);
        //forceGraph.d3Force('link', null);   // Disable link force

        forceGraph.d3Force('collide', d3.forceCollide(50).radius(50));
        forceGraph.d3Force('charge').strength(-500).distanceMax(1000);


        const pause = false;
        if(pause){
            forceGraph.d3AlphaDecay(1)
            forceGraph.d3Force('link', null);   // Disable link force
            forceGraph.d3Force('charge', null); // Disable charge force
            forceGraph.d3Force('collide', null); // Disable collide force
            forceGraph.d3Force('center', null); // Disable center force
        }
        graphSettingEngineSetup(forceGraph);
    }
}


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
    
    let graph = {"nodes": nodeResult.nodes, "links": links.concat(nodeResult.nodeLinks)}
    graph = reorientLinks(graph);

    const normalizedGraph = normalizeGraph(graph);

    renderGraph(normalizedGraph);
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
    
    annotationManagerFetch(genome, chrom, start, end);
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


    // wide muc4/20 region
    let start=198347210
    let end=198855552 // start+100000
    
    // narrow muc4/20 region
    start=198543540;
    end=198660739;
    
    // repeat region
    start=198563043;
    end=198595149;

    // inversion region
    start=198376687
    end=198692934
    
    //chr18
    start=47808957
    end=47931146

    const data = { genome: "GRCh38", chrom: "chr18", start: start, end: end,  source: "testing" };
    
    //document.dispatchEvent( new CustomEvent('selectedCoordinatesChanged', { detail: data }));
    document.dispatchEvent(new CustomEvent("constructGraph", { detail: data }));

});