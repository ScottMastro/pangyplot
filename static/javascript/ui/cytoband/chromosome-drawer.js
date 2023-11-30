const CHR_CANVAS_CONTAINER_ID="chromosome-cytoband-container"
const CHR_CANVAS_ID="chromosome-cytoband-canvas"

function drawChromosome(chromosomeData) {
    resetChromosomeContainer(CHR_CANVAS_CONTAINER_ID);
    const dimensions = calculateChromosomeDimensions();
    const svg = createChromosomeSvg(CHR_CANVAS_CONTAINER_ID, dimensions, CHR_CANVAS_ID);

    drawChromosomeBands(svg, chromosomeData, dimensions);
    const annotations = createChromosomeAnnotations(chromosomeData, dimensions);
    addChromosomeAnnotations(svg, annotations);
}
function calculateChromosomeDimensions() {

    let dimensions =  {
        widthPad: 15,
        chrWidth: 800,
        chrHeight: 40,
        annotationHeight: 10,
        annotationLayerHeight: 20,
        fontHeight: 20
    };
    dimensions.width = dimensions.chrWidth + dimensions.widthPad*2;
    dimensions.height = dimensions.chrHeight + dimensions.annotationHeight + dimensions.annotationLayerHeight + dimensions.fontHeight;
    return dimensions;
}

function resetChromosomeContainer(containerId) {
    document.getElementById(containerId).innerHTML = "";
}

function createChromosomeSvg(containerId, dimensions, svgId) {
    const viewBoxValue = `0 0 ${dimensions.width} ${dimensions.height}`;
    
    return d3.select("#" + containerId)
        .append("svg")
        .attr("id", svgId)
        .attr("width", "100%")
        .attr("height", "auto")
        .attr("viewBox", viewBoxValue);
}

function drawChromosomeBands(svg, data, dimensions) {
    svg.selectAll("x")
        .data(data)
        .enter()
        .append("rect")
        .attr("x", d => (dimensions.widthPad + d.x * dimensions.chrWidth))
        .attr("y", 0)
        .attr("width", d => (d.size * dimensions.chrWidth))
        .attr("height", dimensions.chrHeight)
        .attr("fill", d => d.color);
}

function createChromosomeAnnotations(data, dimensions) {
    return data.map((item, i) => ({
        note: { label: item.name },
        x: dimensions.widthPad + (item.x * dimensions.chrWidth) + (item.size * dimensions.chrWidth) / 2,
        y: dimensions.chrHeight,
        dy: dimensions.annotationHeight + (i % 2 === 0 ? dimensions.annotationLayerHeight : 0),
        dx: 0
    }));
}

function addChromosomeAnnotations(svg, annotations) {
    const makeAnnotations = d3.annotation()
        .type(d3.annotationLabel)
        .annotations(annotations);

    svg.append("g")
        .attr("class", "chromosome-annotation-band")
        .call(makeAnnotations);

        svg.selectAll('.annotation text')
        .attr('class', 'annotation-text')
}
