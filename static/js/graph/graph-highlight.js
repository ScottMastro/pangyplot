var HIGHLIGHT_NODE = null;
const HIGHLIGHT_SIZE=60;




function draw_gene_outline(ctx, graphData){
    
    var hsize = Math.max(HIGHLIGHT_SIZE, HIGHLIGHT_SIZE*(1/ZOOM_FACTOR/10));
    
    graphData.nodes.forEach(node => {

        getNodeAnnotations(node).forEach(geneId => {
            color = str_to_color(geneId, lightness=LIGHTNESS_SCALE);
            outlineNode(node, ctx, 0, hsize, color);
        });
     });

    hsize = Math.max(HIGHLIGHT_SIZE+40, (HIGHLIGHT_SIZE+40)*(1/ZOOM_FACTOR/10));
    graphData.links.forEach(link => {
        getLinkAnnotations(link).forEach(geneId => {
            color = str_to_color(geneId, lightness=LIGHTNESS_SCALE);
            outlineLink(link, ctx, 0, hsize, color);
        });
     });
}


function higlightSelectedNode(ctx, graphData){
    if (HIGHLIGHT_NODE != null){

        const highlightNodeid = nodeidSplit(HIGHLIGHT_NODE);
        updateGraphInfo(highlightNodeid)


        let hsize = Math.max(HIGHLIGHT_SIZE, HIGHLIGHT_SIZE*(1/ZOOM_FACTOR/10));

        graphData.nodes.forEach(node => {

            if (highlightNodeid === node.nodeid){
                outlineNode(node, ctx, 0, hsize, "red");
                
                //todo remove
                if (HIGHLIGHT_NODE === node.__nodeid){
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


function getMousePosition(canvas, event) {
    const rect = canvas.getBoundingClientRect();
    return {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
    };
}

const canvasElement = document.getElementById("graph");
canvasElement.addEventListener('mousemove', (event) => {
    const mousePos = getMousePosition(canvasElement, event);
    highlightNearestElement(mousePos);
});


function highlightNearestElement(mousePos) {
    const nearestNode = findNearestNode(mousePos);
    if(nearestNode){
        HIGHLIGHT_NODE = nearestNode.__nodeid;

    }

    // Compare distances and decide which one to highlight
    // This part of the logic depends on how you define the distance
    // and how you want to handle the highlighting
}
function findNearestNode(mousePos) {
    if (FORCE_GRAPH){
        const pos = FORCE_GRAPH.screen2GraphCoords(mousePos.x, mousePos.y);
        let nearestNode = null;
        let minDistance = Infinity;

        //const [x, y] = d3.pointer(event, svgElement);

        
        FORCE_GRAPH.graphData().nodes.forEach(node => {
            const smallNodeBoost = node.isSingleton ? 0.9 : 1 
            const distance = Math.sqrt((pos.x - node.x) ** 2 + (pos.y - node.y) ** 2) *smallNodeBoost;

            if (distance < minDistance) {
                minDistance = distance;
                nearestNode = node;
            }
        });


        return nearestNode;
    }
    return null
}
