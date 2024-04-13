const GENE_ANNOTATIONS = {};
const NODE_ANNOTATION_DATA = {};

function processAnnotationData(genes){
    genes.forEach(gene => {
        GENE_ANNOTATIONS[gene.id] = gene;
        //console.log(gene.name, gene)
    });
}

function annotateNode(node) {
    //possible todo:
    //speed up by sorting nodes and genes
    NODE_ANNOTATION_DATA[node.__nodeid] = []
    Object.values(GENE_ANNOTATIONS).forEach(gene => {
        if (gene.Name == "MUC4"){
            if(annotationOverlap(gene, node)){
                NODE_ANNOTATION_DATA[node.__nodeid].push(gene.id)
            }
        }
    });
}

document.addEventListener("updatedGraphData", function(event) {
    //possible todo:
    //skip nodes already done
    const graph = event.detail.graph;
    graph.nodes.forEach(node => {
        annotateNode(node);
    });
});


function annotationOverlap(annotation, node) {
    // TODO: check for chromosome name??
    if (node.start == null){ return false }

    if (node.start <= annotation.end && node.end >= annotation.start){
        let pointPosition = calculateEffectiveNodePosition(node);
        return pointPosition >= annotation.start && pointPosition <= annotation.end;
    }
}

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


function fetchGenes(genome, chromosome, start, end) {
    const url = buildUrl('/genes', { genome, chromosome, start, end });

    fetchData(url, 'genes').then(fetchedData => {
        processAnnotationData(fetchedData.genes);
    });
}