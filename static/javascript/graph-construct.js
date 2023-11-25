
const XSCALE_NODE = 1
const YSCALE_NODE = 1

const KINK_SIZE = 100
const NODE_SEGMENT_WIDTH = 21
const SINGLE_NODE_THRESH = 6
const EDGE_LENGTH = 10
const EDGE_WIDTH = 4

var INIT_POSITIONS = {}
var NODEIDS = {}

function source_id(nodeid){
    return NODEIDS[nodeid][NODEIDS[nodeid].length-1]
}
function target_id(nodeid){
    return NODEIDS[nodeid][0]
}

function nodeid_split(nodeid){
    return nodeid.split("#")[0];
}

function get_coordinates(node, n=1, i=0){
    let x, y;
    if (node.hasOwnProperty("x") && node.hasOwnProperty("y")) {
        x = node["x"];
        y = node["y"];
    } else {
        if (n == 1) {
            x = (node["x1"] + node["x2"]) / 2;
            y = (node["y1"] + node["y2"]) / 2;
        } else {
            let p = 1-(i / (n - 1));
            p = Math.max(0, p);
            p = Math.min(1, p);
            x = p * node["x1"] + (1 - p) * node["x2"];
            y = p * node["y1"] + (1 - p) * node["y2"];
        }
    }

    return [x,y]
}

function process_edge_links(links) {
    let graphLinks = [];
    links.forEach(link => {
        let newLink = {};
        newLink["source"] = source_id(link["source"]);
        newLink["target"] =  target_id(link["target"]);
        newLink["sourceid"] = String(link["source"]);
        newLink["targetid"] = String(link["target"]);
        newLink["class"] = "edge";
        newLink["length"] = EDGE_LENGTH;
        newLink["width"] = EDGE_WIDTH;
        graphLinks.push(newLink);
    });

    return graphLinks;
}

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

function process_nodes(nodes) {

    const graphNodes = [];
    const graphLinks = [];

    nodes.forEach(node => {
        let length = node.hasOwnProperty("length") ? node["length"] : node["size"];
        let n = (length < SINGLE_NODE_THRESH) ? 1 : Math.floor(length / KINK_SIZE) + 2;
        let nodeid = String(node.nodeid)
        
        node = scale_node(node)
        INIT_POSITIONS[nodeid] = get_coordinates(node)
        NODEIDS[nodeid] = [];

        for (let i = 0; i < n; i++) {
            let newNode = {};
            newNode["nodeid"] = nodeid;
            newNode["__nodeid"] = `${nodeid}#${i}`;
            NODEIDS[nodeid].push(newNode["__nodeid"]); 
            newNode["id"] = String(node["id"]);
            newNode["class"] = (i == 0 || i == n-1) ? "end" : "mid";
            
            ["chrom", "start", "end", "subtype"].forEach(key => {
                if (node.hasOwnProperty(key)) {
                    newNode[key] = node[key];
                }
            });

            let xy = get_coordinates(node, n, i)
            newNode["x"] = xy[0];
            newNode["y"] = xy[1];

            newNode["type"] = node["type"]
            newNode["isref"] = node.hasOwnProperty("chrom");

            graphNodes.push(newNode);

            if (i != 0){
                let newLink = {};
                newLink["source"] = `${nodeid}#${i-1}`;
                newLink["target"] = newNode["__nodeid"];
                newLink["class"] = "node";
                newLink["type"] = node["type"];
                newLink["length"] = length / n;
                newLink["width"] = NODE_SEGMENT_WIDTH;
                graphLinks.push(newLink);
            }
        }
    });

    return [graphNodes, graphLinks];
}

function process_graph(graph){
    
    let result = process_nodes(graph.nodes);
    let nodes = result[0];
    let nodeLinks = result[1];

    let links = process_edge_links(graph.links);
    
    return {"nodes": nodes, "links": links.concat(nodeLinks),
     "annotations": graph.annotations};
}


function adjust_positions(nodes, originNode){
    let initPos = INIT_POSITIONS[originNode.nodeid]
    let xshift = originNode.x - initPos[0]
    let yshift = originNode.y - initPos[1]

    nodes.forEach(node => {
        node.x = node.x + xshift
        node.y = node.y + yshift
    });

    return nodes
}

function delete_node(graph, nodeid){
    graph.links = graph.links.filter(l => l.source.nodeid != nodeid && l.target.nodeid != nodeid );
    graph.nodes = graph.nodes.filter(n => nodeid != n.nodeid);

    delete NODEIDS["nodeid"];

    return graph
}

function filter_raw_links(links){
    return links.filter(l => l.source in NODEIDS && l.target in NODEIDS );
}

function process_subgraph(subgraph, originNode, graph){
    
    console.log(subgraph)
    let result = process_nodes(subgraph.nodes);
    let nodes = result[0];
    let nodeLinks = result[1];

    nodes = adjust_positions(nodes, originNode);
    graph = delete_node(graph, originNode.nodeid);

    let links = filter_raw_links(subgraph.links);
    console.log(links)

    links = process_edge_links(links);
    
    graph.nodes = graph.nodes.concat(nodes);
    graph.links = graph.links.concat(links).concat(nodeLinks);


    return graph;
}
