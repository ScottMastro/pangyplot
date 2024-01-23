const COLOR_CACHE = {};

const REF_COLOR="#3C5E81";
const HIGHLIGHT_LINK_COLOR="#FF0000";

var BACKGROUND_COLOR="#373737";

var NODE_COLOR1="#0762E5";
var NODE_COLOR2="#F2DC0F";
var NODE_COLOR3="#FF6700";
var LINK_COLOR="#969696";


document.addEventListener('updateColor', function(event) {
    if (event.detail.type === "node"){
        NODE_COLOR1 = event.detail.color1;
        NODE_COLOR2 = event.detail.color2;
        NODE_COLOR3 = event.detail.color3;
    } else if (event.detail.type === "link"){
        LINK_COLOR = event.detail.color;
    } else if (event.detail.type === "background"){
        BACKGROUND_COLOR = event.detail.color;
    }
});


function getBackgroundColor(){
    return BACKGROUND_COLOR;
}

function getLinkColor(link){

    if (link.class === "node"){        
        switch (link.type) {
            case "segment":
                return NODE_COLOR1;
            case "bubble":
                return NODE_COLOR2;
            case "chain":
                return NODE_COLOR3;
            default:
                return REF_COLOR;
        }
    }
   
    if(should_highlight_link(link)){
        return HIGHLIGHT_LINK_COLOR;
    }

    return LINK_COLOR;
}

function getNodeColor(node){
    switch (node.type) {
        case "segment":
            return NODE_COLOR1;
        case "bubble":
            return NODE_COLOR2;
        case "chain":
            return NODE_COLOR3;
        case "null":
            return LINK_COLOR;        
        default:
            return REF_COLOR;
    }    
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
    var r = Math.min(255, rgb[0]+l)
    var g = Math.min(255, rgb[1]+l)
    var b = Math.min(255, rgb[2]+l)

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