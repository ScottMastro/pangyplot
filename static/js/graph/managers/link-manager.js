const LINK_LENGTH = 10
const LINK_WIDTH = 10
const LINK_FORCE = 10

function flipLink(link) {
    return {
        ...link,
        source: nodeSourceId(link.targetid),
        target: nodeTargetId(link.sourceid),
        fromStrand: link.toStrand,
        toStrand: link.fromStrand,
        sourceid: link.targetid,
        targetid: link.sourceid
    };
}

function processLinks(rawLinks) {
    console.log("rawLinks", rawLinks)
    rawLinks = filterBadLinks(rawLinks);
    
    let links = rawLinks.map(rawLink => ({
        source: nodeSourceId(rawLink["source"]),
        target: nodeTargetId(rawLink["target"]),
        fromStrand: rawLink["from_strand"],
        toStrand: rawLink["to_strand"],
        sourceid: String(rawLink["source"]),
        targetid: String(rawLink["target"]),
        haplotype: rawLink["haplotype"],
        isRef: rawLink.is_ref,
        isDel: rawLink.is_del,
        isVisible: true,
        isDrawn: true,
        class: "edge",
        length: rawLink.is_del ? LINK_LENGTH*2 : LINK_LENGTH,
        force: LINK_FORCE,
        width: LINK_WIDTH,
        annotations: []
    }));

    // Flip for -+ or -- direction          
    const adjustedLinks = links.map(link => {
        if (link.fromStrand === "-") {
            return flipLink(link);
        }
        return link;
    });

    return adjustedLinks;

}
