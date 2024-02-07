const NODE_SIZE=50;
const LINK_SIZE=10;
const HOVER_PRECISION=2;


function getLinkWidth(link) {
    if (link.class === "node"){
        return NODE_SIZE;
    }
    return LINK_SIZE;
}

function nodeEffectiveRange(zoomFactor){
    return Math.max(10, (HOVER_PRECISION/zoomFactor));
}

function renderManagerPaintNode(ctx, node) {
    const zoomFactor = ctx.canvas.__zoom["k"]

    let x = node.x; let y = node.y;
    let shape = node.type === "null" ? 1 : 0
    let size = NODE_SIZE;
    if(DEBUG){
        draw_circle_outline2(ctx, x, y, nodeEffectiveRange(zoomFactor)*NODE_SIZE/8 , "orange", 1, null)
    }
    if (!node.isSingleton){
        return;
    }

    let color = getNodeColor(node);
    [
        () => { draw_circle(ctx, x, y, size, color); },
        () => { draw_circle_outline(ctx, x, y, size, color, lineWidth=5); },
        () => { draw_square(ctx, x, y, size, color); },
        () => { draw_cross(ctx, x, y, size, color); },
        () => { draw_triangle(ctx, x, y, size, color); }
    ][shape]();
}

function renderManagerPaintLink(ctx, link){
    const zoomFactor = ctx.canvas.__zoom["k"]

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(link.source.x, link.source.y);
    ctx.lineWidth = getLinkWidth(link); 
    ctx.lineTo(link.target.x, link.target.y);
    ctx.lineCap = 'round';
    ctx.strokeStyle = getLinkColor(link);
    ctx.stroke();
    ctx.restore();
}


function renderManagerPreRender(ctx, forceGraph){
    if (!forceGraph) { return; }
    const zoomFactor = ctx.canvas.__zoom["k"]

    ctx.save();
    geneHighlightEngineDraw(ctx, forceGraph.graphData());
    selectionEngineDraw(ctx, forceGraph.graphData());

    forceGraph.backgroundColor(getBackgroundColor());
    forceGraph.nodeRelSize(nodeEffectiveRange(zoomFactor))

    ctx.restore();
}

function renderManagerPostRender(ctx, forceGraph){
    ctx.save();

    // TODO
    //draw_gene_name(ctx, graphData);

    ctx.restore();
}