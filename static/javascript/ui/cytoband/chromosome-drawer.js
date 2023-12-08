const CHR_CANVAS_CONTAINER_ID="chromosome-cytoband-container"
const CHR_CANVAS_ID="chromosome-cytoband-canvas"
var CURRENT_CHROMOSOME_SIZE=0
var IS_DRAGGING = false;
var DRAG_STARTX = null;
var DRAG_ENDX = null;
var CHROM_DRAG_RECT;
var CHROM_DRAG_RECTX;


function drawChromosome(chromosomeData) {
    resetChromosomeContainer(CHR_CANVAS_CONTAINER_ID);
    CURRENT_CHROMOSOME_SIZE = getChromosomeSize(chromosomeData);
    const dimensions = calculateChromosomeDimensions();
    const svg = createChromosomeSvg(CHR_CANVAS_CONTAINER_ID, dimensions, CHR_CANVAS_ID);
    addDragSelect(svg);
    drawChromosomeBorder(svg, dimensions);
    drawChromosomeBands(svg, chromosomeData, dimensions);
    const annotations = createChromosomeAnnotations(chromosomeData, dimensions);
    addChromosomeAnnotations(svg, annotations);
}


function resetChromosomeContainer(containerId) {
    document.getElementById(containerId).innerHTML = "";
}

function calculateChromosomeDimensions() {

    let dimensions =  {
        widthPad: 15,
        chrWidth: 800,
        chrHeight: 40,
        annotationHeight: 30,
        heightBuffer: 30
    };
    dimensions.width = dimensions.chrWidth + dimensions.widthPad*2;
    dimensions.height = dimensions.chrHeight + dimensions.annotationHeight*2 + dimensions.heightBuffer*2;
    return dimensions;
}

function getChromosomeSize(chromosomeData) {
    let longest = -1;
    for (let j = 0; j < chromosomeData.length; j++) {
        if (chromosomeData[j]["end"] > longest){
            longest = chromosomeData[j]["end"];
        }
    }

    return longest;
}

function createChromosomeSvg(containerId, dimensions, svgId) {
    const viewBoxValue = `0 0 ${dimensions.width} ${dimensions.height}`;
    
    let svg = d3.select("#" + containerId)
                .append("svg")
                .attr("id", svgId)
                .attr("width", "100%")
                .attr("height", "auto")
                .attr("viewBox", viewBoxValue);

    return svg;
}

function drawChromosomeBorder(svg, dimensions) {
    svg.append("rect")
        .attr("x", 0)
        .attr("y", dimensions.heightBuffer+dimensions.annotationHeight*3/4)
        .attr("rx", 4)
        .attr("ry", 4)
        .attr("width", dimensions.width)
        .attr("height", dimensions.chrHeight + dimensions.annotationHeight/2)
        .attr("class", "chromosome-background");
}

function drawChromosomeBands(svg, data, dimensions) {
    svg.selectAll("x")
        .data(data)
        .enter()
        .append("rect")
        .attr("x", d => (dimensions.widthPad + d.x * dimensions.chrWidth))
        .attr("y", dimensions.heightBuffer+dimensions.annotationHeight)
        .attr("width", d => (d.size * dimensions.chrWidth))
        .attr("height", dimensions.chrHeight)
        .attr("fill", d => d.color);
}

