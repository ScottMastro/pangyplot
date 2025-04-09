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

    // Update the graph data without reinitializing the graph
    if (forceGraph) {
        forceGraph.graphData(graph);
        annotationManagerAnnotateGraph(forceGraph.graphData())
        searchSequenceEngineRerun();

        console.log("Graph data updated.");
    } else {

        forceGraph = ForceGraph()(canvasElement)
            .graphData(graph)
            .nodeId("__nodeid")
            .height(getCanvasHeight())
            .width(getCanvasWidth())
            .nodeRelSize(HOVER_PRECISION)
            .nodeVal(NODE_WIDTH)
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
            .warmupTicks(4)
            //.linkDirectionalParticles(4)

        pathManagerInitialize();
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
        //forceGraph.d3Force('pullToAnchor', pullTextToAnchor);

        function textRepelForce(alpha) {
            let strength = -1e9;
            let distanceMin = 10;
            let distanceMax = 10000;

            const nodes = forceGraph.graphData().nodes;
            for (let i = 0; i < nodes.length; i++) {
                if (nodes[i].class != "text") continue;
                let node = nodes[i];

                for (let j = 0; j < nodes.length; j++) {
                    if (i != j) continue;
                    const other = nodes[j];
                    const dx = other.x - node.x;
                    const dy = other.y - node.y;
                    let distance = Math.sqrt(dx * dx + dy * dy);
    
                    if (distance > distanceMax) continue;

                    if (distance < distanceMin) distance = distanceMin;
    
                    const force = (strength / (distance * distance));
                    node.vx += dx  *strength;
                    node.vy += dy * strength;
                }
            }
        }
        //forceGraph.d3Force('textRepel', textRepelForce);

        //todo: try force that keeps nodes apart by certain distance
        //todo: local density check, spread along x axis


        //forceGraph.d3Force('centerEachNode', forceCenterEachNode);
        //forceGraph.d3Force('spreadX', forceSpreadX);
        
        forceGraph.d3Force('center', null);

        function link_force_distance(link) {
            return link.force*10;
        }
        
        forceGraph.d3Force('link').distance(link_force_distance).strength(0.9)
        //forceGraph.d3Force('link').distance(100).strength(0.9); //equal force
        //forceGraph.d3Force('link', null);   // Disable link force

        forceGraph.d3Force('collide', d3.forceCollide(50).radius(50));
        forceGraph.d3Force('charge').strength(-500).distanceMax(1000);

        
        forceGraph.d3Force('repelFromDeletedLinks', repelFromDelLinksDegree);

        const pause = false;
        if(pause){
            forceGraph.d3AlphaDecay(1)
            forceGraph.d3Force('link', null);   // Disable link force
            forceGraph.d3Force('charge', null); // Disable charge force
            forceGraph.d3Force('collide', null); // Disable collide force
            forceGraph.d3Force('center', null); // Disable center force
        }
        graphSettingEngineSetup(forceGraph);
        searchSequenceEngineInitialize(forceGraph);
    }

    setTimeout(() => {
        forceGraph.zoomToFit(200, 10, node => true);
    }, 500); // wait 0.5 seconds 
    
}


// ==================================================

/*
FORCE_GRAPH.d3Force('collide', d3.forceCollide(50).radius(50))    
FORCE_GRAPH.d3Force('charge').strength(-500).distanceMax(1000)
*/

function processGraphData(rawGraph){

    const nodeResult = processNodes(rawGraph.nodes);
    const links = processLinks(rawGraph.links);
    
    let graph = {"nodes": nodeResult.nodes, "links": links.concat(nodeResult.nodeLinks)}
    const normalizedGraph = normalizeGraph(graph);

    renderGraph(normalizedGraph);
    document.dispatchEvent(new CustomEvent("updatedGraphData", { detail: { graph: normalizedGraph } }));
}

function fetchGraph(genome, chromosome, start, end) {
    const url = buildUrl('/select', { genome, chromosome, start, end });
    fetchData(url, 'graph').then(fetchedData => {

        if (fetchedData["detailed"]){
            processGraphData(fetchedData);
        }      

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

    console.log("QUERY:", genome,chrom,start,end);
    
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

    // wide muc4/20 region
    let chrom="chr3"
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
    

    // SERPINB5
    let data = {genome: "GRCh38", chrom:"chr18", start:63466958, end:63515085, genome: "GRCh38"};

    // PRSS1-PRSS2 chr7:142745398-142775564
    data = {genome: "GRCh38", chrom:"chr7", start:142760398-15000, end:142774564+1000, genome: "GRCh38"};
    
    // SLC9A3
    //data = {genome: "GRCh38", chrom:"chr5", start:470456, end:524449, genome: "GRCh38"};


    //document.dispatchEvent( new CustomEvent('selectedCoordinatesChanged', { detail: data }));
    document.dispatchEvent(new CustomEvent("constructGraph", { detail: data }));

});