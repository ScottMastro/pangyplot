function drawCircle(ctx, x, y, size, color){
    const previousFillStyle = ctx.fillStyle;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, size/2, 0, 2 * Math.PI, false);
    ctx.fill();
    ctx.fillStyle = previousFillStyle;
}

function drawCircleOutline(ctx, x, y, size, color, lineWidth=3, fill=BACKGROUND_COLOR){
    ctx.save();
    ctx.strokeStyle = color;
    ctx.fillStyle = fill;
    ctx.lineWidth = lineWidth;
    ctx.beginPath(); ctx.arc(x, y, size, 0, 2 * Math.PI, false);  
    ctx.stroke();
    ctx.fill();
    ctx.restore();
}

function drawLine(ctx, x1, y1, x2, y2, width, color){
    const previousLineWidth = ctx.lineWidth;
    const previousLineCap = ctx.lineCap;
    const previousStrokeStyle = ctx.strokeStyle;

    ctx.lineWidth = width;
    ctx.lineCap = 'round';
    ctx.strokeStyle = color;

    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();

    ctx.lineWidth = previousLineWidth;
    ctx.lineCap = previousLineCap;
    ctx.strokeStyle = previousStrokeStyle;
}

function drawPath(ctx, path, width, color) {
    ctx.save();

    if (path.length < 2) return;

    ctx.beginPath();
    ctx.moveTo(path[0].x, path[0].y);

    for (let i = 1; i < path.length; i++) {
        ctx.lineTo(path[i].x, path[i].y);
    }

    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.stroke();
    ctx.restore();

}


function drawCircleOutline2(ctx, x, y, size, color, lineWidth=3, fill=null){
    ctx.save();
    ctx.strokeStyle = color;
    ctx.fillStyle = fill;
    ctx.lineWidth = lineWidth;
    ctx.beginPath();
    ctx.arc(x, y, size, 0, 2 * Math.PI, false);
    ctx.stroke();
    ctx.restore();
}

function drawSquare(ctx, x, y, size, color){
    ctx.save();
    ctx.fillStyle = color;
    ctx.fillRect(x - size/2, y - size/2, size, size);
    ctx.restore();
}

function drawRectangleOutline(ctx, x, y, width, height, color, lineWidth=3) {
    ctx.save();
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    const startX = x;
    const startY = y;
    ctx.beginPath();
    ctx.rect(startX, startY, width, height);
    ctx.stroke();
    ctx.restore();
}

function drawTriangle(ctx, x, y, size, color){
    ctx.save();
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(x, y - size);
    ctx.lineTo(x - size, y + size);
    ctx.lineTo(x + size, y + size);
    ctx.fill();
    ctx.restore();
}

function drawCross(ctx, x, y, size, color){
    ctx.save();
    ctx.strokeStyle = color;
    ctx.beginPath(); 
    ctx.moveTo(x - size, y - size);
    ctx.lineTo(x + size, y + size);
    ctx.moveTo(x + size, y - size);
    ctx.lineTo(x - size, y + size);
    ctx.stroke();
    ctx.restore();
}

function drawCross(ctx, x, y, size, width, color){
    ctx.save(); 
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = width;

    ctx.moveTo(x - size, y - size);
    ctx.lineTo(x + size, y + size);
    ctx.moveTo(x + size, y - size);
    ctx.lineTo(x - size, y + size);

    ctx.stroke();
    ctx.restore();
}
function drawRotatedCross(ctx, x, y, size, width, color, angle) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = width;

    ctx.moveTo(-size, -size);
    ctx.lineTo(size, size);
    ctx.moveTo(size, -size);
    ctx.lineTo(-size, size);

    ctx.stroke();

    ctx.restore(); 
}

function outlineNode(node, ctx, shift, size, color) {
    ctx.beginPath();
    ctx.arc(node.x+shift, node.y+shift, size, 0, 2 * Math.PI, false);
    ctx.fillStyle = color;
    ctx.fill();
}

function outlineLink(link, ctx, shift, width, color) {
    const previousLineWidth = ctx.lineWidth;
    const previousLineCap = ctx.lineCap;
    const previousStrokeStyle = ctx.strokeStyle;

    ctx.lineWidth = width;
    ctx.strokeStyle = color;
    ctx.lineCap = 'round';

    ctx.beginPath();
    ctx.moveTo(link.source.x+shift, link.source.y+shift);
    ctx.lineTo(link.target.x+shift, link.target.y+shift);
    ctx.stroke();

    ctx.lineWidth = previousLineWidth;
    ctx.lineCap = previousLineCap;
    ctx.strokeStyle = previousStrokeStyle;
}

function drawText(text, ctx, x, y, size, color, outlineColor=null, outlineWidth=4, align="center", baseline="middle") {
    ctx.save();
    
    ctx.textAlign = align;
    ctx.textBaseline = baseline;
    
    ctx.font = size.toString() + 'px Sans-Serif';
    
    if (outlineColor) {
        ctx.lineWidth = outlineWidth;
        ctx.strokeStyle = outlineColor;
        ctx.strokeText(text, x, y); 
    }

    ctx.fillStyle = color;
    ctx.fillText(text, x, y); 
    
    ctx.restore();
}
