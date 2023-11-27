var hiddenParts = [];

function create_link_dicts(graph){
    var linkDict = {};
    let source, target;

    graph.links.forEach(link => {
        if (link.class === "edge"){
            source = (typeof link.source === 'string') ? link.sourceid : link.source.nodeid;
            target = (typeof link.target === 'string') ? link.targetid : link.target.nodeid;

            if (!(target in linkDict)){ 
                linkDict[target] = { "to": [], "from": [] };
            }if (!(source in linkDict)){
                linkDict[source] = { "to": [], "from": [] };
            }
            linkDict[target].to.push(source);
            linkDict[source].from.push(target);

        }
    });

    return(linkDict)
}

function mark_nodes_collapsable(graph, linkDict, simpleOnly=false){
    var canCollapseDict = {};

    let nodeid, check1, check2;
    graph.nodes.forEach(node => {
        nodeid = node.nodeid;
        if (!(nodeid in canCollapseDict)){
            if (!(nodeid in linkDict)){
                canCollapseDict[nodeid] = false;
            } else{
                check1 = linkDict[nodeid].to.length === 1;
                check2 = linkDict[nodeid].from.length === 1;
                canCollapseDict[nodeid] = check1 && check2;
           }
        }
    });

    return(canCollapseDict);
}



function collapse_nodes(graph){

    var linkDict = create_link_dicts(graph);
    var canCollapseDict = mark_nodes_collapsable(graph, linkDict);

    console.log(canCollapseDict);

    //graph.nodes.forEach(node => {


    return graph
}
