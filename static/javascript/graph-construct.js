
const XSCALE_NODE = 1
const YSCALE_NODE = 1

const KINK_SIZE = 100
const NODE_SEGMENT_WIDTH = 21
const SINGLE_NODE_THRESH = 6
const EDGE_LENGTH = 10
const EDGE_WIDTH = 2

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
        if (n === 1) {
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
        newLink["annotations"] = []
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
        
        nodeInfo[nodeid] = node
        //node = scale_node(node)
        INIT_POSITIONS[nodeid] = get_coordinates(node)
        NODEIDS[nodeid] = [];

        for (let i = 0; i < n; i++) {
            let newNode = {};
            newNode["nodeid"] = nodeid;
            newNode["__nodeid"] = `${nodeid}#${i}`;
            newNode["__nodeidx"] = i;
            NODEIDS[nodeid].push(newNode["__nodeid"]); 
            newNode["class"] = (i === 0 || i === n-1) ? "end" : "mid";
            
            ["chrom", "start", "end", "subtype"].forEach(key => {
                if (node.hasOwnProperty(key)) {
                    newNode[key] = node[key];
                }
            });

            let xy = get_coordinates(node, n, i)
            newNode["x"] = xy[0];
            newNode["y"] = xy[1];

            newNode["type"] = node["type"];

            newNode["isref"] = node.hasOwnProperty("chrom");
            newNode["annotations"] = [];

            graphNodes.push(newNode);

            if (i != 0){
                let newLink = {};
                newLink["source"] = `${nodeid}#${i-1}`;
                newLink["target"] = newNode["__nodeid"];
                newLink["nodeid"] = nodeid;
                newLink["class"] = "node";
                newLink["type"] = node["type"];
                newLink["length"] = length / n;
                newLink["width"] = NODE_SEGMENT_WIDTH;
                newLink["annotations"] = []
                graphLinks.push(newLink);
            }
        }
    });

    return [graphNodes, graphLinks];
}


function store_annotations(annotations) {
    filteredAnnotations = annotations.filter(a => a.type === "gene");
    filteredAnnotations.forEach(annotation => {
        annotationInfo[annotation.aid] = annotation;
    });
}

function is_overlap(annotation, node) {
    // TODO: check for chromosome name??
    if (node.start == null){ return false }

    if (node.start <= annotation.end && node.end >= annotation.start){
        var pointPosition = calculate_effective_position(node);
        return pointPosition >= annotation.start && pointPosition <= annotation.end;
    }
}

function calculate_effective_position(node){
    if (!node.hasOwnProperty("start")){
        return null;
    }
    var start = node.start;
    var end = node.end;
    var n = NODEIDS[node.nodeid].length;
    var i = node.__nodeidx;

    if (n === 1){
        return (start+end)/2;
    }
    if (i === n-1){
        return end;
    }

    return (start + i*(end-start)/(n-1));
}

function update_annotations(graph) {

    var annotationSet, aid;
    Object.values(annotationInfo).forEach(annotation => {
        annotationSet = new Set();
        aid = annotation.aid;
        graph.nodes.forEach(node => {
            node["annotations"] = []
            if(is_overlap(annotation, node)){
                annotationSet.add(node.__nodeid);
                node.annotations.push(aid);
            }
        });

        var source, target;
        graph.links.forEach(link => {
            link["annotations"] = [];

            //link could be a link object or simple dictionary
            source = (typeof link.source === 'string') ? link.source : link.source.__nodeid;
            target = (typeof link.target === 'string') ? link.target : link.target.__nodeid;

            // TODO: partial annotation on link?
            if (annotationSet.has(source) && annotationSet.has(target)){
                link.annotations.push(aid);
            }

        });

    });
    return graph;
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
    
    links = process_edge_links(links);
    
    graph.nodes = graph.nodes.concat(nodes);
    graph.links = graph.links.concat(links).concat(nodeLinks);
    graph = update_annotations(graph);

    return graph;
}

function process_graph_data(data){
    
    store_annotations(data.annotations);

    let result = process_nodes(data.nodes);
    let nodes = result[0];
    let nodeLinks = result[1];

    let links = process_edge_links(data.links);
    var graph = {"nodes": nodes, "links": links.concat(nodeLinks)}
    update_annotations(graph)

    return graph;
}
