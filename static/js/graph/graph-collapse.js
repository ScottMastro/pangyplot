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

function mark_nodes_collapsable(graph, linkDict, simpleOnly=false, maxSize=0){
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

function collapse(graph, linkDict, canCollapseDict, maxSize=0){
    var collapsePointer = {};
    var collapseSubgraphs = [];

    let nodeInfoDict = {};
    graph.nodes.forEach(node => {
        nodeInfoDict[node.nodeid] = node;
    });
    let linkStack = [];
    let source, target, sourceSize, targetSize, i,j;
    graph.links.forEach(link => {
        if (link.class === "node"){
            linkStack.push(link);
        }
        if (link.class === "edge"){
            source = (typeof link.source === 'string') ? link.sourceid : link.source.nodeid;
            target = (typeof link.target === 'string') ? link.targetid : link.target.nodeid;
            
            if(canCollapseDict[source] || canCollapseDict[target]){
                sourceSize = nodeInfoDict[source]["length"] || nodeInfoDict[source]["size"];
                targetSize = nodeInfoDict[target]["length"] || nodeInfoDict[target]["size"];
                if (sourceSize < targetSize){
                    if (source in collapsePointer){ i = collapsePointer[source]; }
                    else { 
                        i = collapseSubgraphs.length;
                        collapseSubgraphs.push({"nodes":[], "links":[]});
                        collapsePointer[source] = i;
                    }

                    if (target in collapsePointer){
                        j = collapsePointer[target];
                        collapseSubgraphs[i].links = collapseSubgraphs[i].links.concat(collapseSubgraphs[j].links);
                        collapseSubgraphs[j].links = []
                        collapsePointer[target] = i;

                    }
                    

                } else {
                    if (target in collapsePointer){ i = collapsePointer[target]; }
                    else { 
                        i = collapseSubgraphs.length;
                        collapseSubgraphs.push({"nodes":[], "links":[]});
                        collapsePointer[target] = i;
                    }
                }
            }


        }
    });

    return(collapseSubgraphs);
}


function collapse_nodes(graph){

    var linkDict = create_link_dicts(graph);
    var canCollapseDict = mark_nodes_collapsable(graph, linkDict);
    var collapseSubgraphs = collapse(graph, linkDict, canCollapseDict, maxSize=0);

    console.log(collapseSubgraphs);

    //graph.nodes.forEach(node => {


    return graph
}
