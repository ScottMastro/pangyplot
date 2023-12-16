let SELECTED_CHR = null;

function chromosomeCytobandDimensions() {
    const chrWidth = 800;
    const widthPad = 15;
    const chrHeight = 40;
    const radius = 5;
    const annotationHeight = 30;
    const heightBuffer = 30;

    return {
        widthPad: widthPad,
        chrWidth: chrWidth,
        chrHeight: chrHeight,
        radius: radius,
        annotationHeight: annotationHeight,
        heightBuffer: heightBuffer,
        width: chrWidth + widthPad*2,
        height: chrHeight + annotationHeight*2 + heightBuffer*2
    };
}

function updateChromosomeCytoband(chromosomeData, chromName, chromStart, chromEnd) {

    function getChromosomeSize() {
        let longest = -1;
        for (let j = 0; j < chromosomeData.length; j++) {
            if (chromosomeData[j]["end"] > longest){
                longest = chromosomeData[j]["end"];
            }
        }
        return longest;
    }    

    const canvasContainer = document.getElementById("cytoband-chromosome-canvas-container");
    const missingInfo = document.getElementById("cytoband-chromosome-no-info");

    canvasContainer.innerHTML = "";

    if (chromosomeData == null){
        SELECTED_CHR = null;
        missingInfo.style.display = "block";
    } else{        
        SELECTED_CHR = chromName;
        missingInfo.style.display = "none";

        const chromSize = getChromosomeSize(chromosomeData);
        const svg = drawChromosomeCytoband(chromosomeData);

        addDragSelect(svg, chromSize, chromStart, chromEnd);
    }
}


function addDragSelect(svg, chromSize, chromStart, chromEnd){
    
    let IS_DRAGGING = false;
    let DRAG_STARTX;
    let DRAG_ENDX;
    let CHROM_DRAG_RECT;
    let CHROM_DRAG_RECTX;

    const dim = chromosomeCytobandDimensions();
    const w = dim.widthPad

    const svgElement = svg.node();
    const svgRect = svgElement.getBoundingClientRect();
    const scaleX = svgRect.width / dim.width;

    svg.on('mousedown', function(event) {
        DRAG_STARTX = null;
        DRAG_ENDX = null;
        
        // Starting x-coordinate (normalized)
        const [x, y] = d3.pointer(event, svgElement);
        
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
                    .attr('y', dim.heightBuffer + dim.annotationHeight*3/4)
                    .attr('width', 0)
                    .attr('height', dim.chrHeight + dim.annotationHeight*1/2)
                    .attr('fill', 'none')
                    .attr("class", "cytoband-chromosome-selection-box");       
    });

    svg.on('mousemove', function(event) {
        if (IS_DRAGGING) {

            // Update end x-coordinate (normalized) while dragging
            const [x, y] = d3.pointer(event, svgElement);
            
            DRAG_ENDX = (x - w)*scaleX / (svgElement.clientWidth-w*2*scaleX);
            DRAG_ENDX = Math.max(DRAG_ENDX, 0);
            DRAG_ENDX = Math.min(DRAG_ENDX, 1);

            let rectX = (x < CHROM_DRAG_RECTX) ? x : CHROM_DRAG_RECTX;            
            let width = Math.abs(x - CHROM_DRAG_RECTX);

            if (rectX < w){
                let diff = w - rectX;
                rectX = w;
                width = width - diff;
            }

            if (rectX + width > dim.chrWidth + w){
                let diff = rectX + width - dim.chrWidth - w;
                width = width - diff;
            }

            CHROM_DRAG_RECT.attr('x', rectX)
                    .attr('y', dim.heightBuffer + dim.annotationHeight*3/4)
                    .attr('width', width)
                    .attr('height', dim.chrHeight + dim.annotationHeight*1/2);
     
        }
    });

    function updateStartEndCoordinates(start, end){
        if (start != null && end != null && start != end){
    
            if (end < start){
                let x = end; end = start; start = x;
            }
    
            //console.log(`Dragged from x=${start} to x=${end}`);
    
            let startPos = Math.round(start*chromSize);
            startPos = Math.max(1, startPos);
            let endPos = Math.round(end*chromSize);
    
            const data = {chrom: SELECTED_CHR, start: startPos, end: endPos, source: "cytoband-chromosome"};
            document.dispatchEvent( new CustomEvent('selectedCoordinatesChanged', { detail: data }));    
        }
    }

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

    function drawChromosomeSelectionBox(start, end){
        if (start != null && end != null && start != end){

            const startPos = start/chromSize;
            const endPos = end/chromSize;
            const x1 = startPos*(svgElement.clientWidth-w*2*scaleX)/scaleX + w;
            const x2 = endPos*(svgElement.clientWidth-w*2*scaleX)/scaleX + w;
    
            if (CHROM_DRAG_RECT != null){
                CHROM_DRAG_RECT.remove();
            }

            CHROM_DRAG_RECT = svg.append('rect')
                        .attr('x', x1)
                        .attr('y', dim.heightBuffer + dim.annotationHeight*3/4)
                        .attr('width', x2-x1)
                        .attr('height', dim.chrHeight + dim.annotationHeight*1/2)
                        .attr('fill', 'none')
                        .attr("class", "cytoband-chromosome-selection-box");       
    
        }
    }

    if (chromStart != null & chromEnd != null){
        drawChromosomeSelectionBox(chromStart, chromEnd);
    }
}

document.addEventListener('selectedCoordinatesChanged', function(event) {
    if (event.detail.source === "cytoband-chromosome"){
        return;
    }
    fetchAndDrawChromosomeData(event.detail.chrom, event.detail.start, event.detail.end);    
});
