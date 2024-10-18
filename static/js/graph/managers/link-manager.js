const EDGE_LENGTH = 10
const EDGE_WIDTH = 2

function processLinks(rawLinks) {

    rawLinks = filterBadLinks(rawLinks);
    
    return rawLinks.map(rawLink => ({
        source: nodeSourceId(rawLink["source"]),
        target: nodeTargetId(rawLink["target"]),
        sourceid: String(rawLink["source"]),
        targetid: String(rawLink["target"]),
        isRef: rawLink["is_ref"],
        isVisible: true,
        isDrawn: true,
        class: "edge",
        length: EDGE_LENGTH,
        width: EDGE_WIDTH,
        annotations: []
    }));
}

function flipLink(link) {
    return {
        ...link,
        source: nodeSourceId(link.targetid),
        target: nodeTargetId(link.sourceid),
        sourceid: link.targetid,
        targetid: link.sourceid
    };
}

function findDeadEndNodes(links) {
    const edgeLinks = links.filter(link => link.class === "edge");

    const nodeLinkMap = {};
    edgeLinks.forEach(link => {
        const sourceId = link.sourceid;
        const targetId = link.targetid;

        if (!nodeLinkMap[sourceId]) {
            nodeLinkMap[sourceId] = { sources: [], targets: [] };
        }
        if (!nodeLinkMap[targetId]) {
            nodeLinkMap[targetId] = { sources: [], targets: [] };
        }

        nodeLinkMap[sourceId].sources.push(link);
        nodeLinkMap[targetId].targets.push(link);
    });

    const deadEndNodes = Object.entries(nodeLinkMap).filter(([nodeId, linkData]) => {
        const totalLinks = linkData.sources.length + linkData.targets.length;
        const isSourceOnly = linkData.targets.length === 0;
        const isTargetOnly = linkData.sources.length === 0;

        return totalLinks >= 2 && (isSourceOnly || isTargetOnly);
    }).map(([nodeId]) => nodeId);

    return new Set(deadEndNodes);
}

function reorientLinks(graphData) {
    const deadEndNodes = findDeadEndNodes(graphData.links);
    const nodeMap = Object.fromEntries(graphData.nodes.map(node => [node.nodeid, node])); 

    const adjustedLinks = graphData.links.map(link => {
        const sourceId = link.sourceid;
        const targetId = link.targetid;
        if (deadEndNodes.has(sourceId) || deadEndNodes.has(targetId)) {
            const sourceNode = nodeMap[sourceId];
            const targetNode = nodeMap[targetId];

            if (sourceNode && targetNode) {
                // Check if the link needs to be flipped based on dead-end and non-segment conditions
                if (deadEndNodes.has(sourceId) && targetNode.type !== "segment") {
                    return flipLink(link);
                } else if (deadEndNodes.has(targetId) && sourceNode.type !== "segment") {
                    return flipLink(link);
                }
            }
        }

        return link;
    });

    graphData.links = adjustedLinks;
    return graphData;
}