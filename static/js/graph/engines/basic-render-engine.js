const NODE_SIZE=50;
const LINK_SIZE=10;

function basicRenderPaintNode(ctx, node, svg=false) {

    const zoomFactor = ctx.canvas.__zoom["k"];
    const color = colorManagerNodeColor(node);
    
    if (svg) {
        return node.type === "null" ? {
            cx: node.x,
            cy: node.y,
            size: NODE_SIZE,
            stroke: color,
            fill: BACKGROUND_COLOR,
            strokeWidth: 5
        } : {
            cx: node.x,
            cy: node.y,
            size: NODE_SIZE,
            fill: color
        };
    } else {
        if (node.type === "null") {
            drawCircleOutline(ctx, node.x, node.y, NODE_SIZE, color, lineWidth=5);
        } else {
            drawCircle(ctx, node.x, node.y, NODE_SIZE + 3/zoomFactor, color);
        }
    }
    
    //drawSquare(ctx, x, y, size, color);
    //drawCross(ctx, x, y, size, color);
    //drawTriangle(ctx, x, y, size, color);
}

function basicRenderPaintLink(ctx, link, svg=false){

    const color = colorManagerLinkColor(link);

    let width = LINK_SIZE;
    let zoomAdjust = 0;

    if (link.class === "node"){
        zoomAdjust = 3/(ctx.canvas.__zoom["k"]);
        width = NODE_SIZE;
    }

    const x1 = link.source.x;
    const y1 = link.source.y;
    const x2 = link.target.x;
    const y2 = link.target.y;

    if (svg){
        return({
            x1:x1,
            x2:x2,
            y1:y1,
            y2:y2,
            width:width,
            color:color
        })
    } else{
        drawLine(ctx, x1, y1, x2, y2, width+zoomAdjust, color);
    }
}


