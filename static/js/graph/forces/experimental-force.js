function xAxisStraighteningForce(strength = 0.05) {
    return () => {
        return function straightenForce(alpha) {
            for (const node of forceGraph.graphData().nodes) {
                node.vy += (-node.y * strength) * alpha;  // pull toward y=0
            }
        };
    };
}

function groupNodesByBubble(nodes) {
    const bubbleGroups = {};

    for (const node of nodes) {

        if (node.bubble != null) {
            if (!bubbleGroups[node.bubble]) {
                bubbleGroups[node.bubble] = [];
            }
            bubbleGroups[node.bubble].push(node);
        }


        if (node.chain != null) {
            if (!bubbleGroups[node.chain]) {
                bubbleGroups[node.chain] = [];
            }
            //bubbleGroups[node.chain].push(node);
        }
    }

    return bubbleGroups;
}
function bubbleCohesionForce(forceGraph, strength = 0.02) {
    return function cohesionForce(alpha) {
        const nodes = forceGraph.graphData().nodes;
        const bubbleGroups = groupNodesByBubble(nodes);

        for (const [bubbleId, group] of Object.entries(bubbleGroups)) {
            if (group.length === 0) continue;
            console.log(bubbleId, group);

            const centerX = d3.mean(group, n => n.x);
            const centerY = d3.mean(group, n => n.y);

            for (const node of group) {
                const dx = centerX - node.x;
                const dy = centerY - node.y;

                node.vx += -dx * strength * alpha;
                node.vy += -dy * strength * alpha;
            }
        }
    };
}

function yAxisDampeningForce(strength = 0.02) {
    return () => {
        return function dampenForce(alpha) {
            const links = forceGraph.graphData().links;

            for (const link of links) {
                const src = link.source;
                const tgt = link.target;

                if (Math.abs(src.x - tgt.x) > Math.abs(src.y - tgt.y)) {
                    // more horizontal link => try to align y-values
                    const dy = (src.y - tgt.y) * 0.5;

                    src.vy -= dy * strength * alpha;
                    tgt.vy += dy * strength * alpha;
                }
            }
        };
    };
}
