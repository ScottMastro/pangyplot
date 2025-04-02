
function basicRenderPaintNode(ctx, node, svg=false) {

    const zoomFactor = ctx.canvas.__zoom["k"];
    const color = colorManagerNodeColor(node);
    const nodesize = node.size + 3/zoomFactor;
    if (svg) {
        return {
            cx: node.x,
            cy: node.y,
            size: nodesize,
            fill: color
        };
    } else {
        drawCircle(ctx, node.x, node.y, nodesize, color);
    }
    
    //drawSquare(ctx, x, y, size, color);
    //drawCross(ctx, x, y, size, color);
    //drawTriangle(ctx, x, y, size, color);
}

function basicRenderPaintLink(ctx, link, svg=false){

    const color = colorManagerLinkColor(link);
    const zoomFactor = ctx.canvas.__zoom["k"];

    let zoomAdjust = 0;

    if (link.class === "node"){
        zoomAdjust = 3/zoomFactor;
    }
    const linkwidth = link.width+zoomAdjust;
    const x1 = link.source.x;
    const y1 = link.source.y;
    const x2 = link.target.x;
    const y2 = link.target.y;
    
    //todo: add del cross to svg
    if (svg){
        return({
            x1:x1,
            x2:x2,
            y1:y1,
            y2:y2,
            width:linkwidth,
            color:color
        })
    } else{

        drawLine(ctx, x1, y1, x2, y2, linkwidth, color);
        if (link.isDel){
        
            const midX = (x1 + x2) / 2;
            const midY = (y1 + y2) / 2;
            const crossSize = (link.width+zoomAdjust)*2; 
            const angle = Math.atan2(y2 - y1, x2 - x1);
            
            drawRotatedCross(ctx, midX, midY, crossSize, link.width + zoomAdjust, color, angle);
        }
    }
}


