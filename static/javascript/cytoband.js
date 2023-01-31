let chrDiv = document.getElementById("chromosome")

const CHR_WIDTH = 1000
const CHR_HEIGHT = 200



function draw_chromosome(chromosome, data) {

    var svg = d3.select("#chromosome")
	.append("svg")
	.attr("width", CHR_WIDTH)
	.attr("height", CHR_HEIGHT);
    
    console.log(data["chr18"]);

    chrdata=data[chromosome]
    
    let height_scale = 0.5 
    let front_gap = 10
    let back_gap = 10
    let scale = CHR_WIDTH - front_gap - back_gap

    var rects = svg.selectAll("foo")
        .data(chrdata)
        .enter()
        .append("rect")
        .attr("x", d=> (front_gap + d.x*scale))
        .attr("y", 0)
        .attr("width", d=> (d.size*scale))
        .attr("height", CHR_HEIGHT*height_scale)
        .attr("fill", d=> d.color);
        const type = d3.annotationLabel

    const annotations = []
    for (var i = 0; i < chrdata.length; i++) {
        annotations.push(
            {note: {label: chrdata[i]["name"]},
            x: (front_gap + chrdata[i]["x"]*scale) + (chrdata[i]["size"]*scale)/2,
            y: CHR_HEIGHT*height_scale,
            dy: 10,
            dx: 0,
            })
    }
    annotations.map(function(d){ d.color = "#E8336D"; return d})
    console.log(annotations);

    const makeAnnotations = d3.annotation()
        .type(d3.annotationLabel)
        .annotations(annotations)

    d3.select("svg")
        .append("g")
        .attr("class", "annotation-group")
        .call(makeAnnotations)
}

function get_cytobands(chromosome="") {
    let url = "/cytoband"
    if (chromosome.length > 0){
        url = url + "?chromosome=" + chromosome;
    }
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var data = JSON.parse(xmlHttp.response)
            draw_chromosome("chr18", data);
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send();
}

get_cytobands()


