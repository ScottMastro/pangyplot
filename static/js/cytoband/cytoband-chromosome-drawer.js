function drawChromosomeCytoband(data) {
    const dim = chromosomeCytobandDimensions();

    function createSvgCanvas() {
        const viewBoxValue = `0 0 ${dim.width} ${dim.height}`;
        
        let svg = d3.select("#cytoband-chromosome-canvas-container")
                    .append("svg")
                    .attr("id", "cytoband-chromosome-canvas")
                    .attr("width", "100%")
                    .attr("height", "auto")
                    .attr("viewBox", viewBoxValue);

        return svg;
    }

    function drawChromosomeBackground(svg) {
        svg.append("rect")
            .attr("x", 0)
            .attr("y", dim.heightBuffer + dim.annotationHeight*3/4)
            .attr("rx", dim.radius)
            .attr("ry", dim.radius)
            .attr("width", dim.width)
            .attr("height", dim.chrHeight + dim.annotationHeight/2)
            .attr("class", "cytoband-chromosome-background");
    }

    function drawChromosomeBands(svg) {
        for (let i = 0; i < data.length; i++) {
            const d = data[i];
            const x = dim.widthPad + d.x * dim.chrWidth;
            const y = dim.heightBuffer + dim.annotationHeight;
            const width = d.size * dim.chrWidth;
            const height = dim.chrHeight;
            let radius = dim.radius;

            const centromereL = d.name.startsWith("p") && data[i + 1] && data[i + 1].name.startsWith("q")
            const centromereR = d.name.startsWith("q") && i > 0 && data[i - 1].name.startsWith("p")

            let pathD = "";
            if (i === 0 || centromereR) { // round left side
                pathD = `M ${x + radius} ${y} 
                        L ${x + width} ${y} 
                        L ${x + width} ${y + height} 
                        L ${x + radius} ${y + height} 
                        Q ${x} ${y + height} ${x} ${y + height - radius} 
                        L ${x} ${y + radius} 
                        Q ${x} ${y} ${x + radius} ${y}`;
            } else if (i === data.length - 1 || centromereL) { // round right side
                pathD = `M ${x} ${y} 
                        L ${x + width - radius} ${y} 
                        Q ${x + width} ${y} ${x + width} ${y + radius} 
                        L ${x + width} ${y + height - radius} 
                        Q ${x + width} ${y + height} ${x + width - radius} ${y + height} 
                        L ${x} ${y + height} 
                        Z`;
            } else { // no rounding
                pathD = `M ${x} ${y} 
                        L ${x + width} ${y} 
                        L ${x + width} ${y + height} 
                        L ${x} ${y + height} 
                        Z`;
            }

            function bandClass(d){
                if (d.type){
                    return "cytoband-" + d.type;
                } return "cytoband-band";
            }

            svg.append("path")
                .attr("d", pathD)
                .attr("fill", d.color)
                .attr("class", bandClass(d));
        }
    }

    function addChromosomeAnnotations(svg) {
        function direction(i){
            if (i % 2 === 0) return(1);
            return(-1);
        }
        function y_start(i){
            let h = dim.heightBuffer + dim.annotationHeight;
            if (i % 2 === 0) {
                return(h + dim.chrHeight);
            }
            return(h);
        } 
        function dy(i) {
            let remainder = i % 6
            if (remainder <= 1) { return dim.annotationHeight/3 }
            if (remainder <= 3) { return dim.annotationHeight*2/3 }
            if (remainder <= 5) { return dim.annotationHeight }
            return dim.annotationHeight/3;
        }
        
        const annotations =  data.map((item, i) => ({
                note: { label: `${item.name}` },
                x: dim.widthPad + (item.x * dim.chrWidth) + (item.size * dim.chrWidth) / 2,
                y: y_start(i),
                dy: direction(i)*(dy(i)),
                dx: 0
        }));

        const makeAnnotations = d3.annotation()
            .type(d3.annotationLabel)
            .annotations(annotations);

        svg.append("g")
            .attr("class", "cytoband-chromosome-annotation")
            .call(makeAnnotations);

        svg.selectAll('.annotation text')
            .attr('class', 'cytoband-chromosome-text');
    }

    const svg = createSvgCanvas();
    drawChromosomeBackground(svg);
    drawChromosomeBands(svg);
    addChromosomeAnnotations(svg);

    return svg;
};