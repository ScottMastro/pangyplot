const HIGHTLIGHT_RANGE = 0.1; //cursor distance in screen coordinates
const CAN_CLICK_RANGE = 0.05;

var PAN_ZOOM_MODE = false;

const BOX_SELECT_ID = "box-selection"
var BOX_SELECT = null;
var BOX_SELECT_START = null;
var BLOCK_SINGLE_SELECTION = false;


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

function destroySelectionBox(){
    BOX_SELECT = null;
    BOX_SELECT_START = null;

    const boxSelect = document.getElementById(BOX_SELECT_ID);
    if(boxSelect){
        boxSelect.remove();
    }
}

function selectionEngineKeyDown(event, forceGraph, canvasElement){

    functionKey(forceGraph, canvasElement, event);
    
}

function selectionEngineMouseMove(event, forceGraph, canvasElement, canvas, coordinates){

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
}

function selectionEngineMouseClick(event, forceGraph, canvasElement, canvas, coordinates){
    if (forceGraph && ! PAN_ZOOM_MODE && ! BLOCK_SINGLE_SELECTION){
        checkNodeClick(forceGraph.graphData().nodes, coordinates, canvas);
    }
}

function selectionEnginePointerDown(event, forceGraph, canvasElement, canvas, coordinates){
    if (!PAN_ZOOM_MODE) {
        //e.preventDefault();
        BOX_SELECT_START = {
            x: event.offsetX,
            y: event.offsetY
        };
    }
}

function selectionEnginePointerMove(event, forceGraph, canvasElement, canvas, coordinates){
    BLOCK_SINGLE_SELECTION = false;
    DRAW_HIGHLIGHT_ON_TOP = false;

    if (BOX_SELECT_START && !PAN_ZOOM_MODE) {
        //event.preventDefault();

        const offsetX = event.offsetX;
        const offsetY = event.offsetY;

        if (!BOX_SELECT){
            BOX_SELECT = document.createElement('div');
            BOX_SELECT.id = BOX_SELECT_ID;
            BOX_SELECT.style.left = offsetX.toString() + 'px';
            BOX_SELECT.style.top = offsetY.toString() + 'px';
            canvasElement.appendChild(BOX_SELECT);
        }

        DRAW_HIGHLIGHT_ON_TOP = true;         

        if (offsetX < BOX_SELECT_START.x) {
            BOX_SELECT.style.left = offsetX.toString() + 'px';
            BOX_SELECT.style.width = (BOX_SELECT_START.x - offsetX).toString() + 'px';
        } else {
            BOX_SELECT.style.left = BOX_SELECT_START.x.toString() + 'px';
            BOX_SELECT.style.width = (offsetX - BOX_SELECT_START.x).toString() + 'px';
        }
        if (offsetY < BOX_SELECT_START.y) {
            BOX_SELECT.style.top = offsetY.toString() + 'px';
            BOX_SELECT.style.height = (BOX_SELECT_START.y - offsetY).toString() + 'px';
        } else {
            BOX_SELECT.style.top = BOX_SELECT_START.y.toString() + 'px';
            BOX_SELECT.style.height = (offsetY - BOX_SELECT_START.y).toString() + 'px';
        }

        forceGraph.graphData().nodes.forEach(node => node.isHighlighted = false);
        nodesInSelectionBox(event, forceGraph).forEach(node => node.isHighlighted = true);

    } else if (BOX_SELECT) {
        destroySelectionBox();
    }
}

function selectionEnginePointerUp(event, forceGraph, canvasElement, canvas, coordinates){
        if (BOX_SELECT && !PAN_ZOOM_MODE) {
            event.preventDefault();
            hitNodes = nodesInSelectionBox(event, forceGraph);
            const data = { nodes: hitNodes, source: "drag-selected" };
            //document.dispatchEvent(new CustomEvent("nodesSelected", { detail: data }));

            forceGraph.graphData().nodes.forEach(node => node.isSelected = false);
            hitNodes.forEach(node => node.isSelected = true);
            BLOCK_SINGLE_SELECTION = true;
            DRAW_HIGHLIGHT_ON_TOP = false;
        } 
        destroySelectionBox();
        
}


function checkNodeClick(nodes, coordinates, canvas) {

    if (BOX_SELECT){ return }

    const nearestNode = findNearestNode(nodes, coordinates);
    
    if (nearestNode["type"] == "null"){ return }

    const normDist = findNormalizedDistance(nearestNode, coordinates, canvas);

    nodes.forEach(node => node.isSelected = false);
    if (normDist < CAN_CLICK_RANGE){
        destroySelectionBox();
        nearestNode.isSelected = true;
    }
}

function nodesInSelectionBox(event, forceGraph){
    let left, bottom, top, right;
    if (event.offsetX < BOX_SELECT_START.x) {
        left = event.offsetX;
        right = BOX_SELECT_START.x;
    } else {
        left = BOX_SELECT_START.x;
        right = event.offsetX;
    }
    if (event.offsetY < BOX_SELECT_START.y) {
        top = event.offsetY;
        bottom = BOX_SELECT_START.y;
    } else {
        top = BOX_SELECT_START.y;
        bottom = event.offsetY;
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
