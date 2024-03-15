function draw_circle(ctx, x, y, size, color){
    ctx.save();
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, size/2, 0, 2 * Math.PI, false);
    ctx.fill();
    ctx.restore();
}

function draw_circle_outline2(ctx, x, y, size, color, lineWidth=3, fill=null){
    ctx.save();
    ctx.strokeStyle = color;
    ctx.fillStyle = fill;
    ctx.lineWidth = lineWidth;
    ctx.beginPath();
    ctx.arc(x, y, size, 0, 2 * Math.PI, false);
    ctx.stroke();
    ctx.restore();
}

function draw_circle_outline(ctx, x, y, size, color, lineWidth=3, fill=BACKGROUND_COLOR){
    ctx.save();
    ctx.strokeStyle = color;
    ctx.fillStyle = fill;
    ctx.lineWidth = lineWidth;
    ctx.beginPath(); ctx.arc(x, y, size, 0, 2 * Math.PI, false);  
    ctx.stroke();
    ctx.fill();
    ctx.restore();
}

function draw_square(ctx, x, y, size, color){
    ctx.save();
    ctx.fillStyle = color;
    ctx.fillRect(x - size/2, y - size/2, size, size);
    ctx.restore();
}

function draw_rectangle_outline(ctx, x, y, width, height, color, lineWidth=3) {
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

function draw_triangle(ctx, x, y, size, color){
    ctx.save();
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(x, y - size);
    ctx.lineTo(x - size, y + size);
    ctx.lineTo(x + size, y + size);
    ctx.fill();
    ctx.restore();
}

function draw_cross(ctx, x, y, size, color){
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

function outlineNode(node, ctx, shift, size, color) {
    ctx.beginPath();
    ctx.arc(node.x+shift, node.y+shift, size, 0, 2 * Math.PI, false);
    ctx.fillStyle = color;
    ctx.fill();
}

function outlineLink(link, ctx, shift, width, color) {
    ctx.beginPath();
    ctx.moveTo(link.source.x+shift, link.source.y+shift);
    ctx.lineWidth = width;
    ctx.strokeStyle = color;
    ctx.lineTo(link.target.x+shift, link.target.y+shift);
    ctx.lineCap = 'round';
    ctx.stroke();
}

function add_text(text, ctx, x, y, size, color, align="center", baseline="middle") {
    ctx.save();
    ctx.textAlign = align;
    ctx.textBaseline = baseline;
    ctx.fillStyle = color;
    ctx.font = size.toString() + 'px Sans-Serif';
    ctx.fillText(text, x, y);
    ctx.restore();
}
