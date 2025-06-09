var DRAGGED_NODE = null;
var FIX_AFTER_DRAG = true;

window.addEventListener('tool-setting-changed', (e) => {
    if (e.detail.type == "anchor"){
        FIX_AFTER_DRAG = e.detail.value;
    }
  });

function dragManagerNodeDragged(node, translate, forceGraph){
    DRAGGED_NODE = node;
    destroySelectionBox();
}

function dragManagerNodeDragEnd(node, forceGraph){
    DRAGGED_NODE = null;    

    if (FIX_AFTER_DRAG){
        node.fx = node.x;
        node.fy = node.y;
    }
}

function dragManagerGetDraggedNode(){
    return DRAGGED_NODE;
}

function dragManagerIsDragging(){
    return DRAGGED_NODE != null;
}
