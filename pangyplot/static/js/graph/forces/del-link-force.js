REPEL_FROM_DEL_FORCE=-4000;
REPEL_FROM_DEL_MAX_DIST=400;

function repelFromDelLinksAll(alpha) {
    const nodes = forceGraph.graphData().nodes;
    const links = forceGraph.graphData().links;

    const strength = REPEL_FROM_DEL_FORCE; // Adjust repulsion strength
    const distanceMax = REPEL_FROM_DEL_MAX_DIST; // Maximum distance for the force to act

    for (const link of links) {
        if (!link.is_del) continue;

        const x1 = link.source.x;
        const y1 = link.source.y;
        const x2 = link.target.x;
        const y2 = link.target.y;

        for (const node of nodes) {
            const nodeX = node.x;
            const nodeY = node.y;

            // Calculate the perpendicular distance of the node from the link
            const dx = x2 - x1;
            const dy = y2 - y1;
            const len = Math.sqrt(dx * dx + dy * dy);
            const unitDx = dx / len;
            const unitDy = dy / len;
            const projection = ((nodeX - x1) * unitDx + (nodeY - y1) * unitDy);
            const closestX = x1 + projection * unitDx;
            const closestY = y1 + projection * unitDy;
            const distance = Math.sqrt((nodeX - closestX) ** 2 + (nodeY - closestY) ** 2);

            // Apply repulsive force if within range
            if (distance <= distanceMax) {
                const force = strength / (distance * distance);
                const repelX = (nodeX - closestX) / distance;
                const repelY = (nodeY - closestY) / distance;

                node.vx += repelX * force * alpha;
                node.vy += repelY * force * alpha;
            }
        }
    }
}

function repelFromDelLinksDegree(alpha) {
    const links = forceGraph.graphData().links;

    const strength = REPEL_FROM_DEL_FORCE; // Adjust repulsion strength
    const distanceMax = REPEL_FROM_DEL_MAX_DIST; // Maximum distance for the force to act
    const maxDegree = 4; // Maximum degree of separation to consider

    // Build adjacency list for nodes
    const adjacencyList = new Map();
    for (const link of links) {
        if (!adjacencyList.has(link.source)) adjacencyList.set(link.source, []);
        if (!adjacencyList.has(link.target)) adjacencyList.set(link.target, []);
        adjacencyList.get(link.source).push(link.target);
        adjacencyList.get(link.target).push(link.source);
    }

    // Function to get nodes within n degrees of separation
    function getNodesWithinDegrees(startNode, degree) {
        const visited = new Set();
        const queue = [{ node: startNode, depth: 0 }];
        const result = [];

        while (queue.length > 0) {
            const { node, depth } = queue.shift();
            if (depth > degree || visited.has(node)) continue;

            visited.add(node);
            result.push(node);

            for (const neighbor of adjacencyList.get(node) || []) {
                queue.push({ node: neighbor, depth: depth + 1 });
            }
        }
        return result;
    }

    // Process each link with is_del = true
    for (const link of links) {
        if (!link.is_del) continue;

        const x1 = link.source.x;
        const y1 = link.source.y;
        const x2 = link.target.x;
        const y2 = link.target.y;

        // Get nodes within maxDegree of separation
        const nearbyNodes = [
            ...getNodesWithinDegrees(link.source, maxDegree),
            ...getNodesWithinDegrees(link.target, maxDegree)
        ];

        for (const node of nearbyNodes) {
            if (!node || node === link.source || node === link.target) continue;

            const nodeX = node.x;
            const nodeY = node.y;

            // Calculate the perpendicular distance of the node from the link
            const dx = x2 - x1;
            const dy = y2 - y1;
            const len = Math.sqrt(dx * dx + dy * dy);
            const unitDx = dx / len;
            const unitDy = dy / len;
            const projection = ((nodeX - x1) * unitDx + (nodeY - y1) * unitDy);
            const closestX = x1 + projection * unitDx;
            const closestY = y1 + projection * unitDy;
            const distance = Math.sqrt((nodeX - closestX) ** 2 + (nodeY - closestY) ** 2);

            // Apply repulsive force if within range
            if ( distance <= distanceMax) {
                const force = strength / (distance * distance);
                const repelX = (nodeX - closestX) / distance;
                const repelY = (nodeY - closestY) / distance;

                node.vx += repelX * force * alpha;
                node.vy += repelY * force * alpha;
            }
        }
    }
}