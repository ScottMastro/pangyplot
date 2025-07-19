const SELECTION_MODE = 0;
const PAN_ZOOM_MODE = 1;
const NODE_POP_MODE = 2;

let INPUT_STATE = SELECTION_MODE;
let BUBBLE_MODE = false;

function graphInputStateUpdate(event, forceGraph, canvasElement){
    
    if(event.shiftKey){
        shiftToPanZoomMode(forceGraph, canvasElement);
    } else if(event.ctrlKey || event.metaKey){
        shiftToNodePopMode(forceGraph, canvasElement);
    } else{ 
        shiftToSelectionMode(forceGraph, canvasElement);
    }
    return INPUT_STATE;
}

function shiftToSelectionMode(forceGraph, canvasElement){
    if (INPUT_STATE === SELECTION_MODE) { return; }

    forceGraph.enableZoomPanInteraction(false);

    canvasElement.style.cursor = "default";
    const data = {prevState:INPUT_STATE, state: SELECTION_MODE}
    document.dispatchEvent(new CustomEvent("inputModeChange", { detail: data }));
    INPUT_STATE = SELECTION_MODE;
}

function shiftToPanZoomMode(forceGraph, canvasElement){
    if (INPUT_STATE === PAN_ZOOM_MODE) { return; }
    
    forceGraph.enableZoomPanInteraction(true);

    const data = {prevState:INPUT_STATE, state: PAN_ZOOM_MODE}
    document.dispatchEvent(new CustomEvent("inputModeChange", { detail: data }));
    INPUT_STATE = PAN_ZOOM_MODE;
}


function shiftToNodePopMode(forceGraph, canvasElement){
    if (INPUT_STATE === NODE_POP_MODE) { return; }

    forceGraph.enableZoomPanInteraction(false);

    canvasElement.style.cursor = "crosshair";
    const data = {prevState:INPUT_STATE, state: NODE_POP_MODE}
    document.dispatchEvent(new CustomEvent("inputModeChange", { detail: data }));
    INPUT_STATE = NODE_POP_MODE;
}
