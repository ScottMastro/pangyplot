function findNearestNode(nodes, coordinates) {
    let nearestNode = null;
    let minDistance = Infinity;
    
    nodes.forEach(node => {
        const distance = Math.sqrt((coordinates.x - node.x) ** 2 + (coordinates.y - node.y) ** 2);
        // give a boost to smaller nodes
        const effectiveDistance = distance*(node.isSingleton ? 0.9 : 1);

        if (effectiveDistance < minDistance) {
            minDistance = effectiveDistance;
            nearestNode = node;
        }
    });

    return nearestNode;
}

function findNormalizedDistance(a, b, canvas) {
    const normX = canvas.max.x - canvas.min.x;
    const normY = canvas.max.y - canvas.min.y

    const normDistX = (b.x - canvas.min.x)/normX - (a.x - canvas.min.x)/normX
    const normDistY = (b.y - canvas.min.y)/normY - (a.y - canvas.min.y)/normY

    //in units relative to the size of the canvas
    return Math.sqrt((normDistX) ** 2 + (normDistY) ** 2);
}