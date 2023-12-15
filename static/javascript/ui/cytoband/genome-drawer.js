const GENOME_CANVAS_CONTAINER_ID="genome-container-content"
const GENOME_CANVAS_ID="genome-cytoband-canvas"

function drawGenome(data, chrOrder, initialChr) {
    const chrDimensions = { height: 200, width: 10 };
    const border = { padding: 8, height: chrDimensions.height + 16, width: chrDimensions.width + 16 };
    const spacing = { horizontal: 4, vertical: 10, fontHeight: 20 };
    const annotation = { height: 10, layerHeight: 20 };
    
    const totalDimensions = calculateTotalDimensions(data, chrDimensions, border, spacing, annotation);

    const svg = createSvgCanvas(GENOME_CANVAS_CONTAINER_ID, totalDimensions, GENOME_CANVAS_ID);
    const longestChrSize = getLongestChromosomeSize(data);

    let annotations = [];

    chrOrder.forEach((chrName, index) => {
        const xBorder = calculateXBorder(index, border, spacing);
        drawGenomeChromosomeBorder(svg, xBorder, border, chrName);
        drawGenomeChromosomeBands(svg, data[chrName], xBorder, chrDimensions, border, longestChrSize);
        annotations.push(createAnnotation(chrName, xBorder, border, chrDimensions, annotation, index));
    });

    addAnnotations(svg, annotations);

    if (initialChr != null){
        highlightGenomeChr(initialChr);
    }
}

function calculateTotalDimensions(data, chrDimensions, border, spacing, annotation) {
    const numChromosomes = Object.keys(data).length;
    const width = (chrDimensions.width + border.padding * 2 + spacing.horizontal) * numChromosomes + spacing.horizontal;
    const height = border.height + spacing.vertical + annotation.height + annotation.layerHeight + spacing.fontHeight;
    return { width, height };
}

function createSvgCanvas(containerId, dimensions, svgId) {
    const viewBoxValue = `0 0 ${dimensions.width} ${dimensions.height}`;
    return d3.select("#" + containerId)
        .append("svg")
        .attr("id", svgId)
        .attr("width", "100%")
        .attr("height", "auto")
        .attr("viewBox", viewBoxValue);
}

function getLongestChromosomeSize(data) {
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
function calculateXBorder(index, border, spacing) {
    return (spacing.horizontal + border.width) * index + spacing.horizontal;
}

function drawGenomeChromosomeBorder(svg, x, border, chrName) {

    const data = {
        chr: chrName,
        start: null,
        end: null
    };
    
    svg.append("rect")
        .attr("x", x)
        .attr("y", 0)
        .attr("rx", 4)
        .attr("ry", 4)
        .attr("width", border.width)
        .attr("height", border.height)
        .attr("class", "chromosome-selection-genome")
        .on('click', function() {
            const selectedEvent = new CustomEvent('selectedCoordinatesChanged', { detail: data });
            document.dispatchEvent(selectedEvent);
        });
}

function drawGenomeChromosomeBands(svg, chrData, xBorder, chrDimensions, border, longestChrSize) {
    svg.selectAll("x")
        .data(chrData)
        .enter()
        .append("rect")
        .attr("x", xBorder + border.padding)
        .attr("y", d => chrDimensions.height * (d.start / longestChrSize) + border.padding)
        .attr("width", chrDimensions.width)
        .attr("height", d => (d.end - d.start) / longestChrSize * border.height)
        .attr("fill", d => d.color)
        .attr("class", "chromosome-band");
}

function createAnnotation(chrName, xBorder, border, chrDimensions, annotation, index) {
    let adjust = index % 2 === 0 ? annotation.layerHeight : 0;
    return {
        note: { label: chrName, bgPadding: 3 },
        x: xBorder + border.padding + chrDimensions.width / 2,
        y: border.height,
        dy: annotation.height + adjust,
        className: "genome-annotation-chr-bg",
        dx: 0
    };
}

function addAnnotations(svg, annotations) {
    const annotationsGroup = svg.selectAll(".annotation-group")
        .data([annotations])
        .join("g")
        .attr("class", "annotation-group genome-annotation-chr");

    const makeAnnotations = d3.annotation()
        .type(d3.annotationLabel)
        .annotations(annotations);

    annotationsGroup.call(makeAnnotations);

    svg.selectAll('.annotation text')
    .attr('class', 'chromosome-label-text')

}
function clearAllChrHighlightsMain(){
    let rectangles = document.getElementsByClassName("chromosome-selection-genome");
    for (let i = 0; i < rectangles.length; i++) {
        rectangles[i].classList.remove("chromosome-selection-highlight");
    }

    let annotations = document.getElementsByClassName("genome-annotation-chr")[0].firstElementChild.childNodes;
    for (let i = 0; i < annotations.length; i++) {
        let content = annotations[i].childNodes[2].childNodes[0];
        let bg = content.childNodes[0];

        bg.classList.remove("chromosome-label-highlight");
    }
}

function highlightGenomeChr(chrName) {
    clearAllChrHighlightsMain();

    let rectangles = document.getElementsByClassName("chromosome-selection-genome");
    let annotations = document.getElementsByClassName("genome-annotation-chr")[0].firstElementChild.childNodes;
    for (let i = 0; i < annotations.length; i++) {
        let content = annotations[i].childNodes[2].childNodes[0];
        let bg = content.childNodes[0];
        let label = content.childNodes[1].childNodes[0];

        if (label.textContent === chrName) {
            bg.classList.add("chromosome-label-highlight");
            rectangles[i].classList.add("chromosome-selection-highlight");
        }
    }
}

document.addEventListener('selectedCoordinatesChanged', function(event) {
    
    highlightGenomeChr(event.detail.chr);

});