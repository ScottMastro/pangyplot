function parseTabSeparatedLayout(tsv) {
    let nodes = [];
    let i = 0;
    d3.tsv(tsv, function(data) {
        if (i % 2 == 0){
            nodes.push([[parseFloat(data.X), parseFloat(data.Y)]]);
        } else {
            nodes[nodes.length - 1].push([parseFloat(data.X), parseFloat(data.Y)]);
        }    
        i = i+1;
    });

    return nodes;

}

let nodes = parseTabSeparatedLayout("https://raw.githubusercontent.com/ScottMastro/example_graph_data/master/data/DRB1-3123_sorted.lay.tsv")
//console.log(nodes);

function parseGfa(gfa) {
    let edges = [];

    d3.tsv(gfa, function(data) {
        if (data["#0"] == "L"){
            let n1 = parseInt(data["1"]);
            let n2 = parseInt(data["3"]);
            
            let node_coord1=nodes[n1-1][1];
            let node_coord2=nodes[n2-1][0];
                
            edges.push([node_coord1, node_coord2, n1,n2])
        }
    });
    return edges
}

let edges = parseGfa("https://raw.githubusercontent.com/ScottMastro/example_graph_data/master/data/DRB1-3123.gfa")
console.log(edges);
