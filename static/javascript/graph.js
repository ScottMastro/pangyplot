function force(alpha) {
    for (let i = 0, n = nodes.length, node, k = alpha * 0.1; i < n; ++i) {
      node = nodes[i];
      node.vx -= node.x * k;
      node.vy -= node.y * k;
    }
  }

function replace_bubbles(data){
    console.log(data["bubbles"])


}

function draw_graph(graph){
    replace_bubbles(graph)

    const canvas = document.getElementById('graph');

    //console.log({"nodes": layout[0], "links": layout[1].concat(edges)})
    
    console.log(graph)

    const Graph = ForceGraph()(canvas)
        .backgroundColor('#101020')
        .nodeVal(node => node["size"])
        .nodeRelSize(6)
        .nodeId('id')
        .nodeLabel('nodeid')
        .linkLabel('group')
        .nodeAutoColorBy('group')
        .linkAutoColorBy("group")
        .linkWidth("width")
        .graphData(graph)
        .velocityDecay(0.1)
        .d3Force('link').distance(link => link["length"] )

        //.linkDirectionalParticles(10)

        //.warmupTicks(3)
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
            console.log(data)
            draw_graph(data)
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send();
}

fetch("chr7", 142747350, 142775343)

