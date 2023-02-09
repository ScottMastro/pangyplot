function draw_graph(graph){
    const canvas = document.getElementById('graph');

    //console.log({"nodes": layout[0], "links": layout[1].concat(edges)})
    
    console.log(graph)

    const Graph = ForceGraph()(canvas)
        .backgroundColor('#101020')
        .nodeRelSize(6)
        .nodeAutoColorBy('group')
        .linkAutoColorBy("group")
        .linkWidth("width")
        .linkDirectionalParticles(1)
        .graphData(graph);
        
       //.nodeLabel(node => `${node.user}: ${node.description}`)

}


function fetch(chromosome, start, end) {

    let url = "/select?chromosome=" + chromosome;
    url = url + "&start=" + start;
    url = url + "&end=" + end;

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var data = JSON.parse(xmlHttp.response)
            draw_graph(data)
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send();
}

fetch("chr18", 0, 100000)

