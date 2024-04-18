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

