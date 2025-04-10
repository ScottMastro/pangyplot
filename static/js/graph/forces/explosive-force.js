EXPLOSIVE_FORCE_INNER_RADIUS = 800
EXPLOSIVE_FORCE_MAX_RADIUS = 3000
EXPLOSIVE_FORCE_STRENGTH = 300

function makeExplosionForce(bombX, bombY) {
    return () => {
        return function explosionForce(alpha) {
            for (const node of forceGraph.graphData().nodes) {
                const dx = node.x - bombX;
                const dy = node.y - bombY;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < EXPLOSIVE_FORCE_MAX_RADIUS && dist > 0) {
                    let pushRatio = 1;

                    if (dist > EXPLOSIVE_FORCE_INNER_RADIUS) {
                        const decayFactor = (dist - EXPLOSIVE_FORCE_INNER_RADIUS) /
                                            (EXPLOSIVE_FORCE_MAX_RADIUS - EXPLOSIVE_FORCE_INNER_RADIUS);
                        pushRatio = Math.exp(-2.5 * decayFactor); // try 1.5–3 for control
                    }

                    const pushStrength = EXPLOSIVE_FORCE_STRENGTH * pushRatio;
                    const normX = dx / dist;
                    const normY = dy / dist;

                    node.vx += normX * pushStrength;
                    node.vy += normY * pushStrength;
                }
            }
        };
    };
}


function triggerExplosion(forceGraph, x, y) {
    console.log("triggerExplosion")
    const bombForce = makeExplosionForce(x, y);
    forceGraph.d3Force('explosion', bombForce());
    // 🔥 Heat up the simulation
    forceGraph.d3ReheatSimulation();

    setTimeout(() => {
        forceGraph.d3Force('explosion', null);
    }, 300); // Let it run for a short burst
}