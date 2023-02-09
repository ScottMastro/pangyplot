
var xmlHttp = new XMLHttpRequest();
xmlHttp.onreadystatechange = function() { 
    if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
        console.log(xmlHttp.responseText);
}
xmlHttp.open("GET", "/cytoband", true);
xmlHttp.send(null);

console.log("hi")


const GFA = "https://raw.githubusercontent.com/ScottMastro/example_graph_data/master/data/DRB1-3123_sorted.gfa"
const TSV = "https://raw.githubusercontent.com/ScottMastro/example_graph_data/master/data/DRB1-3123_sorted.lay.tsv"


const canvasDiv = document.getElementById("canvas");

const scaleX=1000
const scaleY=10
const height = 500
const width = 1200

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

let nodes = parseTabSeparatedLayout(TSV)
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

let edges = parseGfa(GFA)
//console.log(edges);


function drawGraph() {

    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height);

    function zoomed({transform}) {
        svg.attr("transform", transform);
    }
        
    svg.call(d3.zoom()
        .on("zoom", zoomed));
  
    console.log(nodes.length)

    for (let i = 1; i < nodes.length; i++) {

        svg.append("line")          // attach a line
        .style("stroke", "red")  // colour the line
        .attr("y1", nodes[i][0][1]/scaleY)
        .attr("x1", nodes[i][0][0]/scaleX)
        .attr("y1", nodes[i][0][1]/scaleY)
        .attr("x2", nodes[i][1][0]/scaleX)
        .attr("y2", nodes[i][1][1]/scaleY)

    }


    for (let i = 1; i < edges.length; i++) {

        svg.append("line")          // attach a line
        .style("stroke", "black")  // colour the line
        .style("stroke-width", 1)
        .attr("x1", edges[i][0][0]/scaleX)
        .attr("y1", edges[i][0][1]/scaleY)
        .attr("x2", edges[i][1][0]/scaleX)
        .attr("y2", edges[i][1][1]/scaleY)

    }
    
    canvasDiv.replaceChildren(svg.node());

    const newDiv = document.createElement("div");
    newDiv.textContent = "#nodes = " + nodes.length + " ------- #edges = " + edges.length ;
    canvasDiv.appendChild(newDiv);

    const newDiv2 = document.createElement("div");
    newDiv2.textContent = TSV;
    canvasDiv.appendChild(newDiv2);

    //svg
    //  .selectAll("circle")
    //  .data(layout)
    //  .join("circle")
    //    .attr("cx", d => d.X/scaleX)
    //    .attr("cy", d => d.Y/scaleY)
    //    .attr("r", d => Math.random() )
    //    .attr("fill", "skyblue");

}

