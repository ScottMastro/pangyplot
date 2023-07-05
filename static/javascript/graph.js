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
        node.vy += node.y * k/6;
    }
}


function highlight_node(node, ctx, shift, size, color) {
    ctx.beginPath();
    ctx.arc(node.x+shift, node.y+shift, size, 0, 2 * Math.PI, false);
    ctx.fillStyle = color;
    ctx.fill();
}

function highlight_link(link, ctx, shift, width, color) {
    ctx.beginPath();
    ctx.moveTo(link.source.x+shift, link.source.y+shift);
    ctx.lineTo(link.target.x+shift, link.target.y+shift);
    ctx.lineWidth = width;
    ctx.strokeStyle = color;
    ctx.stroke();
}

function add_text(text, ctx, size, color, x, y) {
    ctx.beginPath();
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = 'darkgrey';

    ctx.font = size.toString() + 'px Sans-Serif';
    ctx.fillStyle = color;
    ctx.fillText(text, x, y);
    ctx.restore();
}

function add_rect(text, ctx, size, color, x, y) {
    ctx.beginPath();
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = 'darkgrey';

    ctx.font = size.toString() + 'px Sans-Serif';
    ctx.fillStyle = color;
    ctx.fillText(text, x, y);
    ctx.restore();
}

function intToColor(seed) {
    var a = 1664525;
    var c = 1013904223;
    var m = Math.pow(2, 32);

    // Generate three random numbers between 0 and 255
    var red = (seed * a + c) % m;
    seed = (red * a + c) % m;
    var green = seed;
    seed = (green * a + c) % m;
    var blue = seed;

    // Normalize to the range 0-255
    red = Math.floor((red / m) * 256);
    green = Math.floor((green / m) * 256);
    blue = Math.floor((blue / m) * 256);

    // Convert to a hexadecimal string and pad with zeros if necessary
    red = ("00" + red.toString(16)).slice(-2);
    green = ("00" + green.toString(16)).slice(-2);
    blue = ("00" + blue.toString(16)).slice(-2);

    // Combine into a single color string
    var color = "#" + red + green + blue;
    return color;
}

