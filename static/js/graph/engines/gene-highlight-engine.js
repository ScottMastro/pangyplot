const HIGHLIGHT_SIZE=80;
const LIGHTNESS_SCALE=0.0;

function geneHighlightEngineDraw(ctx, graphData){
    const zoomFactor = ctx.canvas.__zoom["k"];
    ctx.save();

    var hsize = Math.max(HIGHLIGHT_SIZE, HIGHLIGHT_SIZE*(1/zoomFactor/10));
    
    graphData.nodes.forEach(node => {
        if (node.isVisible && node.isDrawn){
            getNodeAnnotations(node).forEach(geneId => {
                color = stringToColor(geneId, lightness=LIGHTNESS_SCALE);
                outlineNode(node, ctx, 0, hsize, color);
            });
        }
     });


    hsize = Math.max(HIGHLIGHT_SIZE+40, (HIGHLIGHT_SIZE+40)*(1/zoomFactor/10));
    graphData.links.forEach(link => {
        if (link.isVisible && link.isDrawn){
            getLinkAnnotations(link).forEach(geneId => {
                color = stringToColor(geneId, lightness=LIGHTNESS_SCALE);
                outlineLink(link, ctx, 0, hsize, color);
            });
        }
     });

     ctx.restore();

}

//todo
function drawGeneName(ctx, graphData){
    const zoomFactor = ctx.canvas.__zoom["k"];

    annotationNodesX = {};
    annotationNodesY = {};

    let nodes = graphData.nodes;
    for (let i = 0, n = nodes.length, node; i < n; ++i) {
        node = nodes[i];

        for (let j = 0, m = node.annotations.length, k; j < m; ++j) {
            k = node.annotations[j]

            if (!annotationNodesX.hasOwnProperty(k)) {
                annotationNodesX[k] = [];
                annotationNodesY[k] = [];
            }
            annotationNodesX[k].push(node.x)
            annotationNodesY[k].push(node.y);
        } 
    }

    for (var k in annotationNodesX) {

        //f (annotationDict[k].type != "gene"){
        //     continue;
        //}

        var n = annotationNodesX[k].length
        var sumX = annotationNodesX[k].reduce(function(a, b){
            return a + b;
        }, 0);
        var sumY = annotationNodesY[k].reduce(function(a, b){
            return a + b;
        }, 0);

        let x = sumX/n; let y = sumY/n;
        let size = Math.max(72, 72*(1/zoomFactor/10));
    
        drawText(annotationDict[k].gene, ctx, x, y, size, "lightgrey");
    }

}


