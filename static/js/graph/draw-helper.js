function draw_circle(ctx, x, y, size, color){
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, size, 0, 2 * Math.PI, false);
    ctx.fill();
}
function draw_circle_outline(ctx, x, y, size, color, lineWidth=3, fill=BACKGROUND_COLOR){
    ctx.strokeStyle = color;
    ctx.fillStyle = fill;
    ctx.lineWidth = lineWidth;
    ctx.beginPath(); ctx.arc(x, y, size, 0, 2 * Math.PI, false);  
    ctx.stroke();
    ctx.fill();
}

function draw_square(ctx, x, y, size, color){
    ctx.fillStyle = color;
    ctx.fillRect(x - size/2, y - size/2, size, size);
}

function draw_triangle(ctx, x, y, size, color){
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(x, y - size);
    ctx.lineTo(x - size, y + size);
    ctx.lineTo(x + size, y + size);
    ctx.fill();
}

function draw_cross(ctx, x, y, size, color){
    ctx.strokeStyle = color;
    ctx.beginPath(); 
    ctx.moveTo(x - size, y - size);
    ctx.lineTo(x + size, y + size);
    ctx.moveTo(x + size, y - size);
    ctx.lineTo(x - size, y + size);
    ctx.stroke();
}

function highlight_node(node, ctx, shift, size, color) {
    ctx.beginPath();
    ctx.arc(node.x+shift, node.y+shift, size, 0, 2 * Math.PI, false);
    ctx.fillStyle = color;
    ctx.fill();
}

function highlight_link(link, ctx, shift, width, color) {
    ctx.beginPath();
    ctx.moveTo(link.source.x+shift, link.source.y+shift);
    ctx.lineTo(link.target.x+shift, link.target.y+shift);
    ctx.lineWidth = width;
    ctx.strokeStyle = color;
    ctx.stroke();
}

function add_text(text, ctx, x, y, size, color, align="center", baseline="middle") {
    ctx.textAlign = align;
    ctx.textBaseline = baseline;
    ctx.fillStyle = color;
    ctx.font = size.toString() + 'px Sans-Serif';
    ctx.fillText(text, x, y);
}
