function shrinkGraph(forceGraph, size) {
    const graphData = forceGraph.graphData();

    const nodes = graphData.nodes;
    const links = graphData.links;

    const longNodeIds = new Set();
    nodes.forEach(node => {
        if (node.type == "segment" && node.seqLen > size) {
            longNodeIds.add(node.nodeid);
            node.isDrawn=false;
        }
    });

    links.forEach(link => {
        if (link.class == "node" && longNodeIds.has(link.nodeid)){
            link.isDrawn = false;
        }
        else if (link.class == "edge"){
            if (longNodeIds.has(link.sourceid) && longNodeIds.has(link.targetid)) {
                link.isDrawn = false;
            }
        }
    });

    forceGraph.graphData(graphData)

    return forceGraph;
}

function deleteHighlighted(forceGraph) {

    const selectedNodeIds = new Set();
    forceGraph.graphData().nodes.forEach(node => {
        if (node.isSelected) {
            selectedNodeIds.add(node.nodeid);
        }
    });

    forceGraph.graphData().nodes.forEach(node => {
        if (selectedNodeIds.has(node.nodeid)) {         
            node.isSelected=false;
            node.isDrawn=false;
        }
    });

    forceGraph.graphData().links.forEach(link => {
        if (link.class == "node" && selectedNodeIds.has(link.nodeid)){
            link.isDrawn = false;
        }
        else if (link.class == "edge"){
            if (selectedNodeIds.has(link.sourceid) || selectedNodeIds.has(link.targetid)) {
                link.isDrawn = false;
            }
        }
    });

}
