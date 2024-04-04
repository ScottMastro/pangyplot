//todo: is this script needed?

const NORMALIZATION_RANGE = 1000;
var NORMALIZATION_X = 1;
var NORMALIZATION_Y = 1;
var SHIFT_X = 0;
var SHIFT_Y = 0;


function normalizeGraph(graph) {
    return graph;
    const coordinates = findBoundingBoxNodes(graph.nodes);

    const NORMALIZATION_X = (coordinates.xmax - coordinates.xmin)/NORMALIZATION_RANGE;
    const NORMALIZATION_Y = (coordinates.ymax - coordinates.ymin)/NORMALIZATION_RANGE;
    const SHIFT_X = coordinates.xmin;
    const SHIFT_Y = coordinates.ymin;

    graph.nodes.forEach(node => {
        node.x = (node.x - SHIFT_X) / NORMALIZATION_X;
        node.y = (node.y - SHIFT_Y) / NORMALIZATION_Y;
    });


    graph.nodes.forEach(node => {
        console.log(`(${node.__nodeid}, ${node.x}, ${node.y})`);
    });

    return graph;
}

function shiftCoordinates(nodes, originNode){
    const initPos = INIT_POSITIONS[originNode.nodeid]
    const xshift = originNode.x - initPos.x
    const yshift = originNode.y - initPos.y

    nodes.forEach(node => {
        node.x = node.x + xshift
        node.y = node.y + yshift
    });

    return nodes
}



//todo: delete?
function nodeNeighborhood(node, forceGraph) {
    const links = forceGraph.graphData().links;
    const nodes = forceGraph.graphData().nodes;

    const connectedLinks = links.filter(link => link.class === "edge" && (link.sourceid === node.nodeid || link.targetid === node.nodeid));
    const neighborNodeIds = new Set(connectedLinks.flatMap(link => [link.sourceid, link.targetid]));
    //include both neighbors and self 
    neighborNodeIds.add(node.nodeid);

    const boundingNodes = Array.from(neighborNodeIds).map(id => nodes.find(n => n.nodeid === id));    
    const bounds = findNodeBounds(boundingNodes);
    const maxDimension = Math.max(bounds.maxX - bounds.minX, bounds.maxY - bounds.minY);

    return { x: node.x - maxDimension/2, 
             y: node.y - maxDimension/2, 
             width: maxDimension, 
             height: maxDimension };
}


