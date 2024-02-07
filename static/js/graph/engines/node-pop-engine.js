var GETTING_SUBGRAPH = new Set();
const pointerup_CLICK_RANGE = 0.05;

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

function processSubgraphData(subgraph, originNode, forceGraph){
    graph = forceGraph.graphData();

    const nodeResult = processNodes(subgraph.nodes);

    nodeResult.nodes = shiftCoordinates(nodeResult.nodes, originNode);
    graph = deleteNode(graph, originNode.nodeid);

    let links = subgraph.links.filter(l => l.source in NODEIDS && l.target in NODEIDS )
    
    links = processLinks(links);
    
    graph.nodes = graph.nodes.concat(nodeResult.nodes);
    graph.links = graph.links.concat(links).concat(nodeResult.nodeLinks);

    forceGraph.graphData({ nodes: graph.nodes, links: graph.links })

    HIGHLIGHT_NODE = null;
}

function deleteNode(graph, nodeid){
    graph.links = graph.links.filter(l => l.source.nodeid != nodeid && l.target.nodeid != nodeid );
    graph.nodes = graph.nodes.filter(n => nodeid != n.nodeid);

    delete NODEIDS["nodeid"];
    return graph
}

function fetchSubgraph(originNode, forceGraph) {
    const nodeid = originNode.nodeid;

    if (! queueSubgraph(nodeid)){ return }

    const genome = GRAPH_GENOME;
    const chromosome = GRAPH_CHROM;
    const start = GRAPH_START_POS;
    const end = GRAPH_END_POS;

    const url = buildUrl('/subgraph', {nodeid, genome, chromosome, start, end });

    fetchData(url, 'subgraph').then(fetchedData => {
        dequeueSubgraph(nodeid);
        processSubgraphData(fetchedData, originNode, forceGraph)    
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


function popNodeEngineMouseClick(event, forceGraph, canvasElement, canvas, coordinates, inputState){
    if (inputState===NODE_POP_MODE){

        const nearestNode = findNearestNode(forceGraph.graphData().nodes, coordinates);
        if (nearestNode["type"] == "null"){ return }
        const normDist = findNormalizedDistance(nearestNode, coordinates, canvas);
    
        if (normDist < CAN_CLICK_RANGE){
            fetchSubgraph(nearestNode, forceGraph);
        }
    }
}