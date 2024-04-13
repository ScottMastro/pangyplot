const NODE_SIZE=50;
const LINK_SIZE=10;
const HOVER_PRECISION=2;


function getLinkWidth(link, zoomFactor) {
    if (link.class === "node"){
        return NODE_SIZE + 3/zoomFactor;
    }
    return LINK_SIZE;
}

function nodeEffectiveRange(zoomFactor){
    return Math.max(10, (HOVER_PRECISION/zoomFactor));
}

function renderManagerPaintNode(ctx, node, forceGraph) {
    if (!node.isVisible){ return; }

    const zoomFactor = ctx.canvas.__zoom["k"]

    let x = node.x; let y = node.y;
    let shape = node.type === "null" ? 1 : 0
    let size = NODE_SIZE;
    if(DEBUG && false){
        //draw_circle_outline2(ctx, x, y, nodeEffectiveRange(zoomFactor)*NODE_SIZE/8 , "orange", 1, null)
        const nodeBox = nodeNeighborhood(node, forceGraph)
        draw_rectangle_outline(ctx, nodeBox.x, nodeBox.y, nodeBox.width, nodeBox.height, "purple", lineWidth=3);
    }

    let color = getNodeColor(node);
    [
        () => { draw_circle(ctx, x, y, size + 3/zoomFactor, color); },
        () => { draw_circle_outline(ctx, x, y, size, color, lineWidth=5); },
        () => { draw_square(ctx, x, y, size, color); },
        () => { draw_cross(ctx, x, y, size, color); },
        () => { draw_triangle(ctx, x, y, size, color); }
    ][shape]();
}

function renderManagerPaintLink(ctx, link, forceGraph){
    if (!link.isVisible){ return; }

    const zoomFactor = ctx.canvas.__zoom["k"]

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(link.source.x, link.source.y);
    ctx.lineWidth = getLinkWidth(link, zoomFactor); 
    ctx.lineTo(link.target.x, link.target.y);
    ctx.lineCap = 'round';
    ctx.strokeStyle = getLinkColor(link);
    ctx.stroke();
    ctx.restore();
}


function getViewport(ctx, forceGraph, canvasWidth, canvasHeight, buffer){
    // Zoom and pan positions
    const zoomX = ctx.canvas.__zoom["x"];
    const zoomY = ctx.canvas.__zoom["y"];
    const zoomK = ctx.canvas.__zoom["k"];

    const topLeftGraph = forceGraph.screen2GraphCoords(0, 0);
    const bottomRightGraph = forceGraph.screen2GraphCoords(canvasWidth, canvasHeight);

    const viewportWidth = (bottomRightGraph.x - topLeftGraph.x) * buffer;
    const viewportHeight = (bottomRightGraph.y - topLeftGraph.y) * buffer;

    const viewport = {
        x1: topLeftGraph.x - (viewportWidth - (bottomRightGraph.x - topLeftGraph.x)) / 2,
        x2: bottomRightGraph.x + (viewportWidth - (bottomRightGraph.x - topLeftGraph.x)) / 2,
        y1: topLeftGraph.y - (viewportHeight - (bottomRightGraph.y - topLeftGraph.y)) / 2,
        y2: bottomRightGraph.y + (viewportHeight - (bottomRightGraph.y - topLeftGraph.y)) / 2,
    };

    if (DEBUG){
        draw_square(ctx, viewport.x1, viewport.y1, 15/zoomK, "red");
        draw_square(ctx, viewport.x1, viewport.y2, 15/zoomK, "red");
        draw_square(ctx, viewport.x2, viewport.y1, 15/zoomK, "red");
        draw_square(ctx, viewport.x2, viewport.y2, 15/zoomK, "red");
    }

    return viewport;
}

function renderManagerPreRender(ctx, forceGraph, canvasWidth, canvasHeight){
    if (!forceGraph) { return; }
    const zoomFactor = ctx.canvas.__zoom["k"];

    const viewport = getViewport(ctx, forceGraph, canvasWidth, canvasHeight, buffer=0.85)

    function insideViewport(node){
        return node.x > viewport.x1 &&
               node.x < viewport.x2 &&
               node.y > viewport.y1 &&
               node.y < viewport.y2 ;
    }

    forceGraph.graphData().nodes.forEach(node => {
        node.isVisible = insideViewport(node);
    });

    forceGraph.graphData().links.forEach(link => {
        link.isVisible = link.source.isVisible || link.target.isVisible;
    });

    forceGraph.nodeVisibility(node => node.isVisible);

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