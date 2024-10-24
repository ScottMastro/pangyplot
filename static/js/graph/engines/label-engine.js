const LABEL_FONT_SIZE=80;

function LabelEngineUpdate(ctx, forceGraph){
    const zoomFactor = ctx.canvas.__zoom["k"];

    const labelGroups = {};

    forceGraph.graphData().nodes.forEach(node => {
        if (node.label && node.isVisible && node.isDrawn) {
            if (!labelGroups[node.nodeid]) {
            labelGroups[node.nodeid] = { label: node.label, nodes: [] };
          }

          labelGroups[node.nodeid].nodes.push(node);
        }
      });

      Object.keys(labelGroups).forEach(nodeid => {
        const group = labelGroups[nodeid];
        const { label, nodes } = group;
    
        const bounds = findNodeBounds(nodes);
        const x = bounds.x + bounds.width/2;
        const y = bounds.y + bounds.height/2;
        const size = Math.max(LABEL_FONT_SIZE, LABEL_FONT_SIZE * (1 / zoomFactor / 10));
        drawText(label, ctx, x, y, size, "#FFFFFF", "#000000", size / 8);
      });
    }

