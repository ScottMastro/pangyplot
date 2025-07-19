function forceCenterEachNode(alpha) {
    for (let node of forceGraph.graphData().nodes) {
        if (node.isSingleton){
            node.vx += (node.initX - node.x) * 0.01 * alpha;
            node.vy += (node.initY - node.y) * 0.01 * alpha;
        } else if (node.class = "end"){
            node.vx += (node.initX - node.x) * 0.02 * alpha;
            node.vy += (node.initY - node.y) * 0.02 * alpha;
        } else{
            node.vx += (node.initX - node.x) * 0.02 * alpha;
            node.vy += (node.initY - node.y) * 0.02 * alpha;
        }
    }
}

function forceSpreadX(alpha) {
    const nodes = forceGraph.graphData().nodes;

    let minX = Infinity, maxX = -Infinity;
    for (const node of nodes) {
        if (node.x < minX) minX = node.x;
        if (node.x > maxX) maxX = node.x;
    }

    const midX = (minX + maxX) / 2;
    const range = (maxX-minX)/2;
    let i = 0; 
    for (let node of nodes) {
        const targetX = node.x < midX ? minX : maxX;
        const strength = 1 - Math.abs(targetX - node.x)/range;

        node.vx += (node.x < midX ? -1 : 1) * 1000* strength * alpha;

    }
}

function pullTextToAnchor(alpha) {
    const threshold = 5000; // Define the snapping threshold distance

    for (let node of forceGraph.graphData().nodes) {
        if (node.class === "text") {
            let dx = node.anchorX - node.x;
            let dy = node.anchorY - node.y;

            // Calculate the current distance between the node and the anchor
            let distance = Math.sqrt(dx * dx + dy * dy);

            if (distance > threshold) {
                // Calculate the ratio to snap the node exactly to the threshold distance
                let snapRatio = threshold / distance;

                // Snap the node to the threshold distance from the anchor
                node.x = node.anchorX - dx * snapRatio;
                node.y = node.anchorY - dy * snapRatio;

                // Now apply the velocity based on the new snapped position
                node.vx += (node.anchorX - node.x) * 0.01;
                node.vy += (node.anchorY - node.y) * 0.01;
            } else {
                // Apply the velocity normally if within the threshold
                node.vx += (dx * 0.01);
                node.vy += (dy * 0.01);
            }
        }
    }
}

function textRepelForce(alpha) {
    let strength = -1e9;
    let distanceMin = 10;
    let distanceMax = 10000;

    const nodes = forceGraph.graphData().nodes;
    for (let i = 0; i < nodes.length; i++) {
        if (nodes[i].class != "text") continue;
        let node = nodes[i];

        for (let j = 0; j < nodes.length; j++) {
            if (i != j) continue;
            const other = nodes[j];
            const dx = other.x - node.x;
            const dy = other.y - node.y;
            let distance = Math.sqrt(dx * dx + dy * dy);

            if (distance > distanceMax) continue;

            if (distance < distanceMin) distance = distanceMin;

            const force = (strength / (distance * distance));
            node.vx += dx  *strength;
            node.vy += dy * strength;
        }
    }
}
