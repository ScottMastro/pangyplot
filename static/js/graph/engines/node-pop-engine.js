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


function squishToBoundingBox(nodes, box) {
    const bounds = findNodeBoundsInit(nodes);

    const scaleX = box.width / (bounds.width+1);
    const scaleY = box.height / (bounds.height+1);

    nodes.forEach(node => {
        const dx = ((node.x - bounds.x) * scaleX);
        const dy = ((node.y - bounds.y) * scaleY);
        node.x = box.x + dx;
        node.y = box.y + dy;
    });

    return nodes;
}

function makeRoomForSubgraph(nodeResult, originNode, forceGraph){

    const graphNodes = forceGraph.graphData().nodes;
    const originNodes = graphNodes.filter(n => n.nodeid === originNode.nodeid);

    const nodeBox = findNodeBounds(originNodes)
    const subgraphBox = findNodeBoundsInit(nodeResult.nodes);    

    const expandX = subgraphBox.width - nodeBox.width;
    const expandY = subgraphBox.height - nodeBox.height;

    const rootX = nodeBox.x;
    const rootY = nodeBox.y;

    graphNodes.forEach(node => {
        if (node.x > rootX) {
            node.x += expandX;
        }
        if (node.y > rootY) {
            node.y += expandY;
        }
    });

    const newBounds = { x: rootX, y: rootY, 
        width: subgraphBox.width,
        height: subgraphBox.height }

    nodeResult.nodes = squishToBoundingBox(nodeResult.nodes, newBounds);
    return nodeResult;
}

function processSubgraphData(subgraph, originNode, forceGraph){
    graph = forceGraph.graphData();

    let nodeResult = processNodes(subgraph.nodes);
    nodeResult = makeRoomForSubgraph(nodeResult, originNode, forceGraph);

    graph = deleteNode(graph, originNode.nodeid);

    let links = subgraph.links.filter(l => l.source in NODEIDS && l.target in NODEIDS )
    
    links = processLinks(links);
    
    graph.nodes = graph.nodes.concat(nodeResult.nodes);
    graph.links = graph.links.concat(links).concat(nodeResult.nodeLinks);

    forceGraph.graphData({ nodes: graph.nodes, links: graph.links })
    
    document.dispatchEvent(new CustomEvent("updatedGraphData", { detail: { graph: forceGraph.graphData() } }));

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

    // graph.js getGraphCoordinates()
    const params = {
        nodeid,
        ...getGraphCoordinates()
    };

    const url = buildUrl('/subgraph', params);
    fetchData(url, 'subgraph').then(fetchedData => {
        processSubgraphData(fetchedData, originNode, forceGraph)
        dequeueSubgraph(nodeid);
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
        if (nearestNode.type == "null" || nearestNode.type == "segment"){ 
            return;
        }
        const normDist = findNormalizedDistance(nearestNode, coordinates, canvas);
    
        if (normDist < CAN_CLICK_RANGE){
            fetchSubgraph(nearestNode, forceGraph);
        }
    }
}