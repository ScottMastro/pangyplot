function fixCoordinates(nodes, originNode){
    nodes.forEach(node => {
        node.x = originNode.x;
        node.y = originNode.y 
    });

    return nodes
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

    return bounds;
}

function nodeNeighborhood(node, forceGraph) {
    const links = forceGraph.graphData().links;
    const nodes = forceGraph.graphData().nodes;

    const connectedLinks = links.filter(link => link.class === "edge" && (link.sourceid === node.nodeid || link.targetid === node.nodeid));
    const neighborNodeIds = new Set(connectedLinks.flatMap(link => [link.sourceid, link.targetid]));
    const neighbors = Array.from(neighborNodeIds).map(id => nodes.find(n => n.nodeid === id));

    const bounds = findNodeBounds(neighbors);
    const maxDimension = Math.max(bounds.maxX - bounds.minX, bounds.maxY - bounds.minY);

    return { x: node.x - maxDimension/2, 
             y: node.y - maxDimension/2, 
             width: maxDimension, 
             height: maxDimension };
}

function squishToNeighborhood(nodes, neighborhoodBox) {
    const bounds = findNodeBounds(nodes);
    const originalWidth = bounds.maxX - bounds.minX;
    const originalHeight = bounds.maxY - bounds.minY;

    const scaleX = neighborhoodBox.width / (originalWidth+1);
    const scaleY = neighborhoodBox.height / (originalHeight+1);

    nodes.forEach(node => {
        const dx = ((node.x - bounds.minX) * scaleX);
        const dy = ((node.y - bounds.minY) * scaleY);
        node.x = neighborhoodBox.x + dx;
        node.y = neighborhoodBox.y + dy;
    });

    return nodes;
}