function draw_graph(graph){

    const canvas = document.getElementById('graph');

    //console.log({"nodes": layout[0], "links": layout[1].concat(edges)})

    let nodeIdCounter = 0, linkIdCounter = 0;
    let nodes = [], links = [];
    console.log(graph);

    annotationDict = {}
    for (let i = 0, n = graph.annotations.length; i < n; ++i) {
        annotationDict[graph.annotations[i].index] = graph.annotations[i];
    }

    for (let j = 0, m = graph.annotations.length, annotation; j < m; ++j) {
        annotation = graph.annotations[j];

        for (let i = 0, n = graph.nodes.length, node; i < n; ++i) {
            node = graph.nodes[i];

            if (annotation.start <= node.pos && annotation.end >= node.pos){
                node["annotate"] = 2;
            }

        }
    }

    
    const updateGraphData = () => {
        const lastZoom = 1;
        Graph.graphData({ nodes: graph["nodes"], links: graph["links"] });
        };
    


        function linkWidth(link) 
        {
            return Math.max(2, lastZoom*link["width"]);
        }

        
        SHIFT=0
        

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
            .linkColor(link => intToColor(link.group))
            .linkWidth(linkWidth)
            .d3VelocityDecay(0.2)
            .nodeCanvasObject(highlight_node)
            .autoPauseRedraw(false) // keep redrawing after engine has stopped
            .onNodeClick(node => {
                console.log(node);

                newNodes = node["expand_nodes"]
                for (let i = 0, n = newNodes.length; i < n; ++i) {
                    newNode = newNodes[i];
                    newNode.x = node.x
                    newNode.y = node.y
                }

                graph["links"] = graph["links"].filter(l => l.source !== node && l.target !== node);
                graph["nodes"] = graph["nodes"].filter(n => n !== node);

                for (let i = 0, n = newNodes.length; i < n; ++i) {

                }

    
                graph["nodes"] = graph["nodes"].concat(newNodes);
                graph["links"] = graph["links"].concat(node["expand_links"]);

                updateGraphData();

            });

                
            //.onBackgroundClick(event => {
            //    console.log(Graph.graphData());
            //    force(Graph, 1)
            //    let coords = Graph.screen2GraphCoords(event.layerX, event.layerY);
            //    let nodeId = nodeIdCounter ++;
            //    graph["nodes"].push({ id: nodeId, x: coords.x, y: coords.y, name: 'newnode_' + nodeId });
            //    updateGraphData();
            //});
            //.linkWidth(link => {console.log(link); return 4})



        function linkStrength(link) 
        {

            scale=0.5
            if (link.type == "node"){
                return (1/4)/scale;
            }
            if (link.type == "edge"){
                return (1/2)/scale;
            }

            return (1/2)/scale;
        }

        function linkDistance(link) 
        {
            if (link.type == "node"){
                return link.length;
            }
            if (link.type == "edge"){
                return 5;
            }
            return 5;
        }

        Graph.d3Force('link').distance(linkDistance).iterations(2)
        //Graph.d3Force('center').strength(0.00005);
        
        //Graph.d3Force('link').distance(link => link["length"] )
        Graph.d3Force('collide', d3.forceCollide(50).radius(20))
        //Graph.d3Force('collide', null)

        Graph.d3Force('charge').strength(-30).distanceMax(500)

        Graph.minZoom(0.01)
        Graph.maxZoom(1e100)


        Graph.nodeCanvasObject((node, ctx) => nodePaint(node, ctx))
  
        function nodePaint(node, ctx) {
            shape = 0;
            if (node.shape != null){
                shape = node.shape;
            }

            id = 0;
            x = node.x;
            y = node.y;
            size = node.size;
            ctx.fillStyle = intToColor(node.group);
            ctx.strokeStyle = intToColor(node.group);
            [
                () => { ctx.beginPath(); ctx.arc(x, y, size, 0, 2 * Math.PI, false); ctx.fill(); }, // circle
                () => { ctx.fillRect(x - 6, y - 4, 12, 8); }, // rectangle
                () => { ctx.beginPath(); ctx.arc(x, y, size, 0, 2 * Math.PI, false); ctx.lineWidth = 3; ctx.stroke(); ctx.fillStyle = "#101020"; ctx.fill();}, // x
                () => { ctx.beginPath(); ctx.moveTo(x - size, y - size);  ctx.lineTo(x + size, y + size); ctx.moveTo(x + size, y - size); ctx.lineTo(x - size, y + size); ctx.stroke(); }, // x
                () => { ctx.beginPath(); ctx.moveTo(x, y - 5); ctx.lineTo(x - 5, y + 5); ctx.lineTo(x + 5, y + 5); ctx.fill(); }, // triangle
                () => { ctx.font = '10px Sans-Serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('Text', x, y); } // text
            ][shape]();
            }

        Graph.onRenderFramePre((ctx, scale) => {

            lastZoom = ctx.canvas.__zoom["k"];
            ctx.save();

            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = 'darkgrey';

            let nodes = Graph.graphData()["nodes"]
            for (let i = 0, n = nodes.length, node; i < n; ++i) {
                node = nodes[i];

                node.annotations.sort(function(a, b) {
                    return a - b;
                  });

                for (let j = 0, m = node.annotations.length; j < m; ++j) {
                    if (annotationDict[node.annotations[j]].type == "gene"){
                        highlight_node(node, ctx, 0, Math.max(40, 40*(1/lastZoom/10)), intToColor(node.annotations[j]));
                    }
                }
            }
            
            let links = Graph.graphData()["links"]
            for (let i = 0, n = links.length, link; i < n; ++i) {
                 link = links[i];

                 link.annotations.sort(function(a, b) {
                    return a - b;
                  });

                for (let j = 0, m = link.annotations.length; j < m; ++j) {
                    if (annotationDict[link.annotations[j]].type == "gene"){
                        highlight_link(link, ctx, 0, Math.max(80, 80*(1/lastZoom/10)), intToColor(link.annotations[j]));
                    }
                }



            }
            
            //group_box = Graph.getGraphBbox((node) => node.annotate == 2);
            //console.log(ctx.canvas.__zoom);
        
            //console.log(group_box)
            //const x = group_box.x[0];
            //const y = group_box.y[0];
            //const width = group_box.x[1] - group_box.x[0];
            //const height = group_box.y[1] - group_box.y[0];
            //const color = "blue";

            //ctx.fillStyle = color;
           // ctx.fillRect(x, y, width, height);

            //add_text('genename', ctx, 72, "lightgrey", x + width/2, y + height/2)

        
            
            ctx.restore();
         });


         let highlightNodes = [];
         
        Graph.onRenderFramePost((ctx, scale) => {

            ctx.save();


            annotationNodesX = {};
            annotationNodesY = {};

            let nodes = Graph.graphData()["nodes"]
            for (let i = 0, n = nodes.length, node; i < n; ++i) {
                node = nodes[i];

                for (let j = 0, m = node.annotations.length, k; j < m; ++j) {
                    k = node.annotations[j]

                    if (!annotationNodesX.hasOwnProperty(k)) {
                        annotationNodesX[k] = [];
                        annotationNodesY[k] = [];
                    }
                    annotationNodesX[k].push(node.x)
                    annotationNodesY[k].push(node.y);
                } 
            }

            for (var k in annotationNodesX) {

                if (annotationDict[k].type != "gene"){
                    continue;
                }

                var n = annotationNodesX[k].length
                var sumX = annotationNodesX[k].reduce(function(a, b){
                    return a + b;
                }, 0);
                var sumY = annotationNodesY[k].reduce(function(a, b){
                    return a + b;
                }, 0);

                var xpos = sumX/n;
                var ypos = sumY/n;
            
    
                ctx.shadowColor = 'rgba(0, 0, 0, 0.8)'; // Shadow color
                ctx.shadowBlur = 4; // How much the shadow should blur
                ctx.shadowOffsetX = 5; // Horizontal distance of the shadow from the text
                ctx.shadowOffsetY = 5; // Vertical distance of the shadow from the text
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillStyle = 'darkgrey';
            
                ctx.font = Math.max(72, 72*(1/lastZoom/10)).toString() + 'px Sans-Serif';
                ctx.fillStyle = "lightgrey";

                
                ctx.fillText(annotationDict[k].gene, xpos, ypos);
    
                
            }
            

            for (let i = 0, n = highlightNodes.length, node; i < n; ++i) {
                node = highlightNodes[i];
                highlight_node(highlightNodes[i], ctx, 0, 20, "pink")

                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillStyle = 'darkgrey';
                ctx.font = '24px Sans-Serif';
    
                ctx.shadowColor = 'rgba(0, 0, 0, 0.8)'; // Shadow color
                ctx.shadowBlur = 4; // How much the shadow should blur
                ctx.shadowOffsetX = 5; // Horizontal distance of the shadow from the text
                ctx.shadowOffsetY = 5; // Vertical distance of the shadow from the text
                if (node.length != null){
                    ctx.fillText(node["chrom"]+":"+node["pos"], node.x, node.y);
                }
            }

            //for (let i = 0, n = annotation["nodes"].length; i < n; ++i) {
            

                        
            ctx.restore();
         });



        Graph.onNodeHover(node => {
            highlightNodes = [];
            highlightLinks = [];
            if (node) {
                highlightNodes.push(node);
                //node.toNodes.forEach(link => highlightLinks.add(link));
            }
            hoverNode = node || null;
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

fetch("chrM", 0, 142775343)

