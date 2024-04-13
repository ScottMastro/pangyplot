const REF_COLOR="#3C5E81";
const HIGHLIGHT_LINK_COLOR="#FF0000";

var BACKGROUND_COLOR="#373737";

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
    }
});

document.addEventListener('updateColorStyle', function(event) {
    COLOR_STYLE = event.detail.style;
});

function getBackgroundColor(){
    return BACKGROUND_COLOR;
}

function getLinkColor(link){
    
    if(should_highlight_link(link)){
        return HIGHLIGHT_LINK_COLOR;
    }

    if (link.class === "node"){        

        switch (COLOR_STYLE) {
            case "node_type":
                return colorByType(link.type);        
            case "bubble_size":
                return colorByType(link.type);        
            case "node_length":
                return colorByLength(link.source.seqLen);
            case "ref_alt":
                return colorByType(link.type);        
            case "gc_content":
                return colorByType(link.type);        
            default:
                return colorByType(link.type);        
        }

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
   


    return LINK_COLOR;
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
            return REF_COLOR;
    }    
}

function colorByLength(length){
    const low = 1;
    const high = 10000;

    const color = getGradientColor(low, high, length);
    return color;
    return REF_COLOR;
}


function getNodeColor(node){
    switch (COLOR_STYLE) {
        case "node_type":
            return colorByType(node.type);        
        case "bubble_size":
            return colorByType(node.type);
        case "node_length":
            return colorByLength(node.seqLen);
        case "ref_alt":
            return colorByType(node.type);
        case "gc_content":
            return colorByType(node.type);     
        default:
            return colorByType(node.type);
    }

}
