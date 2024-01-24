const CAN_CLICK_RANGE = 0.02;
var FUNCTION_KEY_PRESSED = false;
var MOUSE_DOWN = false;

function functionKey(forceGraph, canvasElement, event){
    
    FUNCTION_KEY_PRESSED = event.shiftKey

    forceGraph.enablePanInteraction(FUNCTION_KEY_PRESSED);
    forceGraph.enableZoomInteraction(FUNCTION_KEY_PRESSED);
    
    if (FUNCTION_KEY_PRESSED){
        canvasElement.style.cursor = "grabbing";
    } else{
        canvasElement.style.cursor = "default";
    }
}

function addInputListeners(forceGraph, canvasElement){

    forceGraph.enableZoomInteraction(false);
    forceGraph.enablePanInteraction(false);

    function getCoordinates(canvasElement, event) {
        const rect = canvasElement.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const c = forceGraph.screen2GraphCoords(x, y);
        return {x:c.x, y:c.y, screen:{x:x, y:y}}
    };

    function getCanvasBox(canvasElement) {
        const rect = canvasElement.getBoundingClientRect();
        const tl = forceGraph.screen2GraphCoords(0,0);
        const br = forceGraph.screen2GraphCoords(rect.right-rect.left, rect.bottom-rect.top);
        return { min: {x:tl.x, y:tl.y}, max: {x:br.x, y:br.y} };
    };

    canvasElement.addEventListener('wheel', (event) => { event.preventDefault(); });

    canvasElement.addEventListener('mousemove', (event) => {
        const canvas = getCanvasBox(canvasElement);
        const coordinates = getCoordinates(canvasElement, event);

        functionKey(forceGraph, canvasElement, event)
        
        if (forceGraph){
            showCoordinates(coordinates);
            highlightNearestElement(forceGraph.graphData().nodes, coordinates, canvas);
        }
    });

    canvasElement.addEventListener('click', (event) => {
        const canvas = getCanvasBox(canvasElement);
        const coordinates = getCoordinates(canvasElement, event);

        if (forceGraph && ! FUNCTION_KEY_PRESSED){
            checkNodeClick(forceGraph.graphData().nodes, coordinates, canvas);
        }
    });
}

function checkNodeClick(nodes, coordinates, canvas) {
    const nearestNode = findNearestNode(nodes, coordinates);
    
    if (nearestNode["type"] == "null"){ return }

    const normDist = findNormalizedDistance(nearestNode, coordinates, canvas);

    if (normDist < CAN_CLICK_RANGE){
        const data = { nodes: [nearestNode], source: "clicked" };
        document.dispatchEvent(new CustomEvent("nodesSelected", { detail: data }));
    }
}