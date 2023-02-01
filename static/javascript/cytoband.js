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

function highlight_genome_chr(rectangle, info) {

    let rectangles = document.getElementsByClassName("chromosome-selection-genome");
    for (let i = 0; i < rectangles.length; i++) {
        rectangles[i].classList.remove("chromosome-selection-highlight");
    }

    rectangle["target"].classList.add("chromosome-selection-highlight");

    let annotations = document.getElementsByClassName("annotation-genome-chr");
    annotations = annotations[0].firstElementChild.childNodes;

    for (let i = 0; i < annotations.length; i++) {
        let content = annotations[i].childNodes[2].childNodes[0];
        let bg = content.childNodes[0];
        let label = content.childNodes[1].childNodes[0];

        bg.classList.remove("annotation-highlight");
        label.classList.remove("annotation-highlight-label");

        if(label.textContent == info["chr"]){
            bg.classList.add("annotation-highlight");
            label.classList.add("annotation-highlight-label");
        }

    }
}


function draw_genome_(data) {

    let width = 1000;
    let height = 400;
    var shift = 8;

    let chr_width = 10;
    let gap = 20;
    let scale = 200;
    let chr_height = scale - 2*shift;

    var svg = d3.select("#genome")
	.append("svg")
	.attr("width", width)
	.attr("height", height);
    
    const annotations = []

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
            .attr("height", scale)
            .attr("class", "chromosome-selection-genome")
            .on('click', function(d,i) {
                highlight_genome_chr(d,i);
            });

        var rects = svg.selectAll("foo")
            .data(value)
            .enter()
            .append("rect")
            .attr("x", x_)
            .attr("y", d=> chr_height*(d.start/longest) + shift)
            .attr("width", chr_width)
            .attr("height", d=> ((d.end-d.start)/longest *chr_height) )
            .attr("fill", d=> d.color)
            .attr("class", "chromosome-band");
        
        var adjust = 0;
        if (i % 2 == 0){
            adjust = 20;
        }
        annotations.push(
            {note: {label: key, bgPadding: 3},
            x: x_ + chr_width/2,
            y: scale,
            dy: 10 + adjust,
            className: "annotation-genome-chr-bg",
            dx: 0,
            });

        i=i+1;
    }
    
    const makeAnnotations = d3.annotation()
        .type(d3.annotationLabel)
        .annotations(annotations);

    d3.select("#genome")
        .select("svg")
        .append("g")
        .attr("class", "annotation-group")
        .attr("class", "annotation-genome-chr")
        .call(makeAnnotations);

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
