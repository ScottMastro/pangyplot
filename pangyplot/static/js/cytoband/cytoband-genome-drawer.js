function drawGenomeCytoband(data, chromOrder) {
    const dim = genomeCytobandDimensions();

    function createSvgCanvas() {
        const viewBoxValue = `0 0 ${dim.width} ${dim.height}`;
        return d3.select("#cytoband-genome-canvas-container")
            .append("svg")
            .attr("id", "cytoband-genome-canvas")
            .attr("width", "100%")
            .attr("height", dim.chrFullHeight)
            .attr("viewBox", viewBoxValue);
    }

    function getLongestChromosomeSize() {
        let longest = -1;
        for (const [key, chr] of Object.entries(data)) {
            for (let j = 0; j < chr.length; j++) {
                if (chr[j]["end"] > longest){
                    longest = chr[j]["end"];
                }
            }
        }
        return longest;
    }

    function calculateBorderX(index) {
        return dim.widthPad + (dim.chrFullWidth + dim.widthPad) * index;
    }
    function drawGenomeChromosomeBorder(svg, index, chromName) {
        const borderX = calculateBorderX(index);

        svg.append("rect")
            .attr("x", borderX)
            .attr("y", dim.topPad)
            .attr("rx", dim.radius)
            .attr("ry", dim.radius)
            .attr("width", dim.chrFullWidth)
            .attr("height", dim.chrFullHeight)
            .attr("class", "cytoband-genome-chromosome")
            .on('click', function() {

                highlightGenomeCytoband(chromName);
                const data = {chrom: chromName, start: null, end: null, source: "cytoband-genome"};
                document.dispatchEvent( new CustomEvent('selectedCoordinatesChanged', { detail: data }));    
            });
    }
    
    function drawGenomeChromosomeBands(svg, index, chromData) {
        const borderX = calculateBorderX(index);
        const longestChromSize = getLongestChromosomeSize();
        
        function bandClasses(d){
            if (d.type){
                return "cytoband-band cytoband-" + d.type;
            } return "cytoband-band";
        }

        svg.selectAll("x")
            .data(chromData)
            .enter()
            .append("rect")
            .attr("x", borderX + dim.borderPad)
            .attr("y", d => dim.topPad + dim.borderPad + dim.chrHeight * (d.start / longestChromSize))
            .attr("width", dim.chrWidth)
            .attr("height", d => dim.chrHeight * (d.end - d.start) / longestChromSize)
            .attr("fill", d => d.color)
            .attr("class", d => bandClasses(d))
    }
    
    function createAnnotation(chromName, index ) {
        const borderX = calculateBorderX(index);

        return {
            note: { label: chromName, bgPadding: 0 },
            x: borderX + dim.chrFullWidth / 2,
            y: dim.topPad + dim.chrFullHeight,
            dy: dim.annotationHeight * ((index % 2) + 1),
            dx: 0
        };
    }

    function addAnnotations(svg, annotations) {
        const annotationsGroup = svg.selectAll(".annotation-group")
            .data([annotations])
            .join("g")
            .attr("class", "cytoband-genome-annotation");
    
        const makeAnnotations = d3.annotation()
            .type(d3.annotationLabel)
            .annotations(annotations);
    
        annotationsGroup.call(makeAnnotations);
    
        svg.selectAll('.annotation text')
        .attr('class', 'cytoband-genome-text')
    }

    const svg = createSvgCanvas();
    let annotations = [];

    chromOrder.forEach((chromName, index) => {
        drawGenomeChromosomeBorder(svg, index, chromName);
        drawGenomeChromosomeBands(svg, index, data[chromName]);
        annotations.push(createAnnotation(chromName, index));
    });

    addAnnotations(svg, annotations);

    return svg;
}