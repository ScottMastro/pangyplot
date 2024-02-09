const HIGHLIGHT_SIZE=60;
const LIGHTNESS_SCALE=0.0;

function geneHighlightEngineDraw(ctx, graphData){
    const zoomFactor = ctx.canvas.__zoom["k"];
    ctx.save();

    var hsize = Math.max(HIGHLIGHT_SIZE, HIGHLIGHT_SIZE*(1/zoomFactor/10));
    
    graphData.nodes.forEach(node => {
        if (node.isVisible){
            getNodeAnnotations(node).forEach(geneId => {
                color = stringToColor(geneId, lightness=LIGHTNESS_SCALE);
                outlineNode(node, ctx, 0, hsize, color);
            });
        }
     });


    hsize = Math.max(HIGHLIGHT_SIZE+40, (HIGHLIGHT_SIZE+40)*(1/zoomFactor/10));
    graphData.links.forEach(link => {
        if (link.isVisible){
            getLinkAnnotations(link).forEach(geneId => {
                color = stringToColor(geneId, lightness=LIGHTNESS_SCALE);
                outlineLink(link, ctx, 0, hsize, color);
            });
        }
     });

     ctx.restore();

}


