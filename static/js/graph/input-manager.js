function setupEngineInputListeners(forceGraph, canvasElement){

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
    

    forceGraph.enableZoomInteraction(false);
    forceGraph.enablePanInteraction(false);


    // keyboard

    document.addEventListener('keydown', (event) => {

        if (event.code === 'Space' || event.key === ' ') {
            forceGraph.centerAt(0,0,1000);
        }


    });

    canvasElement.addEventListener("keydown", (event) => {
        event.preventDefault();


    });


    // mouse

    canvasElement.addEventListener('wheel', (event) => { 
        event.preventDefault();

    });

    // pointer

    canvasElement.addEventListener('mousemove', (event) => {
        const canvas = getCanvasBox(canvasElement);
        const coordinates = getCoordinates(canvasElement, event);

        selectionEngineMouseMove(event, forceGraph, canvasElement, canvas, coordinates);
    });

    canvasElement.addEventListener('pointermove', (event) => {
        const canvas = getCanvasBox(canvasElement);
        const coordinates = getCoordinates(canvasElement, event);

        selectionEnginePointerMove(event, forceGraph, canvasElement, canvas, coordinates);

    });

    canvasElement.addEventListener('pointerdown', (event) => {
        const canvas = getCanvasBox(canvasElement);
        const coordinates = getCoordinates(canvasElement, event);

        selectionEnginePointerDown(event, forceGraph, canvasElement, canvas, coordinates);
    });

    
    document.addEventListener('pointerup', (event) => {
        const canvas = getCanvasBox(canvasElement);
        const coordinates = getCoordinates(canvasElement, event);
        
        selectionEnginePointerUp(event, forceGraph, canvasElement, canvas, coordinates);        
    });


    canvasElement.addEventListener('click', (event) => {
        const canvas = getCanvasBox(canvasElement);
        const coordinates = getCoordinates(canvasElement, event);

        selectionEngineMouseClick(event, forceGraph, canvasElement, canvas, coordinates);
    });

}
