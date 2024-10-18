const GENE_ANNOTATIONS = [];
const NODE_ANNOTATION_DATA = {};

function annotationOverlap(annotation, node) {
    // TODO: check for chromosome name??
    if (node.start == null){ return false }

    if (node.start <= annotation.end && node.end >= annotation.start){
        let pointPosition = calculateEffectiveNodePosition(node);
        return pointPosition >= annotation.start && pointPosition <= annotation.end;
    }
}

//possible todo:
//speed up by sorting nodes and genes
function annotationManagerAnnotateGraph(graphData) {
    const nodeGroup = {};

    graphData.nodes.forEach(node => {
        NODE_ANNOTATION_DATA[node.__nodeid] = []

        GENE_ANNOTATIONS.forEach(gene => {

            const transcript = gene.transcripts[0];

            if(annotationOverlap(transcript, node)){
                NODE_ANNOTATION_DATA[node.__nodeid].push(gene.gene)
                
                if (!nodeGroup[gene]) {
                    nodeGroup[gene] = [];
                }
                nodeGroup[gene].push(node);
            }

            //todo
            //transcript.exons.forEach(exon => {
            //    if(annotationOverlap(exon, node)){
            //        NODE_ANNOTATION_DATA[node.__nodeid].push(exon.id)
            //    }  
            //})
        });
    });


    GENE_ANNOTATIONS.forEach(gene => {
        const nodes = nodeGroup[gene];
        const bounds = findNodeBounds(nodes);
        
        const rawNode = {
            nodeid: gene.id,
            type: "gene",
            text: gene.gene,
            x: bounds.x + bounds.width / 2,
            y: bounds.y + bounds.height / 2,
        };

        geneTextNode = createNewTextNode(rawNode);
        //todo?
        //graphData.nodes.push(geneTextNode);
    });
        
};

function getNodeAnnotations(node) {
    const genes = NODE_ANNOTATION_DATA[node.__nodeid];
    return genes ? genes : [] 
}
function getLinkAnnotations(link) {
    const source = NODE_ANNOTATION_DATA[link.source.__nodeid];
    const target = NODE_ANNOTATION_DATA[link.target.__nodeid];

    if (source && target){
        const sourceSet = new Set(source);
        return target.filter(item => sourceSet.has(item));
    }
    return [];
}

function annotationManagerFetch(genome, chromosome, start, end) {
    const url = buildUrl('/genes', { genome, chromosome, start, end });

    GENE_ANNOTATIONS.length = 0

    fetchData(url, 'genes').then(fetchedData => {
        fetchedData.genes.forEach(gene => {
            GENE_ANNOTATIONS.push(gene);
            console.log(gene.gene, gene)
        });
    
    });
}

ANNOTATION_UPDATE_FRAME=0;

function annotationManagerUpdate(ctx, forceGraph){
    //todo?
    return;
    if (ANNOTATION_UPDATE_FRAME > 0){
        ANNOTATION_UPDATE_FRAME-=1;
        return
    }
    
    ANNOTATION_UPDATE_FRAME=4;

    const geneNodes = {};
    const geneTextNodes = {};

    forceGraph.graphData().nodes.forEach(node => {
        if (node.class === "text" && node.type === "gene"){
            geneTextNodes[node.text] = node;
        }else if (node.isVisible && node.isDrawn) {
            const genes = getNodeAnnotations(node); 
            
            genes.forEach(geneId => {                
                if (!geneNodes[geneId]) {
                    geneNodes[geneId] = [];
                }
                geneNodes[geneId].push(node);
            });
        }
    });

    Object.keys(geneNodes).forEach(geneId => {
        const nodes = geneNodes[geneId];
        const bounds = findNodeBounds(nodes);
            
        geneTextNodes[geneId].anchorX = bounds.x + bounds.width / 2;
        geneTextNodes[geneId].anchorY = bounds.y + bounds.height / 2;

    });

}