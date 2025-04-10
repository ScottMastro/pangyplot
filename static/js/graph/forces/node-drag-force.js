let PREVIOUS_DRAGGED_POS_FORCE = { x: null, y: null };
const DRAG_FORCE_BASE_STRENGTH=1
var DRAG_FORCE_STRENGTH_DECAY=0.05

function pullNeighborsWhenDragging(alpha) {
    const dragged_node = inputManagerGetDraggedNode();
    if (!dragged_node) {
        PREVIOUS_DRAGGED_POS_FORCE.x = null;
        PREVIOUS_DRAGGED_POS_FORCE.y = null;
        return;
    }

    const { x: prevX, y: prevY } = PREVIOUS_DRAGGED_POS_FORCE;
    PREVIOUS_DRAGGED_POS_FORCE.x = dragged_node.x;
    PREVIOUS_DRAGGED_POS_FORCE.y = dragged_node.y;

    if (prevX == null || prevY == null) return;

    const dx = dragged_node.x - prevX;
    const dy = dragged_node.y - prevY;

    const dragVector = { dx, dy };

    const links = forceGraph.graphData().links;
    const visited = new Set();
    const queue = [{ node: dragged_node, depth: 0 }];
    const maxDepth = 200;

    while (queue.length > 0) {
        const { node, depth } = queue.shift();
        if (visited.has(node) || depth > maxDepth) continue;
        visited.add(node);

        if (node !== dragged_node) {
            const strength = Math.max(0, DRAG_FORCE_BASE_STRENGTH - DRAG_FORCE_STRENGTH_DECAY * depth);
            node.x += dragVector.dx * strength;
            node.y += dragVector.dy * strength;        
        }


        for (const link of links) {
            if (link.source === node && !visited.has(link.target)) {
                queue.push({ node: link.target, depth: depth + 1 });
            } else if (link.target === node && !visited.has(link.source)) {
                queue.push({ node: link.source, depth: depth + 1 });
            }
        }
    }
}

document.addEventListener('wheel', (e) => {
    if (!inputManagerGetDraggedNode()) return;

    if (e.deltaY > 0) {
        DRAG_FORCE_STRENGTH_DECAY = Math.max(DRAG_FORCE_STRENGTH_DECAY - 0.005, 0.01);
    } else {
        DRAG_FORCE_STRENGTH_DECAY = Math.min(DRAG_FORCE_STRENGTH_DECAY + 0.005, 0.1);
    }
});


function renderDragInfluenceCircle(ctx, viewport) {
    const dragged_node = inputManagerGetDraggedNode();
    if (!dragged_node) {
        return;
    }

    // Desired visual radius in screen pixels (e.g. ~50px)
    const screenRadiusPixels = (1/DRAG_FORCE_STRENGTH_DECAY) * 2;

    // Convert screen-space radius to graph-space using viewport
    const canvasWidth = ctx.canvas.width;
    const canvasHeight = ctx.canvas.height;

    const viewportWidthGraph = viewport.x2 - viewport.x1;
    const viewportHeightGraph = viewport.y2 - viewport.y1;

    const pixelsPerGraphX = canvasWidth / viewportWidthGraph;
    const pixelsPerGraphY = canvasHeight / viewportHeightGraph;

    const graphUnitsPerPixel = (1 / pixelsPerGraphX + 1 / pixelsPerGraphY) / 2;
    const graphRadius = screenRadiusPixels * graphUnitsPerPixel;

    ctx.beginPath();
    ctx.arc(dragged_node.x, dragged_node.y, graphRadius, 0, 2 * Math.PI);
    ctx.strokeStyle = 'rgba(0, 150, 255, 0.4)';
    ctx.lineWidth = 5 * graphUnitsPerPixel;
    ctx.setLineDash([15, 5]);
    ctx.stroke();
    ctx.setLineDash([]);

}
