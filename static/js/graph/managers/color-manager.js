var BACKGROUND_COLOR="#373737";

const HIGHLIGHT_LINK_COLOR="#FF0000";

const NULL_COLOR="#3C5E81";
var NODE_COLOR1="#0762E5";
var NODE_COLOR2="#F2DC0F";
var NODE_COLOR3="#FF6700";
var LINK_COLOR="#969696";

var COLOR_STYLE="default";

document.addEventListener('updateColor', function(event) {
    if (event.detail.type === "node"){
        NODE_COLOR1 = event.detail.color1;
        NODE_COLOR2 = event.detail.color2;
        NODE_COLOR3 = event.detail.color3;
    } else if (event.detail.type === "link"){
        LINK_COLOR = event.detail.color;
    } else if (event.detail.type === "background"){
        BACKGROUND_COLOR = event.detail.color;
    } else if (event.detail.type === "style"){
        COLOR_STYLE = event.detail.style;
    }
});

function colorManagerBackgroundColor(){
    return BACKGROUND_COLOR;
}

function colorManagerLinkColor(link){

    //todo: move logic elsewhere
    if(pathManagerShouldHighlightLink(link)){
        return HIGHLIGHT_LINK_COLOR;
    }

    if (link.class != "node"){
        return LINK_COLOR;
    }

    switch (COLOR_STYLE) {
        case "node_type":
            return colorByType(link.type);        
        case "bubble_size":
            return colorBySize(link.source.largestChild);
        case "node_length":
            return colorByLength(link.source.seqLen);
        case "ref_alt":
            return colorByRef(link.isRef);
        case "gc_content":
            return colorByGC(link.source.gcCount, link.source.seqLen);
        case "position":
            return colorByPosition(link.source.start, link.source.end);  
        case "solid":
            return NODE_COLOR1;
        default:
            return colorByType(link.type);        
    }
}

function colorManagerNodeColor(node){
    switch (COLOR_STYLE) {
        case "node_type":
            return colorByType(node.type);
        case "bubble_size":
            return colorBySize(node.largestChild);
        case "node_length":
            return colorByLength(node.seqLen);
        case "ref_alt":
            return colorByRef(node.isRef);
        case "gc_content": 
            return colorByGC(node.gcCount, node.seqLen);
        case "position":
            return colorByPosition(node.start, node.end);
        case "solid":
                return NODE_COLOR1;    
        default:
            return colorByType(node.type);
    }
}

function colorByGC(count, total){
    if (count == null || isNaN(count) || count < 0) {
        return NULL_COLOR;
    } if (total == null || isNaN(total) || total <= 0) {
        return NULL_COLOR;
    }
    if (total < 3){ return NULL_COLOR ; }
    
    const pcGC = count/total;
    const color = getGradientColor(pcGC, 0, 1, [NODE_COLOR1, NODE_COLOR2, NODE_COLOR3]);

    return color;
}

function colorByPosition(start, end){
    if (start == null || isNaN(start) || end == null || isNaN(end)) {
        return NULL_COLOR;
    }
    const position = (start+end)/2;
    return getGradientColor(position, GRAPH_START_POS, GRAPH_END_POS, [NODE_COLOR1, NODE_COLOR2, NODE_COLOR3]);
}

function colorBySize(size){
    const low = 0;
    const high = 12;

    if (size == null || isNaN(size) || size <= 0) {
        return NULL_COLOR;
    }

    const color = getGradientColor(size, low, high, [NODE_COLOR1, NODE_COLOR2, NODE_COLOR3]);

    return color;
}

function colorByType(type){
    switch (type) {
        case "segment":
            return NODE_COLOR1;
        case "bubble":
            return NODE_COLOR2;
        case "chain":
            return NODE_COLOR3;
        case "null":
            return LINK_COLOR;        
        default:
            return NULL_COLOR;
    }    
}

function colorByRef(isRef){
    return isRef ? NODE_COLOR1 : NODE_COLOR3;
}

function colorByLength(length) {
    const low = 0;
    const high = 5;

    if (length == null || isNaN(length) || length <= 0) {
        return NULL_COLOR;
    }

    const logLength = Math.log10(length);
    const color = getGradientColor(logLength, low, high, [NODE_COLOR1, NODE_COLOR2, NODE_COLOR3]);

    return color;
}
