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

function makeRoomForSubgraph(nodeResult, originNode, forceGraph, pushNodes){

    const graphNodes = forceGraph.graphData().nodes;
    const originNodes = graphNodes.filter(n => n.nodeid === originNode.nodeid);

    const nodeBox = findNodeBounds(originNodes)
    const subgraphBox = findNodeBoundsInit(nodeResult.nodes);    

    const expandX = subgraphBox.width - nodeBox.width;
    const expandY = subgraphBox.height - nodeBox.height;

    const rootX = nodeBox.x;
    const rootY = nodeBox.y;

    if (pushNodes){
        graphNodes.forEach(node => {
            if (node.x > rootX) {
                node.x += expandX;
            }
            if (node.y > rootY) {
                node.y += expandY;
            }
        });
    }

    const newBounds = { x: rootX, y: rootY, 
        width: subgraphBox.width,
        height: subgraphBox.height }

    nodeResult.nodes = squishToBoundingBox(nodeResult.nodes, newBounds);
    return nodeResult;
}

function shiftSubgraph(nodeResult, originNode, forceGraph) {
    
    let totalShiftX = 0;
    let totalShiftY = 0;
    let count = 0;

    forceGraph.graphData().nodes.forEach(node => {
        if (node.initX !== undefined && node.initY !== undefined) {
            totalShiftX += (node.x - node.initX);
            totalShiftY += (node.y - node.initY);
            count++;
        }
    });

    const shiftX = count > 0 ? totalShiftX / count : 0;
    const shiftY = count > 0 ? totalShiftY / count : 0;

    nodeResult.nodes.forEach(node => {
        node.x += shiftX;
        node.y += shiftY;
    });

    return nodeResult;
}
function findSubgraphs(nodeIds, adjacencyList) {
    const visited = new Set();
    const connectedComponents = [];

    nodeIds.forEach(nodeId => {
        if (!visited.has(nodeId)) {
            const component = [];
            const queue = [nodeId];
            visited.add(nodeId);

            while (queue.length > 0) {
                const current = queue.shift();
                component.push(current);

                const neighbors = adjacencyList.get(current) || [];
                neighbors.forEach(neighbor => {
                    if (!visited.has(neighbor)) {
                        visited.add(neighbor);
                        queue.push(neighbor);
                    }
                });
            }
            connectedComponents.push(component);
        }
    });

    return connectedComponents;
}

function processSubgraphData(subgraph, originNode, forceGraph){
    graphData = forceGraph.graphData();

    graphData.nodes = graphData.nodes.filter(node => node.type != "collapse");
    graphData.links = graphData.links.filter(link => link.type != "collapse");

    if (graphData.hasOwnProperty('collapsed_nodes')){
        graphData.nodes = [...graphData.nodes, ...graphData.collapsed_nodes];
        graphData.links = [...graphData.links, ...graphData.collapsed_links];
    }

    let nodeResult = processNodes(subgraph.nodes);
    //nodeResult = makeRoomForSubgraph(nodeResult, originNode, forceGraph, false);
    nodeResult = shiftSubgraph(nodeResult, originNode, forceGraph);
    
    graphData = deleteNode(graphData, originNode.nodeid);
       
    links = processLinks(subgraph.links);
    
    graphData.nodes = graphData.nodes.concat(nodeResult.nodes);
    graphData.links = graphData.links.concat(links).concat(nodeResult.nodeLinks);

    graphData = reorientLinks(graphData);

    forceGraph.graphData(graphData)

    //todo: take number as input
    forceGraph = simplifyGraph(forceGraph, 1);
    //forceGraph = shrinkGraph(forceGraph, 1000); 

    document.dispatchEvent(new CustomEvent("updatedGraphData", { detail: { graph: forceGraph.graphData() } }));
}

function deleteNode(graphData, nodeid){
    graphData.nodes = graphData.nodes.filter(node => node.nodeid != nodeid);
    graphData.links = graphData.links.filter(link => 
        (link.class == "node" && link.nodeid != nodeid) ||
        (link.class == "edge" && link.sourceid != nodeid && link.targetid != nodeid));

    delete NODEIDS[nodeid];
    return graphData
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
        if (nearestNode.type == "null" || nearestNode.type == "segment" || nearestNode.type == "collapse"){ 
            return;
        }
        const normDist = findNormalizedDistance(nearestNode, coordinates, canvas);
    
        if (normDist < CAN_CLICK_RANGE){
            fetchSubgraph(nearestNode, forceGraph);
        }
    }
}