function createChromosomeAnnotations(data, dimensions) {
    function direction(i){
        if (i % 2 === 0) return(1);
        return(-1);
    }
     function y_start(i){
        if (i % 2 === 0) {
            return(dimensions.heightBuffer + 
                    dimensions.annotationHeight +
                    dimensions.chrHeight);
        }
        return(dimensions.heightBuffer+dimensions.annotationHeight);
    } 
    function dy(i) {
        let remainder = i % 6
        if (remainder <= 1) { return dimensions.annotationHeight/3 }
        if (remainder <= 3) { return dimensions.annotationHeight*2/3 }
        if (remainder <= 5) { return dimensions.annotationHeight }
        return dimensions.annotationHeight/3;
    }
    
    return data.map((item, i) => ({
        note: { label: `${item.name}` },
        x: dimensions.widthPad + (item.x * dimensions.chrWidth) + (item.size * dimensions.chrWidth) / 2,
        y: y_start(i),
        dy: direction(i)*(dy(i)),
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
        .attr('class', 'chromosome-label-text')
}

function addDragSelect(svg){
    const svgElement = svg.node();
    const svgRect = svgElement.getBoundingClientRect();
    svg.on('mousedown', function(event) {
        DRAG_STARTX = null;
        DRAG_ENDX = null;
        
        // Starting x-coordinate (normalized)
        const [x, y] = d3.pointer(event, svgElement);
        const dimensions = calculateChromosomeDimensions();
        let w = dimensions.widthPad
        const scaleX = svgRect.width / dimensions.width;
        
        DRAG_STARTX = (x-w)*scaleX / (svgElement.clientWidth-w*2*scaleX);
        DRAG_STARTX = Math.max(DRAG_STARTX, 0);
        DRAG_STARTX = Math.min(DRAG_STARTX, 1);
        IS_DRAGGING = true;

        CHROM_DRAG_RECTX = x;
        if (CHROM_DRAG_RECT != null){
            CHROM_DRAG_RECT.remove();
        }
        CHROM_DRAG_RECT = svg.append('rect')
                    .attr('x', CHROM_DRAG_RECTX)
                    .attr('y', dimensions.heightBuffer+dimensions.annotationHeight*3/4)
                    .attr('width', 0)
                    .attr('height', dimensions.chrHeight+dimensions.annotationHeight*1/2)
                    .attr('fill', 'none')
                    .attr("class", "chromosome-selection-box");       
    });

    svg.on('mousemove', function(event) {
        if (IS_DRAGGING) {
            // Update end x-coordinate (normalized) while dragging
            const [x, y] = d3.pointer(event, svgElement);
            const dimensions = calculateChromosomeDimensions();
            let w = dimensions.widthPad
            const scaleX = svgRect.width / dimensions.width;
            
            DRAG_ENDX = (x - w)*scaleX / (svgElement.clientWidth-w*2*scaleX);
            DRAG_ENDX = Math.max(DRAG_ENDX, 0);
            DRAG_ENDX = Math.min(DRAG_ENDX, 1);

            let rectX = (x < CHROM_DRAG_RECTX) ? x : CHROM_DRAG_RECTX;            
            let width = Math.abs(x - CHROM_DRAG_RECTX);

            if (rectX < dimensions.widthPad){
                let diff = dimensions.widthPad - rectX;
                rectX = dimensions.widthPad;
                width = width - diff;
            }

            if (rectX + width > dimensions.chrWidth + dimensions.widthPad){
                let diff = rectX + width - dimensions.chrWidth - dimensions.widthPad;
                width = width - diff;
            }

            CHROM_DRAG_RECT.attr('x', rectX)
                    .attr('y', dimensions.heightBuffer+dimensions.annotationHeight*3/4)
                    .attr('width', width)
                    .attr('height', dimensions.chrHeight+dimensions.annotationHeight*1/2);
     
        }
    });

    svg.on('mouseup', function() {
        if (IS_DRAGGING) {
            IS_DRAGGING = false;

            if (DRAG_STARTX == DRAG_ENDX){
                if (CHROM_DRAG_RECT != null){
                    CHROM_DRAG_RECT.remove();
                }
                return;
            }
            updateStartEndCoordinates(DRAG_STARTX, DRAG_ENDX);
        }
    });

    svg.on('mouseleave', function() {
        if (IS_DRAGGING) {
            IS_DRAGGING = false;
            updateStartEndCoordinates(DRAG_STARTX, DRAG_ENDX);
        }
    });
}

function updateStartEndCoordinates(start, end){
    if (start != null && end != null && start != end){

        if (end < start){
            let x = end; end = start; start = x;
        }

        //console.log(`Dragged from x=${start} to x=${end}`);

        let startPos = Math.round(start*CURRENT_CHROMOSOME_SIZE);
        startPos = Math.max(1, startPos);
        let endPos = Math.round(end*CURRENT_CHROMOSOME_SIZE);

        updateGoValues(null, startPos, endPos);
    }
}