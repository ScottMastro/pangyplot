const DEFAULT_CHR="chr18"

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

function highlight_genome_chr(chr_name) {

    let rectangles = document.getElementsByClassName("chromosome-selection-genome");
    for (let i = 0; i < rectangles.length; i++) {
        rectangles[i].classList.remove("chromosome-selection-highlight");
    }

    let annotations = document.getElementsByClassName("genome-annotation-chr");
    annotations = annotations[0].firstElementChild.childNodes;

    for (let i = 0; i < annotations.length; i++) {
        let content = annotations[i].childNodes[2].childNodes[0];
        let bg = content.childNodes[0];
        let label = content.childNodes[1].childNodes[0];

        bg.classList.remove("annotation-highlight");
        label.classList.remove("annotation-highlight-label");

        if(label.textContent == chr_name){
            bg.classList.add("annotation-highlight");
            label.classList.add("annotation-highlight-label");
            document.getElementsByClassName("chromosome-selection-genome")[i].classList.add("chromosome-selection-highlight");
        }
    }

}

function draw_genome_(data, chr_order) {

    //---- Adjustable params ----

    let chr_height = 200;
    let chr_width = 10;

    let border_padding = 8;
    let hspacing = 4;

    let annotation_height = 10;
    let annotation_layer_height = 20;

    //---------------------------

    let nchrs = Object.keys(data).length;
    let border_height = chr_height + 2*border_padding;
    let border_width = chr_width + 2*border_padding;    
    let total_width = (chr_width+border_padding*2 + hspacing)*nchrs + hspacing
    //20 is for font height
    let total_height = border_height+hspacing*2 + annotation_height + annotation_layer_height + 20; 
    var svg = d3.select("#genome")
	.append("svg")
	.attr("width", total_width)
	.attr("height", total_height);
    
    const annotations = []

    let longest = get_longest_size(data);
    let i = 0;
    
    for (var ci = 0; ci < chr_order.length; ci++) {
        let chr_name =  chr_order[ci]

        let x_border = (hspacing+border_width)*i + hspacing

        var rects = svg.append("rect")
            .attr("x", x_border)
            .attr("y", 0)
            .attr("rx", 4)
            .attr("ry", 4)
            .attr("width", border_width)
            .attr("height", border_height)
            .attr("class", "chromosome-selection-genome")
            .on('click', function() {
                highlight_genome_chr(chr_name);
                draw_chromosome(chr_name);
            });

        var rects = svg.selectAll("foo")
            .data(data[chr_name])
            .enter()
            .append("rect")
            .attr("x", x_border + border_padding)
            .attr("y", d=> chr_height*(d.start/longest) + border_padding)
            .attr("width", chr_width)
            .attr("height", d=> ((d.end-d.start)/longest *border_height) )
            .attr("fill", d=> d.color)
            .attr("class", "chromosome-band");
        
        var adjust = 0;
        if (i % 2 == 0){
            adjust = annotation_layer_height;
        }
        annotations.push(
            {note: {label: chr_name, bgPadding: 3},
            x: x_border + border_padding + chr_width/2,
            y: border_height,
            dy: annotation_height + adjust,
            className: "genome-annotation-chr-bg",
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
        .attr("class", "genome-annotation-chr")
        .call(makeAnnotations);
    
    highlight_genome_chr(DEFAULT_CHR)
}


function draw_chromosome_(data) {
    document.getElementById("chromosome").innerHTML = "";

    //---- Adjustable params ----

    let chr_height = 80;
    let total_width = 1600;
    let padding = 20;

    let annotation_height = 10;
    let annotation_layer_height = 20;

    //---------------------------
    
    let chr_width = total_width - padding*2;
    //20 is for font height
    let total_height = chr_height+padding*2 + annotation_height + annotation_layer_height + 20; 

    var svg = d3.select("#chromosome")
	.append("svg")
	.attr("width", total_width)
	.attr("height", total_height)
    .attr("padding-right", padding);

    var rects = svg.selectAll("foo")
        .data(data)
        .enter()
        .append("rect")
        .attr("x", d=> (padding + d.x*chr_width))
        .attr("y", padding)
        .attr("width", d=> (d.size*chr_width))
        .attr("height", chr_height)
        .attr("fill", d=> d.color);

    const annotations = []
    for (var i = 0; i < data.length; i++) {
        var adjust = 0;
        if (i % 2 == 0){
            adjust = annotation_layer_height;
        }
        annotations.push(
            {note: {label: data[i]["name"]},
            x: (padding + data[i]["x"]*chr_width) + (data[i]["size"]*chr_width)/2,
            y: padding + chr_height,
            dy: annotation_height + adjust,
            dx: 0,
            });
    }

    const makeAnnotations = d3.annotation()
        .type(d3.annotationLabel)
        .annotations(annotations);

    d3.select("#chromosome")
        .select("svg")
        .append("g")
        .attr("class", "chromosome-annotation-band")
        .call(makeAnnotations);
}

function draw_genome() {
    let url = "/cytoband?include_order=true"
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var data = JSON.parse(xmlHttp.response)

            let order = data.order;
            delete data.order;

            draw_genome_(data, order);
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
draw_chromosome(DEFAULT_CHR);
