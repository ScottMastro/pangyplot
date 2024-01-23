var HIGHLIGHT_NODE = null;
const HIGHLIGHT_SIZE=60;
const HIGHTLIGHT_RANGE = 0.1; //cursor distance in screen coordinates
const LIGHTNESS_SCALE=0.0;


function drawGeneOutline(ctx, graphData){
    
    var hsize = Math.max(HIGHLIGHT_SIZE, HIGHLIGHT_SIZE*(1/ZOOM_FACTOR/10));
    
    graphData.nodes.forEach(node => {

        getNodeAnnotations(node).forEach(geneId => {
            color = stringToColor(geneId, lightness=LIGHTNESS_SCALE);
            outlineNode(node, ctx, 0, hsize, color);
        });
     });

    hsize = Math.max(HIGHLIGHT_SIZE+40, (HIGHLIGHT_SIZE+40)*(1/ZOOM_FACTOR/10));
    graphData.links.forEach(link => {
        getLinkAnnotations(link).forEach(geneId => {
            color = stringToColor(geneId, lightness=LIGHTNESS_SCALE);
            outlineLink(link, ctx, 0, hsize, color);
        });
     });
}

function higlightSelectedNode(ctx, graphData){
    if (HIGHLIGHT_NODE != null){

        const highlightNodeid = nodeidSplit(HIGHLIGHT_NODE.__nodeid);
        updateGraphInfo(highlightNodeid)

        let hsize = Math.max(HIGHLIGHT_SIZE, HIGHLIGHT_SIZE*(1/ZOOM_FACTOR/10));

        graphData.nodes.forEach(node => {

            if (highlightNodeid === node.nodeid && node.isSingleton){
                outlineNode(node, ctx, 0, hsize, "red");
                
                //todo remove
                if (highlightNodeid === node.__nodeid){
                    color="green";
                    draw_circle_outline(ctx, node.x, node.y, Math.max(HIGHLIGHT_SIZE, HIGHLIGHT_SIZE/ZOOM_FACTOR/10), color, lineWidth=3/ZOOM_FACTOR, fill="rgba(0, 0, 0, 0)");
                }
            } 
        });

        hsize = Math.max(HIGHLIGHT_SIZE+40, (HIGHLIGHT_SIZE+40)*(1/ZOOM_FACTOR/10));

        graphData.links.forEach(link => {
            if (link.class === "node" && link.nodeid === highlightNodeid){
                color="red";

                outlineLink(link, ctx, 0, hsize, color);

            }
        });
    }
}

function highlightNearestElement(nodes, coordinates, canvas) {
    const nearestNode = findNearestNode(nodes, coordinates);
    if(nearestNode){
        normDist = findNormalizedDistance(nearestNode, coordinates, canvas);
        
        if (normDist < HIGHTLIGHT_RANGE){
            HIGHLIGHT_NODE = nearestNode;
        } else{
            HIGHLIGHT_NODE = null;
        }
    }
}