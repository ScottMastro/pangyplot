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

function findNodeBoundsInit(nodes) {
    let bounds = {
        minX: Infinity,
        maxX: -Infinity,
        minY: Infinity,
        maxY: -Infinity
    };

    nodes.forEach(node => {
        if (node.initX < bounds.minX) bounds.minX = node.initX;
        if (node.initX > bounds.maxX) bounds.maxX = node.initX;
        if (node.initY < bounds.minY) bounds.minY = node.initY;
        if (node.initY > bounds.maxY) bounds.maxY = node.initY;
    });

    return { x: bounds.minX, y: bounds.minY, 
        width: bounds.maxX - bounds.minX, 
        height: bounds.maxY - bounds.minY };
}

function findNodeBounds(nodes) {
    let bounds = {
        minX: Infinity,
        maxX: -Infinity,
        minY: Infinity,
        maxY: -Infinity
    };

    nodes.forEach(node => {
        if (node.x < bounds.minX) bounds.minX = node.x;
        if (node.x > bounds.maxX) bounds.maxX = node.x;
        if (node.y < bounds.minY) bounds.minY = node.y;
        if (node.y > bounds.maxY) bounds.maxY = node.y;
    });

    return { x: bounds.minX, y: bounds.minY, 
        width: bounds.maxX - bounds.minX, 
        height: bounds.maxY - bounds.minY };
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

function processSubgraphData(subgraph, originNode, forceGraph){
    graph = forceGraph.graphData();

    const nodeResult = processNodes(subgraph.nodes);

    const graphNodes = forceGraph.graphData().nodes;
    const originNodes = graphNodes.filter(n => n.nodeid === originNode.nodeid);

    const nodeBox = findNodeBounds(originNodes)
    const initNodeBox = findNodeBoundsInit(originNodes);    

    const scaleW = initNodeBox.width / initGraphBox.width;
    const scaleH = initNodeBox.height / initGraphBox.height;


    console.log(scaleW, scaleH)












    const subgraphBox = findNodeBoundsInit(nodeResult.nodes);    

    const graphBox = findNodeBounds(graphNodes);
    const initGraphBox = findNodeBoundsInit(forceGraph.graphData().nodes);    

    //const scaleW = initNodeBox.width / initGraphBox.width;
    //const scaleH = initNodeBox.height / initGraphBox.height;

    
    const targetW = scaleW * graphBox.width;
    const targetH = scaleH * graphBox.height;

    console.log(targetW, targetH)


    console.log("initBox:", initGraphBox)
    console.log("subgraphBox:", subgraphBox)

    console.log("graphBox:", graphBox)
    console.log("nodeBox:", nodeBox)

    nodeResult.nodes = squishToBoundingBox(nodeResult.nodes, nodeBox);

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