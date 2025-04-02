// clicking variables
const HIGHTLIGHT_RANGE = 0.1; //cursor distance in screen coordinates
const CAN_CLICK_RANGE = 0.05;

// multiselect variables
const BOX_SELECT_ID = "box-selection"
var BOX_SELECT = null;
var BOX_SELECT_START = null;
var BLOCK_SINGLE_SELECTION = false;

// drawing variables
var DRAW_HIGHLIGHT_ON_TOP = false;
const HIGHLIGHT_COLOR = "#fab3ae";
const SELECTED_COLOR = "#f44336";
var IS_DRAGGING_NODE = false;


function selectionEnginePointerDown(event, forceGraph, canvasElement, canvas, coordinates, inputState){
    if (inputState!=PAN_ZOOM_MODE) {
        BOX_SELECT_START = { x: event.offsetX, y: event.offsetY };
    }
}

function selectionEnginePointerUp(event, forceGraph, canvasElement, canvas, coordinates, inputState){
    if (BOX_SELECT && inputState!=PAN_ZOOM_MODE) {
        hitNodes = nodesInSelectionBox(event, forceGraph);
        forceGraph.graphData().nodes.forEach(node => node.isSelected = false);
        hitNodes.forEach(node => node.isSelected = true);
        BLOCK_SINGLE_SELECTION = true;
        DRAW_HIGHLIGHT_ON_TOP = false;
    }

    IS_DRAGGING_NODE = false;
    destroySelectionBox();
}

function selectionEnginePointerMove(event, forceGraph, canvasElement, canvas, coordinates, inputState){
    BLOCK_SINGLE_SELECTION = false;
    DRAW_HIGHLIGHT_ON_TOP = false;

    if (BOX_SELECT_START && inputState!=PAN_ZOOM_MODE) {
        DRAW_HIGHLIGHT_ON_TOP = true;         
        const offsetX = event.offsetX;
        const offsetY = event.offsetY;

        if (!BOX_SELECT){
            BOX_SELECT = document.createElement('div');
            BOX_SELECT.id = BOX_SELECT_ID;
            BOX_SELECT.style.left = offsetX.toString() + 'px';
            BOX_SELECT.style.top = offsetY.toString() + 'px';
            canvasElement.appendChild(BOX_SELECT);
        }

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
    } else { // highlight nearest node when not rectangle selecting
        forceGraph.graphData().nodes.forEach(node => node.isHighlighted = false);
        const nearestNode = findNearestNode(forceGraph.graphData().nodes, coordinates);
        if(!IS_DRAGGING_NODE && nearestNode){
            normDist = findNormalizedDistance(nearestNode, coordinates, canvas);
            if (normDist < HIGHTLIGHT_RANGE){
                nearestNode.isHighlighted = true;
            }
        }
    }
}

function selectionEngineMouseClick(event, forceGraph, canvasElement, canvas, coordinates, inputState){
    if (!BOX_SELECT && inputState==SELECTION_MODE && ! BLOCK_SINGLE_SELECTION){
        const nearestNode = findNearestNode(forceGraph.graphData().nodes, coordinates);
        if (nearestNode == null || nearestNode["type"] == "null"){ return }
        const normDist = findNormalizedDistance(nearestNode, coordinates, canvas);
    
        forceGraph.graphData().nodes.forEach(node => node.isSelected = false);
        if (normDist < CAN_CLICK_RANGE){
            destroySelectionBox();
            nearestNode.isSelected = true;
            console.log("clicked:", nearestNode);

            const connectedEdges = forceGraph.graphData().links.filter(link => 
                link.source === nearestNode || link.target === nearestNode
            );
            console.log("connected edges:", connectedEdges);
        }
    }
}

function destroySelectionBox(){
    BOX_SELECT = null;
    BOX_SELECT_START = null;

    const boxSelect = document.getElementById(BOX_SELECT_ID);
    if(boxSelect){ boxSelect.remove(); }
}

document.addEventListener('inputModeChange', function(event) {
    if (event.detail.state == PAN_ZOOM_MODE){
        destroySelectionBox();
    }
});

function selectionEngineNodeDragged(node){
    IS_DRAGGING_NODE = true;
    destroySelectionBox();
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
        if (node.isDrawn && tl.x < node.x && node.x < br.x && br.y > node.y && node.y > tl.y) {
            hitNodes.push(node);
        }
    });
    return hitNodes;
}


function selectionEngineDraw(ctx, graphData) {
    ctx.save();

    let highlightNodeIds = new Set();
    let selectedNodeIds = new Set();

    count=0;
    graphData.nodes.forEach(node => {

        if(node.class != "text" && node.isSelected){
            count+=1;
            const selectedNodeId = nodeidSplit(node.__nodeid);
            selectedNodeIds.add(selectedNodeId);
            
            if (count == 1){
                // todo: summarize all highlighted nodes
                updateGraphInfo(selectedNodeId);
            }
        }
        
        if (node.isHighlighted) {
            count+=1;
            const highlightNodeId = nodeidSplit(node.__nodeid);
            highlightNodeIds.add(highlightNodeId);
        }

    });

    const zoomFactor = ctx.canvas.__zoom["k"];

    graphData.nodes.forEach(node => {
        if (node.isSingleton) {
            let hsize = node.size+50 + 3/zoomFactor;

            if (highlightNodeIds.has(node.nodeid) && (!selectedNodeIds.has(node.nodeid) || DRAW_HIGHLIGHT_ON_TOP)){
                outlineNode(node, ctx, 0, hsize, HIGHLIGHT_COLOR);
            } else if (selectedNodeIds.has(node.nodeid)){
                outlineNode(node, ctx, 0, hsize, SELECTED_COLOR);
            }
        } 
    });

    graphData.links.forEach(link => {
        if (link.class === "node"){

            let hsize = link.width+50 + 3/zoomFactor;

            if (highlightNodeIds.has(link.nodeid) && (!selectedNodeIds.has(link.nodeid) || DRAW_HIGHLIGHT_ON_TOP)){
                outlineLink(link, ctx, 0, hsize, HIGHLIGHT_COLOR); 
            } else if (selectedNodeIds.has(link.nodeid)){
                outlineLink(link, ctx, 0, hsize, SELECTED_COLOR); 
            }
        }
    });

    ctx.restore();
}