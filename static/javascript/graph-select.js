var boxSelect = null;

document.getElementById(GRAPH_ID).addEventListener('pointerdown', (e) => {
    if (e.shiftKey) {
        e.preventDefault();
        boxSelect = document.createElement('div');
        boxSelect.id = 'boxSelect';
        boxSelect.style.left = e.offsetX.toString() + 'px';
        boxSelect.style.top = e.offsetY.toString() + 'px';
        boxSelectStart = {
            x: e.offsetX,
            y: e.offsetY
        };
        document.getElementsByClassName(GRAPH_CONTAINER_ID)[0].appendChild(this.boxSelect);
    }
});

document.getElementById(GRAPH_ID).addEventListener('pointermove', (e) => {
    if (e.shiftKey && boxSelect) {
        e.preventDefault();
        if (e.offsetX < boxSelectStart.x) {
            boxSelect.style.left = e.offsetX.toString() + 'px';
            boxSelect.style.width = (boxSelectStart.x - e.offsetX).toString() + 'px';
        } else {
            boxSelect.style.left = boxSelectStart.x.toString() + 'px';
            boxSelect.style.width = (e.offsetX - boxSelectStart.x).toString() + 'px';
        }
        if (e.offsetY < boxSelectStart.y) {
            boxSelect.style.top = e.offsetY.toString() + 'px';
            boxSelect.style.height = (boxSelectStart.y - e.offsetY).toString() + 'px';
        } else {
            boxSelect.style.top = boxSelectStart.y.toString() + 'px';
            boxSelect.style.height = (e.offsetY - boxSelectStart.y).toString() + 'px';
        }
    } else if (boxSelect) {
        boxSelect.remove();
        boxSelect = null;
    }
});

const runBoxSelect = (left, bottom, top, right) => {
    const tl = forceGraph.screen2GraphCoords(left, top);
    const br = forceGraph.screen2GraphCoords(right, bottom);
    const hitNodes = [];
    forceGraph.graphData()["nodes"].forEach(node => {
        if (tl.x < node.x && node.x < br.x && br.y > node.y && node.y > tl.y) {
            hitNodes.push(node);
        };
    });
    explode_nodes(hitNodes);
}

document.getElementById(GRAPH_ID).addEventListener('pointerup', (e) => {
    if (e.shiftKey && boxSelect) {
        e.preventDefault();
        let left, bottom, top, right;
        if (e.offsetX < boxSelectStart.x) {
            left = e.offsetX;
            right = boxSelectStart.x;
        } else {
            left = boxSelectStart.x;
            right = e.offsetX;
        }
        if (e.offsetY < boxSelectStart.y) {
            top = e.offsetY;
            bottom = boxSelectStart.y;
        } else {
            top = boxSelectStart.y;
            bottom = e.offsetY;
        }
        runBoxSelect(left, bottom, top, right);
        boxSelect.remove();
        boxSelect = null;
    } else if (boxSelect) {
        boxSelect.remove();
        boxSelect = null;
    }
});