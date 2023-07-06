


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

const COLOR_CACHE = {}
function intToColor(seed) {
    if (COLOR_CACHE.hasOwnProperty(seed)) { return COLOR_CACHE[seed]; }
    const originalSeed = seed;
    var a = 1664525;
    var c = 1013904223;
    var m = Math.pow(2, 32);

    // Generate three random numbers between 0 and 255
    var red = (seed * a + c) % m;
    seed = (red * a + c) % m;
    var green = seed;
    seed = (green * a + c) % m;
    var blue = seed;

    // Normalize to the range 0-255
    red = Math.floor((red / m) * 256);
    green = Math.floor((green / m) * 256);
    blue = Math.floor((blue / m) * 256);

    // Convert to a hexadecimal string and pad with zeros if necessary
    red = ("00" + red.toString(16)).slice(-2);
    green = ("00" + green.toString(16)).slice(-2);
    blue = ("00" + blue.toString(16)).slice(-2);

    // Combine into a single color string
    var color = "#" + red + green + blue;
    COLOR_CACHE[originalSeed] = color;
    return color;
}