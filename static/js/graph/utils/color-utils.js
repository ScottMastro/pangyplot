const COLOR_CACHE = {};

function hexToRgb(hex) {
    let r = 0, g = 0, b = 0;
    if (hex.length == 4) {
        r = parseInt(hex[1] + hex[1], 16);
        g = parseInt(hex[2] + hex[2], 16);
        b = parseInt(hex[3] + hex[3], 16);
    } else if (hex.length == 7) {
        r = parseInt(hex[1] + hex[2], 16);
        g = parseInt(hex[3] + hex[4], 16);
        b = parseInt(hex[5] + hex[6], 16);
    }
    return [r, g, b];
}

function rgbToHex(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
}

function interpolateColor(color1, color2, factor) {
    let result = color1.slice();
    for (let i = 0; i < 3; i++) {
        result[i] = Math.round(result[i] + factor * (color2[i] - color1[i]));
    }
    return result;
}

function intToColor(seed, adjust=0) {
    const originalSeed = seed;

    if (!(seed in COLOR_CACHE)) {
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

        COLOR_CACHE[originalSeed] = [red,green,blue];
    }
    
    rgb = COLOR_CACHE[originalSeed];
    var l = Math.floor(adjust*255)
    var r = Math.min(255, Math.abs(rgb[0])+l)
    var g = Math.min(255, Math.abs(rgb[1])+l)
    var b = Math.min(255, Math.abs(rgb[2])+l)

    //console.log(r,g,b);
    let color = "rgba(" + r.toString() + "," 
                        + g.toString() + "," 
                        + b.toString() + ")";
    //console.log(color)
    return color;
}

function stringToColor(string, adjust=0){
    if (string in COLOR_CACHE) {
        return COLOR_CACHE[string]
    }
    
    var hash = 0;
    for (var i = 0; i < string.length; i++) {
        var char = string.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; 
    }
    
    color = intToColor(hash, adjust)
    COLOR_CACHE[string] = color
    return(color)
}

function getGradientColor(value, rangeStart, rangeEnd, colorStops) {
    let numStops = colorStops.length;
    if (numStops === 1) {
        return colorStops[0]; // If only one color stop, return it directly.
    }

    let factor = (value - rangeStart) / (rangeEnd - rangeStart);
    factor = Math.min(Math.max(factor, 0), 1); // Clamp factor between 0 and 1

    let scaledFactor = factor * (numStops - 1);
 
    let index = Math.floor(scaledFactor);
    let remainder = scaledFactor - index;

    if (index >= numStops - 1) {
        return colorStops[numStops - 1];
    }

    let color1 = hexToRgb(colorStops[index]);
    let color2 = hexToRgb(colorStops[index + 1]);

    return rgbToHex(...interpolateColor(color1, color2, remainder));
}
