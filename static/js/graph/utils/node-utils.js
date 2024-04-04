const SCALE_FACTOR = 1;

function resetGraphPositions(graph){
    graph.nodes.forEach(node => {
        node.x = node.initX;
        node.y = node.initY;
    });
}

function normalizeGraph(graph) {

    resetGraphPositions(graph)
    
    const bounds = findNodeBounds(graph.nodes);
    
    //const scaleX = (coordinates.xmax - coordinates.xmin)/SCALE_FACTOR;
    //const scaleY = (coordinates.ymax - coordinates.ymin)/SCALE_FACTOR;
    const shiftX = bounds.x;
    const shiftY = bounds.y;

    graph.nodes.forEach(node => {
        node.x = (node.x - shiftX) / SCALE_FACTOR;
        node.y = (node.y - shiftY) / SCALE_FACTOR;
    });

    return graph;
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
