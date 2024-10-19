const HIGHLIGHT_SIZE=60;
const FONT_SIZE = 180;
const LIGHTNESS_SCALE=0.0;
const GENE_LOCATION = {};

function geneRenderEngineDraw(ctx, graphData){
    const zoomFactor = ctx.canvas.__zoom["k"];
    ctx.save();

    let renderQueue = [];

    var hsize = Math.max(HIGHLIGHT_SIZE, HIGHLIGHT_SIZE*(1/zoomFactor/10));
    
    //todo: don't loop if no genes are visible
    graphData.nodes.forEach(node => {
        if (node.isVisible && node.isDrawn) {
            const annotations = annotationManagerGetNodeAnnotations(node); 
            let n = 1; 
            
            annotations.forEach(annotation => {
                renderQueue.push({
                    type: 'node', 
                    element: node, 
                    color: annotation.color, 
                    size: hsize * n, 
                    zIndex: n
                });
                n += 1;
            });
        }
    });

    hsize = Math.max(HIGHLIGHT_SIZE+40, (HIGHLIGHT_SIZE+40)*(1/zoomFactor/10));
    graphData.links.forEach(link => {
        if (link.isVisible && link.isDrawn) {
            const annotations = annotationManagerGetLinkAnnotations(link);
            let n = 1;
            
            annotations.forEach(annotation => {
                renderQueue.push({
                    type: 'link', 
                    element: link, 
                    color: annotation.color, 
                    size: hsize * n, 
                    zIndex: n
                });
                n += 1;
            });
        }
    });
    
    renderQueue.sort((a, b) => b.zIndex - a.zIndex);

    renderQueue.forEach(item => {
        if (item.type === 'node') {
            outlineNode(item.element, ctx, 0, item.size, item.color);
        } else if (item.type === 'link') {
            outlineLink(item.element, ctx, 0, item.size, item.color);
        }
    });

    ctx.restore();
}

function adjustTextPositions(genePositions, minDistance) {
    genePositions.sort((a, b) => a.y - b.y);

    for (let i = 1; i < genePositions.length; i++) {
        const prev = genePositions[i - 1];
        const curr = genePositions[i];

        if (Math.abs(curr.y - prev.y) < minDistance) {
            curr.y = prev.y + minDistance;
        }
    }
}

function placeTextOutsideBoundingBox(bounds, viewport) {
    const viewportHeight = viewport.y2 - viewport.y1;
    let x = bounds.x + bounds.width / 2;
    let y = bounds.y < viewportHeight / 2 ? bounds.y + bounds.height : bounds.y - bounds.height;
    let position = { x, y };

    const paddingX = (viewport.x2 - viewport.x1) * 0.05; // 5% of viewport width
    const paddingY = (viewport.y2 - viewport.y1) * 0.05; // 5% of viewport height

    if (position.x < viewport.x1 + paddingX) position.x = viewport.x1 + paddingX;
    if (position.x > viewport.x2 - paddingX) position.x = viewport.x2 - paddingX;
    if (position.y < viewport.y1 + paddingY) position.y = viewport.y1 + paddingY;
    if (position.y > viewport.y2 - paddingY) position.y = viewport.y2 - paddingY;

    return position;
}

//potential speedup: skip frames
function drawGeneName(ctx, graphData, viewport){
    const zoomFactor = ctx.canvas.__zoom["k"];
    const viewportHeight = viewport.y2 - viewport.y1;
    const annotationNodes = {};

    graphData.nodes.forEach(node => {
        if (node.isVisible && node.isDrawn) {
            const annotations = annotationManagerGetNodeAnnotations(node); 
            
            annotations.forEach(annotation => {                
                if (!annotationNodes[annotation.id]) {
                    annotationNodes[annotation.id] = [];
                }
                annotationNodes[annotation.id].push({
                    node: node,
                    exon_number: annotation.exon_number
                });
            });
        }
    });

    const size = Math.max(FONT_SIZE, FONT_SIZE * (1 / zoomFactor / 10));

    const genePositions = [];
    
    Object.keys(annotationNodes).forEach(id => {
        const nodes = annotationNodes[id];

        if (annotationManagerShouldShowExon(id)) {
            const exonGroups = {};
            nodes.forEach(({ node, exon_number }) => {
                if (exon_number) {
                    if (!exonGroups[exon_number]) {
                        exonGroups[exon_number] = [];
                    }
                    exonGroups[exon_number].push(node);
                }
            });
            
            Object.keys(exonGroups).forEach(exon => {
                const exonNodes = exonGroups[exon];
                const bounds = findNodeBounds(exonNodes);
                
                const { x, y } = placeTextOutsideBoundingBox(bounds, viewport);

                genePositions.push({
                    id: id,
                    exon_number: exon,
                    x: x,
                    y: y,
                    size: size/2
                });
            });
        } else {

            const nodesOnly = nodes.map(({ node }) => node);
            const bounds = findNodeBounds(nodesOnly);
            
            const { x, y } = placeTextOutsideBoundingBox(bounds, viewport);

            genePositions.push({
                id: id,
                exon_number: null,
                x: x,
                y: y,
                size: size
            });
        }
    });

    adjustTextPositions(genePositions, viewportHeight* zoomFactor*0.9);

    const bgColor = colorManagerBackgroundColor();

    genePositions.forEach(position => {
        const { id, x, y, size, exon_number } = position;
        const geneName = annotationManagerGetGeneName(id);
        const displayName = exon_number ? `${geneName}:exon${exon_number}` : geneName;
        const color = annotationManagerGetGeneColor(id);
        drawText(displayName, ctx, x, y, size, color, bgColor, size/8);

    });
}