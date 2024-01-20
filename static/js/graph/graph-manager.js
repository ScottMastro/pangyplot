var GRAPH_GENOME=null;
var GRAPH_CHROM=null;
var GRAPH_START_POS=null;
var GRAPH_END_POS=null;

var GETTING_SUBGRAPH = new Set();

function queueSubgraph(nodeid) {
    if (GETTING_SUBGRAPH.has(nodeid)){
        return false;
    }
    GETTING_SUBGRAPH.add(nodeid);
    showLoader();
    return true;
}
function dequeueSubgraph(nodeid) {
    GETTING_SUBGRAPH.delete(nodeid);
    if (GETTING_SUBGRAPH.size === 0) {
        hideLoader();
    }
}

function processGraphData(rawGraph){

    const nodeResult = processNodes(rawGraph.nodes);
    const links = processLinks(rawGraph.links);
    
    const graph = {"nodes": nodeResult.nodes, "links": links.concat(nodeResult.nodeLinks)}
    console.log("look here",graph);

    document.dispatchEvent(new CustomEvent("updatedGraphData", { detail: { graph: graph } }));
}

function processSubgraphData(subgraph, originNode, graph){
    graph = FORCE_GRAPH.graphData();

    const nodeResult = processNodes(subgraph.nodes);

    nodeResult.nodes = shiftCoordinates(nodeResult.nodes, originNode);
    graph = deleteNode(graph, originNode.nodeid);

    let links = subgraph.links.filter(l => l.source in NODEIDS && l.target in NODEIDS )
    
    links = processLinks(links);
    
    graph.nodes = graph.nodes.concat(nodeResult.nodes);
    graph.links = graph.links.concat(links).concat(nodeResult.nodeLinks);

    updateGraphData(graph);

    HIGHLIGHT_NODE = null;

    const data = { graph: graph };
    document.dispatchEvent(new CustomEvent("updatedGraphData", { detail: data }));
}

function deleteNode(graph, nodeid){
    graph.links = graph.links.filter(l => l.source.nodeid != nodeid && l.target.nodeid != nodeid );
    graph.nodes = graph.nodes.filter(n => nodeid != n.nodeid);

    delete NODEIDS["nodeid"];
    return graph
}

function fetchGraph(genome, chromosome, start, end) {
    const url = buildUrl('/select', { genome, chromosome, start, end });

    fetchData(url, 'graph').then(fetchedData => {
        processGraphData(fetchedData);
    });
}

function fetchSubgraph(originNode) {
    const nodeid = originNode.nodeid;

    if (! queueSubgraph(nodeid)){ return }

    const genome = GRAPH_GENOME;
    const chromosome = GRAPH_CHROM;
    const start = GRAPH_START_POS;
    const end = GRAPH_END_POS;

    const url = buildUrl('/subgraph', {nodeid, genome, chromosome, start, end });

    fetchData(url, 'subgraph').then(fetchedData => {
        dequeueSubgraph(nodeid);
        processSubgraphData(fetchedData, originNode)    
    });
}

document.addEventListener("nodesSelected", function(event) {
    //todo:batch request instead?
    event.detail.nodes.forEach(node => {
        if (node.type != "segment" && node.type != "null"){
            fetchSubgraph(node);
        }
    });
});

function fetchAndConstructGraph(genome, chrom, start, end){
    if (genome === GRAPH_GENOME && 
        chrom === GRAPH_CHROM &&
        start === GRAPH_START_POS &&
        end === GRAPH_END_POS){
        return;
    }

    //todo: accomodate other genomes
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

    //todo: accomodate other genomes
    fetchAndConstructGraph("CHM13", event.detail.chrom, event.detail.start, event.detail.end);
});


document.addEventListener('DOMContentLoaded', function () {

    //PRSS region
    //const data = { chrom: "chr7", start: "144084904", end: "144140209", source: "testing"  };
    // chr18 region
    const data = { chrom: "chr18", start: "47506000", end: "47600000",  source: "testing" };

    //document.dispatchEvent( new CustomEvent('selectedCoordinatesChanged', { detail: data }));
    document.dispatchEvent(new CustomEvent("constructGraph", { detail: data }));

});

