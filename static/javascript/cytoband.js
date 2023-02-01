function get_longest_size(data) {
    let longest = -1;
    for (const [key, chr] of Object.entries(data)) {
        for (var j = 0; j < chr.length; j++) {
            if (chr[j]["end"] > longest){
                longest = chr[j]["end"];
            }
        }
    }
    return longest;
}

function draw_genome_(data) {

    let width = 1000;
    let height = 200;
    var shift = 5;

    let chr_width = 10;
    let gap = 15;
    let scale = height - (shift * 2);

    var svg = d3.select("#genome")
	.append("svg")
	.attr("width", width)
	.attr("height", height);
    
    let longest = get_longest_size(data);
    let i = 1;
    for (const [key, value] of Object.entries(data)) {
        let x_ = (gap+chr_width)*i
        
        var rects = svg.selectAll("foo")
            .data(value)
            .enter()
            .append("rect")
            .attr("x", x_-shift)
            .attr("y", 0)
            .attr("rx", 4)
            .attr("ry", 4)
            .attr("width", chr_width+shift*2)
            .attr("height", scale + shift*2)
            .attr("fill", "#222222");

        var rects = svg.selectAll("foo")
            .data(value)
            .enter()
            .append("rect")
            .attr("x", x_)
            .attr("y", d=> scale*(d.end/longest) + shift)
            .attr("width", chr_width)
            .attr("height", d=> ((d.end-d.start)/longest *scale) )
            .attr("fill", d=> d.color);
        

        i=i+1;
    }


}


function draw_chromosome_(data) {

    let width = 1000;
    let height = 200;

    let height_scale = 0.5;
    let front_gap = 10;
    let back_gap = 10;
    let scale = width;

    var svg = d3.select("#chromosome")
	.append("svg")
	.attr("width", width)
	.attr("height", height);
    
    console.log(data);

    var rects = svg.selectAll("foo")
        .data(data)
        .enter()
        .append("rect")
        .attr("x", d=> (front_gap + d.x*scale))
        .attr("y", 0)
        .attr("width", d=> (d.size*scale))
        .attr("height", height*height_scale)
        .attr("fill", d=> d.color);

    const annotations = []
    for (var i = 0; i < data.length; i++) {
        annotations.push(
            {note: {label: data[i]["name"]},
            x: (front_gap + data[i]["x"]*scale) + (data[i]["size"]*scale)/2,
            y: height*height_scale,
            dy: 10,
            dx: 0,
            });
    }
    annotations.map(function(d){ d.color = "#E8336D"; return d})
    console.log(annotations);

    const makeAnnotations = d3.annotation()
        .type(d3.annotationLabel)
        .annotations(annotations);

    d3.select("#chromosome")
        .select("svg")
        .append("g")
        .attr("class", "annotation-group")
        .call(makeAnnotations);
}

function draw_genome() {
    let url = "/cytoband"
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var data = JSON.parse(xmlHttp.response)
            draw_genome_(data);
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send();
}

function draw_chromosome(chromosome) {
    let url = "/cytoband?chromosome=" + chromosome;
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var data = JSON.parse(xmlHttp.response)
            draw_chromosome_(data[chromosome]);
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send();
}


draw_genome();
draw_chromosome("chr18");
