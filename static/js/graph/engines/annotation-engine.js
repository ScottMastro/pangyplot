const GENE_ANNOTATIONS = [];
const NODE_ANNOTATION_DATA = {};

function processAnnotationData(genes){
    genes.forEach(gene => {
        if (gene.name == "MUC4" || gene.name == "MUC20"){
            GENE_ANNOTATIONS.push(gene);
            console.log(gene.name, gene)
        }
    });
}

//todo: this happenes before processAnnotationData can run
function annotateNode(node) {
    //possible todo:
    //speed up by sorting nodes and genes
    NODE_ANNOTATION_DATA[node.__nodeid] = []

    GENE_ANNOTATIONS.forEach(gene => {

        const transcript = gene.transcripts[0];

        if(annotationOverlap(transcript, node)){
            NODE_ANNOTATION_DATA[node.__nodeid].push(gene.id)
        }

        transcript.exons.forEach(exon => {

            if(annotationOverlap(exon, node)){
                NODE_ANNOTATION_DATA[node.__nodeid].push(exon.id)
            }
            
        })
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