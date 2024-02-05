const HIGHTLIGHT_RANGE = 0.1; //cursor distance in screen coordinates
const CAN_CLICK_RANGE = 0.05;
var PAN_ZOOM_MODE = false;

var BOX_SELECT = null;
var BOX_SELECT_START = null;
var BLOCK_SINGLE_SELECTION = false;

const BOX_SELECT_ID = "box-selection"


function functionKey(forceGraph, canvasElement, event){
    
    PAN_ZOOM_MODE = event.shiftKey;

    forceGraph.enablePanInteraction(PAN_ZOOM_MODE);
    forceGraph.enableZoomInteraction(PAN_ZOOM_MODE);
    
    if (PAN_ZOOM_MODE){
        destroySelectionBox();
    } else{
        canvasElement.style.cursor = "default";
    }
}

function nodeDraggedInput(node){
    destroySelectionBox();
}

function destroySelectionBox(){
    BOX_SELECT = null;
    BOX_SELECT_START = null;

    const boxSelect = document.getElementById(BOX_SELECT_ID);
    if(boxSelect){
        boxSelect.remove();
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

    document.addEventListener('keydown', (event) => {
        functionKey(forceGraph, canvasElement, event);
    });

    canvasElement.addEventListener('mousemove', (event) => {
        const canvas = getCanvasBox(canvasElement);
        const coordinates = getCoordinates(canvasElement, event);

        functionKey(forceGraph, canvasElement, event);


        if (PAN_ZOOM_MODE){
            canvasElement.style.cursor = "grabbing";
        }

        if (!BOX_SELECT && forceGraph){
            showCoordinates(coordinates);
            
            forceGraph.graphData().nodes.forEach(node => node.isHighlighted = false);
            const nearestNode = findNearestNode(forceGraph.graphData().nodes, coordinates);
            if(nearestNode){
                normDist = findNormalizedDistance(nearestNode, coordinates, canvas);
                
                if (normDist < HIGHTLIGHT_RANGE){
                    nearestNode.isHighlighted = true;
                }
            }
        }
    });

    function checkNodeClick(nodes, coordinates, canvas) {

        if (BOX_SELECT){ return }

        const nearestNode = findNearestNode(nodes, coordinates);
        
        if (nearestNode["type"] == "null"){ return }

        const normDist = findNormalizedDistance(nearestNode, coordinates, canvas);

        forceGraph.graphData().nodes.forEach(node => node.isSelected = false);
        if (normDist < CAN_CLICK_RANGE){
            destroySelectionBox();
            nearestNode.isSelected = true;
        }
    }

    canvasElement.addEventListener('click', (event) => {
        const canvas = getCanvasBox(canvasElement);
        const coordinates = getCoordinates(canvasElement, event);

        if (forceGraph && ! PAN_ZOOM_MODE && ! BLOCK_SINGLE_SELECTION){
            checkNodeClick(forceGraph.graphData().nodes, coordinates, canvas);
        }
    });

    canvasElement.addEventListener('pointerdown', (e) => {
        if (!PAN_ZOOM_MODE) {
            //e.preventDefault();
            BOX_SELECT_START = {
                x: e.offsetX,
                y: e.offsetY
            };
        }
    });

    function nodesInSelectionBox(e){
        let left, bottom, top, right;
        if (e.offsetX < BOX_SELECT_START.x) {
            left = e.offsetX;
            right = BOX_SELECT_START.x;
        } else {
            left = BOX_SELECT_START.x;
            right = e.offsetX;
        }
        if (e.offsetY < BOX_SELECT_START.y) {
            top = e.offsetY;
            bottom = BOX_SELECT_START.y;
        } else {
            top = BOX_SELECT_START.y;
            bottom = e.offsetY;
        }

        const tl = forceGraph.screen2GraphCoords(left, top);
        const br = forceGraph.screen2GraphCoords(right, bottom);
        const hitNodes = [];
        forceGraph.graphData().nodes.forEach(node => {
            if (tl.x < node.x && node.x < br.x && br.y > node.y && node.y > tl.y) {
                hitNodes.push(node);
            }
        });
        return hitNodes;
    }

    canvasElement.addEventListener('pointermove', (e) => {
        BLOCK_SINGLE_SELECTION = false;
        DRAW_HIGHLIGHT_ON_TOP = false;

        if (BOX_SELECT_START && !PAN_ZOOM_MODE) {
            //e.preventDefault();

            if (!BOX_SELECT){
                BOX_SELECT = document.createElement('div');
                BOX_SELECT.id = BOX_SELECT_ID;
                BOX_SELECT.style.left = e.offsetX.toString() + 'px';
                BOX_SELECT.style.top = e.offsetY.toString() + 'px';
                canvasElement.appendChild(BOX_SELECT);
            }

            DRAW_HIGHLIGHT_ON_TOP = true;         

            if (e.offsetX < BOX_SELECT_START.x) {
                BOX_SELECT.style.left = e.offsetX.toString() + 'px';
                BOX_SELECT.style.width = (BOX_SELECT_START.x - e.offsetX).toString() + 'px';
            } else {
                BOX_SELECT.style.left = BOX_SELECT_START.x.toString() + 'px';
                BOX_SELECT.style.width = (e.offsetX - BOX_SELECT_START.x).toString() + 'px';
            }
            if (e.offsetY < BOX_SELECT_START.y) {
                BOX_SELECT.style.top = e.offsetY.toString() + 'px';
                BOX_SELECT.style.height = (BOX_SELECT_START.y - e.offsetY).toString() + 'px';
            } else {
                BOX_SELECT.style.top = BOX_SELECT_START.y.toString() + 'px';
                BOX_SELECT.style.height = (e.offsetY - BOX_SELECT_START.y).toString() + 'px';
            }

            forceGraph.graphData().nodes.forEach(node => node.isHighlighted = false);
            nodesInSelectionBox(e).forEach(node => node.isHighlighted = true);

        } else if (BOX_SELECT) {
            destroySelectionBox();
        }
    });

    document.addEventListener('pointerup', (e) => {
        if (BOX_SELECT && !PAN_ZOOM_MODE) {
            e.preventDefault();
            hitNodes = nodesInSelectionBox(e);
            const data = { nodes: hitNodes, source: "drag-selected" };
            //document.dispatchEvent(new CustomEvent("nodesSelected", { detail: data }));

            forceGraph.graphData().nodes.forEach(node => node.isSelected = false);
            nodesInSelectionBox(e).forEach(node => node.isSelected = true);
            BLOCK_SINGLE_SELECTION = true;
            DRAW_HIGHLIGHT_ON_TOP = false;
        } 
        destroySelectionBox();
        
    });

    canvasElement.addEventListener("keydown", (event) => {
        event.preventDefault();
        if (event.code === 'Space' || event.key === ' ') {
            forceGraph.centerAt(0,0,1000);
        }
    });


}
