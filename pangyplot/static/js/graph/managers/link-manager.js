const LINK_LENGTH = 10
const LINK_WIDTH = 10

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

function decodeHaplotypeMask(hexString) {
    if (!hexString) return [0];
    
    const mask = BigInt("0x" + hexString.replace(/^0x/, ""));
    const bools = [];
    let i = 0n;
    while ((mask >> i) > 0) {
        bools.push((mask >> i) & 1n ? true : false);
        i += 1n;
    }
    return bools;
}

function processLinks(rawLinks) {
    rawLinks = filterBadLinks(rawLinks);

    let links = rawLinks.map(rawLink => ({
        source: nodeSourceId(rawLink["source"]),
        target: nodeTargetId(rawLink["target"]),
        fromStrand: rawLink["from_strand"],
        toStrand: rawLink["to_strand"],
        sourceid: String(rawLink["source"]),
        targetid: String(rawLink["target"]),
        haplotype: decodeHaplotypeMask(rawLink["haplotype"]),
        isRef: rawLink.ref,
        isDel: rawLink.is_del,
        isVisible: true,
        isDrawn: true,
        class: "edge",
        length: rawLink.is_del ? LINK_LENGTH*2 : LINK_LENGTH,
        width: LINK_WIDTH,
        annotations: []
    }));

    return links

    // Flip for -+ or -- direction          
    const adjustedLinks = links.map(link => {
        if (link.fromStrand === "-") {
            console.log("flip", link)
            return flipLink(link);
        }
        return link;
    });

    return adjustedLinks;

}
