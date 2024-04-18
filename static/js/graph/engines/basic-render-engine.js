const NODE_SIZE=50;
const LINK_SIZE=10;

function basicRenderPaintNode(ctx, node) {

    const zoomFactor = ctx.canvas.__zoom["k"];
    const color = colorManagerNodeColor(node);
    
    if (node.type === "null"){
        drawCircleOutline(ctx, node.x, node.y, NODE_SIZE, color, lineWidth=5);
    } else{
        drawCircle(ctx, node.x, node.y, NODE_SIZE + 3/zoomFactor, color);
    }

    //drawSquare(ctx, x, y, size, color);
    //drawCross(ctx, x, y, size, color);
    //drawTriangle(ctx, x, y, size, color);
}

function basicRenderPaintLink(ctx, link){

    const color = colorManagerLinkColor(link);

    let width = LINK_SIZE;
    if (link.class === "node"){
        const zoomFactor = ctx.canvas.__zoom["k"]
        width = NODE_SIZE + 3/zoomFactor;
    }

    const x1 = link.source.x;
    const y1 = link.source.y;
    const x2 = link.target.x;
    const y2 = link.target.y;

    drawLine(ctx, x1, y1, x2, y2, width, color);
}


