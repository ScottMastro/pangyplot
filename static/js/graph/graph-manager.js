

function processGraphData(rawGraph){

    const nodeResult = processNodes(rawGraph.nodes);
    const links = processLinks(rawGraph.links);
    
    const graph = {"nodes": nodeResult.nodes, "links": links.concat(nodeResult.nodeLinks)}
    console.log("look here",graph);

    document.dispatchEvent(new CustomEvent("updatedGraphData", { detail: { graph: graph } }));

}


function processSubgraphData(subgraph, originNode, graph){
    graph = FORCE_GRAPH.graphData();

    const nodeResult = processNodes(subgraph.nodes);

    nodeResult.nodes = shiftCoordinates(nodeResult.nodes, originNode);
    graph = delete_node(graph, originNode.nodeid);

    let links = filter_raw_links(subgraph.links);
    
    links = processLinks(links);
    
    graph.nodes = graph.nodes.concat(nodeResult.nodes);
    graph.links = graph.links.concat(links).concat(nodeResult.nodeLinks);


    updateGraphData(graph);


    GETTING_SUBGRAPH.delete(originNode.nodeid);
    if (GETTING_SUBGRAPH.size === 0) {
        hideLoader();
    }
    HIGHLIGHT_NODE = null;

    const data = { graph: graph };
    document.dispatchEvent(new CustomEvent("updatedGraphData", { detail: data }));



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


