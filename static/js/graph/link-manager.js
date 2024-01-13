const EDGE_LENGTH = 10
const EDGE_WIDTH = 2


function processLinks(rawLinks) {
    return rawLinks.map(rawLink => ({
        source: nodeSourceId(rawLink["source"]),
        target: nodeTargetId(rawLink["target"]),
        sourceid: String(rawLink["source"]),
        targetid: String(rawLink["target"]),
        class: "edge",
        length: EDGE_LENGTH,
        width: EDGE_WIDTH,
        annotations: []
    }));
}
