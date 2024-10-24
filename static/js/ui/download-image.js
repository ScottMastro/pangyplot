function getFormattedDateTime() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day}_${hours}-${minutes}-${seconds}`;
}

function setUpImageDownloadButtons(forceGraph){
    document.getElementById('download-image-png-button').addEventListener('click', function() {
        downloadGraphImage();
    });
    document.getElementById('download-image-svg-button').addEventListener('click', function() {
        exportForceGraphToSVG(forceGraph);
    });
}

function downloadGraphImage(){
    const canvas = document.querySelector('.force-graph-container canvas');
    if (!canvas) {
        console.error('Canvas element not found');
        return;
    }

    const dateTimeStr = getFormattedDateTime();
    const dataUrl = canvas.toDataURL('image/png');
    const link = document.createElement('a');
    link.download = `pangyplot_${dateTimeStr}.png`;
    link.href = dataUrl;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}


function exportForceGraphToSVG(forceGraph) {
    const canvasElement = document.querySelector('#graph-container canvas');
    const ctx = canvasElement.getContext('2d');
    const viewport = getViewport(forceGraph, getCanvasWidth(), getCanvasHeight(), buffer=1.01);
    const graphData = forceGraph.graphData();
    const { nodes, links } = graphData;

    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    function updateBoundingBox(x, y) {
        minX = Math.min(minX, x);
        minY = Math.min(minY, y);
        maxX = Math.max(maxX, x);
        maxY = Math.max(maxY, y);
    }
    
    const geneGroup = document.createElementNS(svgNS, "g");

    genes = geneRenderEngineDraw(ctx, graphData, true)
    genes.forEach(item => {
        if (item.type === 'node') {
            const circle = document.createElementNS(svgNS, "circle");
            circle.setAttribute("cx", item.element.x);
            circle.setAttribute("cy", item.element.y);
            circle.setAttribute("r", item.size/2);
            circle.setAttribute("fill", item.color);
            geneGroup.appendChild(circle);
        } else if (item.type === 'link') {
            const line = document.createElementNS(svgNS, "line");
            line.setAttribute("x1", item.element.source.x);
            line.setAttribute("y1", item.element.source.y);
            line.setAttribute("x2", item.element.target.x);
            line.setAttribute("y2", item.element.target.y);
            line.setAttribute("stroke", item.color);
            line.setAttribute("stroke-width", item.size); 
            geneGroup.appendChild(line);
        }
    });
    
    const linkGroup = document.createElementNS(svgNS, "g");
    const nodeGroup = document.createElementNS(svgNS, "g");
    
    // Add links to the SVG
    links.forEach(link => {
        if (!link.isVisible || !link.isDrawn) return;
        const l = basicRenderPaintLink(ctx, link, true)
        const line = document.createElementNS(svgNS, "line");
        line.setAttribute("x1", l.x1);
        line.setAttribute("y1", l.y1);
        line.setAttribute("x2", l.x2);
        line.setAttribute("y2", l.y2);
        line.setAttribute("stroke", l.color);
        line.setAttribute("stroke-width", l.width); 
        linkGroup.appendChild(line);
        updateBoundingBox(l.x1, l.y1);
        updateBoundingBox(l.x2, l.y2);
    });

    // Add nodes to the SVG
    nodes.forEach(node => {
        if (!node.isVisible || !node.isDrawn) return;

        const n = basicRenderPaintNode(ctx, node, true);
        const circle = document.createElementNS(svgNS, "circle");
        circle.setAttribute("cx", n.cx);
        circle.setAttribute("cy", n.cy);
        circle.setAttribute("r", n.size/2);
        circle.setAttribute("fill", n.fill);

        if (n.stroke) {
            circle.setAttribute("stroke", n.stroke); // Outline color
            circle.setAttribute("stroke-width", n.strokeWidth);
        }

        nodeGroup.appendChild(circle);
        updateBoundingBox(n.cx, n.cy);
    });

    const geneLabelGroup = document.createElementNS(svgNS, "g");
    geneLabels = drawGeneName(ctx, graphData, viewport, true);
    geneLabels.forEach(label => {
        const textElement = document.createElementNS(svgNS, "text");
        textElement.setAttribute("x", label.x);
        textElement.setAttribute("y", label.y);
        textElement.setAttribute("font-size", label.fontSize);
        textElement.setAttribute("fill", label.color);
        textElement.setAttribute("stroke", label.stroke);
        textElement.setAttribute("stroke-width", label.strokeWidth);
        textElement.textContent = label.text;

        geneLabelGroup.appendChild(textElement);
        updateBoundingBox(label.x, label.y);
    });
    
    const labelGroup = document.createElementNS(svgNS, "g");
    labels = LabelEngineUpdate(ctx, forceGraph, true);
    labels.forEach(label => {
        const textElement = document.createElementNS(svgNS, "text");
        textElement.setAttribute("x", label.x);
        textElement.setAttribute("y", label.y);
        textElement.setAttribute("font-size", label.fontSize);
        textElement.setAttribute("fill", label.color);
        textElement.setAttribute("stroke", label.stroke);
        textElement.setAttribute("stroke-width", label.strokeWidth);
        textElement.textContent = label.text;

        labelGroup.appendChild(textElement);
        updateBoundingBox(label.x, label.y);
    });
    
    svg.appendChild(geneGroup);
    svg.appendChild(linkGroup);
    svg.appendChild(nodeGroup);
    svg.appendChild(geneLabelGroup);
    svg.appendChild(labelGroup);

    // Calculate final bounding box dimensions
    const width = maxX - minX;
    const height = maxY - minY;

    // Add a 5% buffer to the bounding box
    const bufferX = width * 0.05;
    const bufferY = height * 0.05;
    const finalMinX = minX - bufferX;
    const finalMinY = minY - bufferY;
    const finalWidth = width + 2 * bufferX;
    const finalHeight = height + 2 * bufferY;

    svg.setAttribute("width", finalWidth / 10);
    svg.setAttribute("height", finalHeight / 10);
    svg.setAttribute("viewBox", `${finalMinX} ${finalMinY} ${finalWidth} ${finalHeight}`);


    const serializer = new XMLSerializer();
    const svgString = serializer.serializeToString(svg);

    const svgBlob = new Blob([svgString], { type: "image/svg+xml;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(svgBlob);
    const dateTimeStr = getFormattedDateTime();
    link.download = `pangyplot_${dateTimeStr}.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
