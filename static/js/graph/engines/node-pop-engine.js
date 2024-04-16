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

function simplifyGraph(forceGraph, size) {
    const graphData = forceGraph.graphData();

    const nodes = graphData.nodes;
    const nodeDict = {};
    nodes.forEach(node => {
        nodeDict[node.__nodeid] = node;
    });

    const links = graphData.links;

    const junkNodeIds = new Set();
    nodes.forEach(node => {
        if (node.seqLen < size) {
            junkNodeIds.add(node.nodeid);
        } else if ((node.type == "bubble" || node.type == "chain") 
        && node.largestChild < size) {
            junkNodeIds.add(node.nodeid);
        }
    });

    const junkLinks = new Set();
    const affectedLinks = new Set();
    const adjacencyList = new Map();

    links.forEach(link => {
        if (link.class == "node" && junkNodeIds.has(link.nodeid)){
            junkLinks.add(link);
        }
        else if (link.class == "edge"){
            if (junkNodeIds.has(link.sourceid) && junkNodeIds.has(link.targetid)) {
                junkLinks.add(link);

                if (!adjacencyList.has(link.sourceid)) {
                    adjacencyList.set(link.sourceid, []);
                }
                if (!adjacencyList.has(link.targetid)) {
                    adjacencyList.set(link.targetid, []);
                }
                adjacencyList.get(link.sourceid).push(link.targetid);
                adjacencyList.get(link.targetid).push(link.sourceid);

            } else if (junkNodeIds.has(link.sourceid) || junkNodeIds.has(link.targetid)) {
                affectedLinks.add(link);
            }
        }
    });

    const connectedComponents = findSubgraphs(junkNodeIds, adjacencyList);

    graphData.nodes = nodes.filter(node => junkNodeIds.has(node.nodeid));
    graphData.links = links.filter(link => junkLinks.has(link) || affectedLinks.has(link));
    
    graphData.collapsed_nodes = nodes.filter(node => junkNodeIds.has(node.nodeid));
    graphData.collapsed_links = links.filter(link => junkLinks.has(link) || affectedLinks.has(link));

    graphData.nodes = nodes.filter(node => !junkNodeIds.has(node.nodeid));
    graphData.links = links.filter(link => !junkLinks.has(link) && !affectedLinks.has(link));

    const newNodes = [];
    const newLinks = [];
    
    let compId = 0;

    connectedComponents.forEach(component => {
        const id =`component_${compId}`
        //${Math.random().toString(36).substr(2, 12)}`
        const componentNodes = component.map(nodeId => nodes.find(n => n.nodeid === nodeId));
        const x = componentNodes.reduce((acc, n) => acc + n.x, 0) / component.length;
        const y = componentNodes.reduce((acc, n) => acc + n.y, 0) / component.length;
        const seqLen = componentNodes.reduce((acc, n) => acc + n.seqLen, 0);
        
        let x1 = 0; let y1 = 0; let x2 = 0; let y2 = 0;
        let n1 = 0; let n2 = 0;


        component.forEach(nodeId => {
            [...affectedLinks].forEach(link => {
                if (link.class == "edge") {
                    if(link.sourceid === nodeId){
                        const targetId = nodeTargetId(nodeId);
                        const targetNode = nodeDict[targetId];
                        x1 += targetNode.initX;
                        y1 += targetNode.initY;
                        n1+=1;
                    } else if(link.targetid === nodeId){
                        const sourceId = nodeSourceId(nodeId);
                        const sourceNode = nodeDict[sourceId];
                        x2 += sourceNode.initX;
                        y2 += sourceNode.initY;
                        n2+=1;
                    }
                }
            });
        });

        if (n1 == 0){
            x1 = x; y1 = y; 
        } else{
            x1 = x1/n1; y1 = y1/n1;
        }
        if (n2 == 0){
            x2 = x; y2 = y;
        } else{
            x2 = x2/n2; y2 = y2/n2;
        }
        
        const newNode = {
            nodeid: id,
            type: "collapse",
            x1: x1, y1: y1,
            x2: x2, y2: y2,
            size: seqLen,
            largest_child: 0,
            isRef: false
        };
        newNodes.push(newNode);
        compId +=1;
    });

    const nodeResult = processNodes(newNodes);

    compId = 0;
    connectedComponents.forEach(component => {
        const id =`component_${compId}`;

        component.forEach(nodeId => {
            [...affectedLinks].forEach(link => {
                if (link.class == "edge" && (link.sourceid === nodeId || link.targetid === nodeId)) {
                    const newLink = {
                        source: link.sourceid === nodeId ? nodeSourceId(id) : link.source,
                        target: link.targetid === nodeId ? nodeTargetId(id) : link.target,
                        sourceid: link.sourceid === nodeId ? id : link.sourceid,
                        targetid: link.targetid === nodeId ? id : link.targetid,
                        class: "edge",
                        type: "collapse",
                        isVisible: true,
                        length: EDGE_LENGTH,
                        width: EDGE_WIDTH                    
                    };
                    newLinks.push(newLink);
                    //console.log(link, newLink)
                    affectedLinks.delete(link);
                }
            });
        });
        compId +=1;
    });


    graphData.nodes = [...graphData.nodes, ...nodeResult.nodes];
    graphData.links = [...graphData.links, ...newLinks, ...nodeResult.nodeLinks];
    forceGraph.graphData(graphData)

    return forceGraph;
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

    let links = subgraph.links.filter(l => l.source in NODEIDS && l.target in NODEIDS )
    
    links = processLinks(links);
    
    graphData.nodes = graphData.nodes.concat(nodeResult.nodes);
    graphData.links = graphData.links.concat(links).concat(nodeResult.nodeLinks);
    forceGraph.graphData(graphData)

    //todo: take number as input
    forceGraph = simplifyGraph(forceGraph, 10);

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
        if (nearestNode.type == "null" || nearestNode.type == "segment"){ 
            return;
        }
        const normDist = findNormalizedDistance(nearestNode, coordinates, canvas);
    
        if (normDist < CAN_CLICK_RANGE){
            fetchSubgraph(nearestNode, forceGraph);
        }
    }
}