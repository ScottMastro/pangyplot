function force(alpha) {
    for (let i = 0, n = nodes.length, node, k = alpha * 0.1; i < n; ++i) {
      node = nodes[i];
      node.vx -= node.x * k;
      node.vy -= node.y * k;
    }
  }


function force(Graph, alpha) {

    let nodes = Graph.graphData().nodes
    for (let i = 0, n = nodes.length, node, k = alpha * 0.1; i < n; ++i) {
        node = nodes[i];
        node.vx += node.x * k;
        node.vy += node.y * k/2;
    }
}

function draw_graph(graph){

    const canvas = document.getElementById('graph');

    //console.log({"nodes": layout[0], "links": layout[1].concat(edges)})

    let nodeIdCounter = 0, linkIdCounter = 0;
    let nodes = [], links = [];

    
    const updateGraphData = () => {
        Graph.graphData({ nodes: graph["nodes"], links: graph["links"] });
        };
    
        function linkStrength(link) 
        {
          var stnval = 1 / (link.length);
          
          return 1;
        }

        function linkDistance(link) 
        {
            return link.length/10;
        }
        
        const Graph = ForceGraph()
        (document.getElementById('graph'))
            .graphData(graph)
            .backgroundColor('#101020')
            .nodeVal(node => node["size"])
            .nodeRelSize(6)
            .nodeId('id')
            .nodeLabel('id')
            .linkLabel('group')
            .nodeAutoColorBy('group')
            .linkAutoColorBy("group")
            .linkWidth("width")
            .d3VelocityDecay(0.1);

            //.onBackgroundClick(event => {
            //    console.log(Graph.graphData());
            //    force(Graph, 1)
            //    let coords = Graph.screen2GraphCoords(event.layerX, event.layerY);
            //    let nodeId = nodeIdCounter ++;
            //    graph["nodes"].push({ id: nodeId, x: coords.x, y: coords.y, name: 'newnode_' + nodeId });
            //    updateGraphData();
            //});

        Graph.d3Force('link').strength(linkStrength).distance(linkDistance)
        Graph.minZoom(0.01)
        Graph.maxZoom(1e100)

        //console.log(Graph.nodeId("1914_1"))

        Graph.onRenderFramePre((ctx, scale) => {

            //for (let i = 0, n = annotation["nodes"].length; i < n; ++i) {
            let annotation = graph["annotations"][0];
            
            let nodes = Graph.graphData()["nodes"]
            for (let i = 0, n = nodes.length, node; i < n; ++i) {
                node = nodes[i];
                if (annotation["nodes"].includes(node.id)){
                    node["annotate"] = 2;
                }
                
            }


            group_box = Graph.getGraphBbox((node) => node.annotate == 2);
            console.log(ctx)
            ctx.save();
        
            console.log(group_box)
            const x = group_box.x[0];
            const y = group_box.y[0];
            const width = group_box.x[1] - group_box.x[0];
            const height = group_box.y[1] - group_box.y[0];
            const color = "blue";

            ctx.fillStyle = color;
            ctx.fillRect(x, y, width, height);

            ctx.font = '72px Sans-Serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = 'darkgrey';
            ctx.fillText('genename ', x + width/2, y + height/2);
    
            ctx.restore();
         });


         //.linkDirectionalParticles(10)
        //            .nodeLabel('nodeid')


        //.warmupTicks(3)
        //.nodeLabel(node => `${node.user}: ${node.description}`)
        updateGraphData();

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

fetch("chr7", 142747350, 142775343)

