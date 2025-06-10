let MAJOR_AXIS_X = 1;
let MAJOR_AXIS_Y = 0;

function calculateExtrema(graphData) {
    const nodes = graphData.nodes;

    // Compute direction of max spread (principal axis approximation)
    centroid = computeNodeCentroid(nodes)
    cx = centroid.x
    cy = centroid.y

    let dx = 0, dy = 0;
    for (const n of nodes) {
        dx += (n.x - cx) ** 2;
        dy += (n.y - cy) ** 2;
    }
    
    const magnitude = Math.sqrt(dx * dx + dy * dy);
    if (magnitude === 0) {
        MAJOR_AXIS_X = 1;
        MAJOR_AXIS_Y = 0;
        return;
    }

    MAJOR_AXIS_X = dx / magnitude;
    MAJOR_AXIS_Y = dy / magnitude;

    // Project all nodes onto the axis
    let minProj = Infinity, maxProj = -Infinity;

    nodes.forEach(n => {
    const vx = n.x - centroid.x;
    const vy = n.y - centroid.y;
    const proj = vx * MAJOR_AXIS_X + vy * MAJOR_AXIS_Y;
    n._stressProj = proj;

    if (proj < minProj) minProj = proj;
    if (proj > maxProj) maxProj = proj;
    });

    const range = maxProj - minProj || 1; // avoid divide-by-zero

    nodes.forEach(n => {
        const norm = (n._stressProj - minProj) / range;
        // Map center to 0, ends to 1 (inverted parabolic falloff)
        const distFromCenter = Math.abs(norm - 0.5) * 2;
    n   .extrema = distFromCenter;  // 0 at center, 1 at ends
    });

}
function expansionForce(strength = 0.5) {
  const nodes = forceGraph.graphData().nodes;

  function force(alpha) {
    if (!nodes.length) return;

    // Recompute centroid every tick (for stability during layout)
    let cx = 0, cy = 0;
    for (const n of nodes) {
      cx += n.x;
      cy += n.y;
    }
    cx /= nodes.length;
    cy /= nodes.length;

    for (const node of nodes) {
      const dx = node.x - cx;
      const dy = node.y - cy;

      // Project direction onto the major axis
      const proj = dx * MAJOR_AXIS_X + dy * MAJOR_AXIS_Y;

      const w = node.extrema ?? 0;

      // Move further along axis direction, scaled by strength and extrema
      node.vx += (MAJOR_AXIS_X * proj * strength * w * alpha)/100;
      node.vy += (MAJOR_AXIS_Y * proj * strength * w * alpha)/100;
    }
  }

  force.strength = function(x) {
    if (!arguments.length) return strength;
    strength = x;
    return force;
  };

  return force;
}
