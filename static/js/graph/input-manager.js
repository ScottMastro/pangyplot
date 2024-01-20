const CAN_CLICK_RANGE = 0.02; //cursor distance in screen coordinates

function addMouseListener(forceGraph, canvasElement){

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

    canvasElement.addEventListener('mousemove', (event) => {
        const canvas = getCanvasBox(canvasElement);
        const coordinates = getCoordinates(canvasElement, event);

        if (forceGraph){
            showCoordinates(coordinates);
            highlightNearestElement(forceGraph.graphData().nodes, coordinates, canvas);
        }
    });

    canvasElement.addEventListener('click', (event) => {
        const canvas = getCanvasBox(canvasElement);
        const coordinates = getCoordinates(canvasElement, event);

        if (forceGraph){

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