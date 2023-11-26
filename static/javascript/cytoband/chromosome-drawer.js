const CHROMOSOME_CYTOBAND_ID="chromosome-cytoband"

function drawChromosome(chromosomeData) {
    resetChromosomeContainer();
    const dimensions = calculateChromosomeDimensions();
    const svg = createChromosomeSvg(dimensions);

    drawChromosomeBands(svg, chromosomeData, dimensions);
    const annotations = createChromosomeAnnotations(chromosomeData, dimensions);
    addChromosomeAnnotations(svg, annotations);
}
function calculateChromosomeDimensions() {
    return {
        height: 80,
        totalWidth: window.innerWidth * 0.6,
        padding: 20,
        annotationHeight: 10,
        annotationLayerHeight: 20,
        fontHeight: 20
    };
}

function resetChromosomeContainer() {
    document.getElementById(CHROMOSOME_CYTOBAND_ID).innerHTML = "";
}

function createChromosomeSvg(dimensions) {
    return d3.select("#" + CHROMOSOME_CYTOBAND_ID)
        .append("svg")
        .attr("width", dimensions.totalWidth)
        .attr("height", dimensions.height + dimensions.padding * 2 + dimensions.annotationHeight + dimensions.annotationLayerHeight + dimensions.fontHeight)
        .attr("padding-right", dimensions.padding);
}

function drawChromosomeBands(svg, data, dimensions) {
    const chrWidth = dimensions.totalWidth - dimensions.padding * 2;

    svg.selectAll("foo")
        .data(data)
        .enter()
        .append("rect")
        .attr("x", d => (dimensions.padding + d.x * chrWidth))
        .attr("y", dimensions.padding)
        .attr("width", d => (d.size * chrWidth))
        .attr("height", dimensions.height)
        .attr("fill", d => d.color);
}

function createChromosomeAnnotations(data, dimensions) {
    const chrWidth = dimensions.totalWidth - dimensions.padding * 2;
    return data.map((item, i) => ({
        note: { label: item.name },
        x: (dimensions.padding + item.x * chrWidth) + (item.size * chrWidth) / 2,
        y: dimensions.padding + dimensions.height,
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
}
