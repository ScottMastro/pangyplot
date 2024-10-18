const HIGHLIGHT_SIZE=60;
const FONT_SIZE = 180;
const LIGHTNESS_SCALE=0.0;
const GENE_LOCATION = {};

function geneHighlightEngineDraw(ctx, graphData){
    const zoomFactor = ctx.canvas.__zoom["k"];
    ctx.save();

    let renderQueue = [];

    var hsize = Math.max(HIGHLIGHT_SIZE, HIGHLIGHT_SIZE*(1/zoomFactor/10));
    
    graphData.nodes.forEach(node => {
        if (node.isVisible && node.isDrawn) {
            const genes = getNodeAnnotations(node); 
            let n = genes.length; 
            
            genes.forEach(geneId => {
                let color = stringToColor(geneId, LIGHTNESS_SCALE);
                
                renderQueue.push({
                    type: 'node', 
                    element: node, 
                    color: color, 
                    size: hsize * n, 
                    zIndex: n
                });
                n -= 1;
            });
        }
    });


    hsize = Math.max(HIGHLIGHT_SIZE+40, (HIGHLIGHT_SIZE+40)*(1/zoomFactor/10));
    graphData.links.forEach(link => {
        if (link.isVisible && link.isDrawn) {
            const genes = getLinkAnnotations(link);
            let n = genes.length;
            
            genes.forEach(geneId => {
                let color = stringToColor(geneId, LIGHTNESS_SCALE);
                renderQueue.push({
                    type: 'link', 
                    element: link, 
                    color: color, 
                    size: hsize * n, 
                    zIndex: n
                });
                n -= 1;
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


function placeTextOutsideBoundingBox(bounds, viewport, allBounds) {
    const viewportHeight = viewport.y2 - viewport.y1;
    let x = bounds.x + bounds.width / 2;
    let y = bounds.y < viewportHeight / 2 ? bounds.y + bounds.height : bounds.y - bounds.height;
    let position = { x, y };

    if (doesOverlapWithBoundingBox(position, allBounds)) {
        let alternativePositions = [
            { x: bounds.x + bounds.width / 2, y: bounds.y + bounds.height }, // Below
            { x: bounds.x, y: bounds.y }, // Top left
            { x: bounds.x + bounds.width, y: bounds.y }, // Top right
        ];

        for (let alt of alternativePositions) {
            if (!doesOverlapWithBoundingBox(alt, allBounds)) {
                position = alt;
                break;
            }
        }
    }

    const paddingX = (viewport.x2 - viewport.x1) * 0.05; // 5% of viewport width
    const paddingY = (viewport.y2 - viewport.y1) * 0.05; // 5% of viewport height

    if (position.x < viewport.x1 + paddingX) position.x = viewport.x1 + paddingX;
    if (position.x > viewport.x2 - paddingX) position.x = viewport.x2 - paddingX;
    if (position.y < viewport.y1 + paddingY) position.y = viewport.y1 + paddingY;
    if (position.y > viewport.y2 - paddingY) position.y = viewport.y2 - paddingY;

    return position;
}

function doesOverlapWithBoundingBox(position, allBounds) {
    return allBounds.some(bounds => (
        position.x > bounds.x && position.x < bounds.x + bounds.width &&
        position.y > bounds.y && position.y < bounds.y + bounds.height
    ));
}

//potential speedup: skip frames
function drawGeneName(ctx, graphData, viewport){
    const zoomFactor = ctx.canvas.__zoom["k"];
    const viewportHeight = viewport.y2 - viewport.y1;
    const geneNodes = {};

    graphData.nodes.forEach(node => {
        if (node.isVisible && node.isDrawn) {
            const genes = getNodeAnnotations(node); 
            
            genes.forEach(geneId => {                
                if (!geneNodes[geneId]) {
                    geneNodes[geneId] = [];
                }
                geneNodes[geneId].push(node);
            });
        }
    });

    const size = Math.max(FONT_SIZE, FONT_SIZE * (1 / zoomFactor / 10));

    const allBounds = [];

    Object.keys(geneNodes).forEach(geneId => {
        const nodes = geneNodes[geneId];
        const bounds = findNodeBounds(nodes);
        allBounds.push(bounds); 
    });

    const genePositions = [];
    
    Object.keys(geneNodes).forEach(geneId => {
        const nodes = geneNodes[geneId];
        const bounds = findNodeBounds(nodes);
            
        const { x, y } = placeTextOutsideBoundingBox(bounds, viewport, allBounds);
    
        genePositions.push({
            geneId: geneId,
            x: x,
            y: y,
            size: size,
            color: color
        });
    });

    adjustTextPositions(genePositions, viewportHeight* zoomFactor*0.9);

    const bgColor = colorManagerBackgroundColor();

    genePositions.forEach(position => {
        const { geneId, x, y, size } = position;
        const color = stringToColor(geneId, LIGHTNESS_SCALE);
        drawText(geneId, ctx, x, y, size, color, bgColor, size/8);

    });
}


