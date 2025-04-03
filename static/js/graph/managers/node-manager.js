var NODEIDS = {};
var NODE_INFO = {};

const KINK_SIZE = 100;
const MAX_KINKS = 20;
const NODE_WIDTH=50;

const SINGLE_NODE_THRESH = 6;

function nodeSourceId(nodeid){
    return NODEIDS[nodeid][NODEIDS[nodeid].length-1];
}
function nodeTargetId(nodeid){
    return NODEIDS[nodeid][0];
}

function filterBadLinks(rawLinks){
    return rawLinks.filter(l => l.source in NODEIDS && l.target in NODEIDS )
}

function getNodeInformation(nodeid){
    return NODE_INFO[nodeid];
}

function nodeidSplit(__nodeid){
    return __nodeid.split("#")[0];
}

function countNodeKinks(nodeid){
    return NODEIDS[nodeid].length;
}

function calculateEffectiveNodePosition(node){
    if (!node.hasOwnProperty("start")){
        return null;
    }
    const start = node.start;
    const end = node.end;
    const n = countNodeKinks(node.nodeid);
    const i = node.__nodeidx;

    if (n === 1){
        return (start+end)/2;
    }
    if (i === n-1){
        return end;
    }

    return (start + i*(end-start)/(n-1));
}

function getCoordinates(node, n=1, i=0){
    let x, y;

    if (n === 1) {

        if (node.hasOwnProperty("x") && node.hasOwnProperty("y")) {
            x = node["x"];
            y = node["y"];
        } else {
            x = (node["x1"] + node["x2"]) / 2;
            y = (node["y1"] + node["y2"]) / 2;
        }

    } else {
        let p = 1-(i / (n - 1));
        p = Math.max(0, p);
        p = Math.min(1, p);
        x = p * node["x1"] + (1 - p) * node["x2"];
        y = p * node["y1"] + (1 - p) * node["y2"];
    }

    return {x:x, y:y}
}

function getNodeLength(node) {
    return node.hasOwnProperty("length") ? node["length"] : node["size"];
}

function calculateNumberOfKinks(nodeLength) {
    let n = (nodeLength < SINGLE_NODE_THRESH) ? 1 : Math.floor(nodeLength / KINK_SIZE) + 2;
    return Math.min(n, MAX_KINKS);
}

function createNewNode(node, nodeid, idx, totalKinks) {
    let coords = getCoordinates(node, totalKinks, idx);
    let seqLength = 0;
    let largestChild = 0;

    if (node.type == "segment") {
        seqLength = node.length;
    } else {
        seqLength = node.size;
        largestChild = node.largest_child;
    }

    let newNode = {
        nodeid,
        __nodeid: `${nodeid}#${idx}`,
        __nodeidx: idx,
        class: (idx === 0 || idx === totalKinks - 1) ? "end" : "mid",
        x: coords.x,
        y: coords.y,
        initX: coords.x,
        initY: coords.y,
        type: node.type,
        seqLen: seqLength,
        isHighlight: false,
        isSelected: false,
        isVisible: true,
        isDrawn: true,
        size: NODE_WIDTH,
        largestChild: largestChild,
        isSingleton: totalKinks === 1,
        isRef: node.is_ref,
        gcCount: node.gc_count,
        annotations: []
    };

    //if (newNode.class == "end" && ! newNode.isSingleton){
    //    newNode.fx = coords.x;
    //    newNode.fy = coords.y;
    //}

    ["chrom", "start", "end", "subtype"].forEach(key => {
        if (node.hasOwnProperty(key)) {
            newNode[key] = node[key];
        }
    });

    return newNode;
}


function createNewNodeLink(node, nodeid, idx, totalKinks, nodeLength) {
    //console.log(`${nodeid}#${idx - 1}`, `${nodeid}#${idx}`)
    return {
        source: `${nodeid}#${idx - 1}`,
        target: `${nodeid}#${idx}`,
        nodeid,
        isVisible: true,
        isDrawn: true,
        class: "node",
        type: node["type"],
        width: NODE_WIDTH,
        length: Math.min(nodeLength / totalKinks, 1000),
        force: LINK_FORCE,
        isRef: node.is_ref,
        annotations: []
    };
}

function createNewTextNode(node) {
    let newNode = {
        __nodeid: node.nodeid,
        x: node.x,
        y: node.y,
        class: "text",
        type: node.type,
        text: node.text,
        anchorX: node.x,
        anchorY: node.y,
        isVisible: true,
        isDrawn: true,
    };

    return newNode;
}

function processNodes(rawNodes) {
    let nodes = [];
    let nodeLinks = [];

    rawNodes.forEach(rawNode => {
        const nodeLength = getNodeLength(rawNode);
        const numberOfKinks = calculateNumberOfKinks(nodeLength);
        const nodeid = String(rawNode.nodeid);

        NODEIDS[nodeid] = [];
        NODE_INFO[nodeid] = rawNode;

        for (let i = 0; i < numberOfKinks; i++) {
            const newNode = createNewNode(rawNode, nodeid, i, numberOfKinks);
            nodes.push(newNode);
            NODEIDS[nodeid].push(newNode.__nodeid);

            if (i !== 0) {
                const newLink = createNewNodeLink(newNode, nodeid, i, numberOfKinks, nodeLength);
                nodeLinks.push(newLink);
            }
        }
    });
    
    return { nodes: nodes, nodeLinks: nodeLinks };
}

const XSCALE_NODE = 1
const YSCALE_NODE = 1

function scale_node(node){
    if (node.hasOwnProperty("x") && node.hasOwnProperty("y")) {
        node.x = node.x * XSCALE_NODE;
        node.y = node.y * YSCALE_NODE;
    }
    node.x1 = node.x1 * XSCALE_NODE;
    node.x2 = node.x2 * XSCALE_NODE;
    node.y1 = node.y1 * YSCALE_NODE;
    node.y2 = node.y1 * YSCALE_NODE;
    return node
}
