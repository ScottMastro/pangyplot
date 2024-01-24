const HIGHLIGHT_SIZE=60;
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

function highlightSelectedNodes(ctx, graphData) {
    let highlightNodeIds = new Set();
    count=0;
    graphData.nodes.forEach(node => {

        if (node.isHighlighted) {
            count+=1;
            const highlightNodeId = nodeidSplit(node.__nodeid);
            highlightNodeIds.add(highlightNodeId);

            // todo: summarize all highlighted nodes
            updateGraphInfo(highlightNodeId);
        }
    });
    console.log(count);

    const hsize = Math.max(HIGHLIGHT_SIZE, HIGHLIGHT_SIZE * (1 / ZOOM_FACTOR / 10));
    const color = "red";

    graphData.nodes.forEach(node => {
        if (node.isSingleton && highlightNodeIds.has(node.nodeid)) {
            outlineNode(node, ctx, 0, hsize, color);
        }
    });

    const hsizeLink = Math.max(HIGHLIGHT_SIZE + 40, (HIGHLIGHT_SIZE + 40) * (1 / ZOOM_FACTOR / 10));

    graphData.links.forEach(link => {
        if (link.class === "node" && highlightNodeIds.has(link.nodeid)) {
            outlineLink(link, ctx, 0, hsizeLink, color); 
        }
    });
}
