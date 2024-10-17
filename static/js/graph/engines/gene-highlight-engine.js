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

//potential speedup: skip frames
function drawGeneName(ctx, graphData, viewport){
    const zoomFactor = ctx.canvas.__zoom["k"];
    const viewportHeight = viewport.y2 - viewport.y1;
    const geneNodes = {};

    // Collect the nodes for each gene
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

    const genePositions = [];
    Object.keys(geneNodes).forEach(geneId => {
        const nodes = geneNodes[geneId];

        const bounds = findNodeBounds(nodes);

        const centerX = bounds.x + bounds.width / 2;
        const centerY = bounds.y + bounds.height / 2;
        genePositions.push({
            geneId: geneId,
            x: centerX,
            y: centerY - bounds.height*0.15,
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


