const HIGHLIGHT_SIZE=60;
const LIGHTNESS_SCALE=0.0;
const HIGHLIGHT_COLOR = "#fab3ae";
const SELECTED_COLOR = "#f44336";
var DRAW_HIGHLIGHT_ON_TOP = false;


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

function highlightSelectedNodes(ctx, graphData) {
    let highlightNodeIds = new Set();
    let selectedNodeIds = new Set();

    count=0;
    graphData.nodes.forEach(node => {

        if(node.isSelected){
            count+=1;
            const selectedNodeId = nodeidSplit(node.__nodeid);
            selectedNodeIds.add(selectedNodeId);

            // todo: summarize all highlighted nodes
            updateGraphInfo(selectedNodeId);
        }
        
        if (node.isHighlighted) {
            count+=1;
            const highlightNodeId = nodeidSplit(node.__nodeid);
            highlightNodeIds.add(highlightNodeId);

            // todo: summarize all highlighted nodes
            updateGraphInfo(highlightNodeId);
        }
    
    });

    const hsize = Math.max(HIGHLIGHT_SIZE, HIGHLIGHT_SIZE * (1 / ZOOM_FACTOR / 10));
    console.log(DRAW_HIGHLIGHT_ON_TOP)
    graphData.nodes.forEach(node => {
        if (node.isSingleton) {
            if (highlightNodeIds.has(node.nodeid) && (!selectedNodeIds.has(node.nodeid) || DRAW_HIGHLIGHT_ON_TOP)){
                outlineNode(node, ctx, 0, hsize, HIGHLIGHT_COLOR);
            } else if (selectedNodeIds.has(node.nodeid)){
                outlineNode(node, ctx, 0, hsize, SELECTED_COLOR);
            }
        } 
    });

    const hsizeLink = Math.max(HIGHLIGHT_SIZE + 40, (HIGHLIGHT_SIZE + 40) * (1 / ZOOM_FACTOR / 10));

    graphData.links.forEach(link => {
        if (link.class === "node"){
            if (highlightNodeIds.has(link.nodeid) && (!selectedNodeIds.has(link.nodeid) || DRAW_HIGHLIGHT_ON_TOP)){
                outlineLink(link, ctx, 0, hsizeLink, HIGHLIGHT_COLOR); 
            } else if (selectedNodeIds.has(link.nodeid)){
                outlineLink(link, ctx, 0, hsizeLink, SELECTED_COLOR); 
            }
        }
    });
}
