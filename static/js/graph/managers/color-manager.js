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
    if(should_highlight_link(link)){
        return HIGHLIGHT_LINK_COLOR;
    }

    if (link.class != "node"){
        return LINK_COLOR;
    }

    switch (COLOR_STYLE) {
        case "node_type":
            return colorByType(link.type);        
        case "bubble_size":
            return colorBySize(null);
        case "node_length":
            return colorByLength(link.source.seqLen);
        case "ref_alt":
            return colorByRef(false);
        case "gc_content": 
            return colorByGC(null);
        case "position": 
            return colorByPosition(link.source.start, link.source.end);  
        default:
            return colorByType(link.type);        
    }
}

function colorManagerNodeColor(node){
    switch (COLOR_STYLE) {
        case "node_type":
            return colorByType(node.type);
        case "bubble_size":
            return colorBySize(null);
        case "node_length":
            return colorByLength(node.seqLen);
        case "ref_alt":
            return colorByRef(node.isRef);
        case "gc_content": 
            return colorByGC(null);
        case "position": 
            return colorByPosition(node.start, node.end);
        default:
            return colorByType(node.type);
    }
}

function colorByGC(content){
    return NULL_COLOR;
}

function colorByPosition(start, end){
    if (start == null || end == null){
        return NULL_COLOR;
    }
    const position = (start+end)/2;
    return getGradientColor(position, GRAPH_START_POS, GRAPH_END_POS, [NODE_COLOR1, NODE_COLOR2, NODE_COLOR3]);
}

function colorBySize(size){
    return NULL_COLOR;
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

function colorByLength(length){
    const low = 1;
    const high = 10000;

    const color = getGradientColor(length, low, high, [NODE_COLOR1, NODE_COLOR2, NODE_COLOR3]);
    return color;
}