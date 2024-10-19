const GENE_ANNOTATIONS = {};
const NODE_ANNOTATION_DATA = {};

const GENE_VISIBLE_BY_DEFAULT = true;

function annotationManagerGetGene(geneId) {
    if (GENE_ANNOTATIONS[geneId]) {
        return GENE_ANNOTATIONS[geneId];
    } else{
        return null
    }
}
function annotationManagerGetGeneColor(geneId) {
    if (GENE_ANNOTATIONS[geneId]) {
        return GENE_ANNOTATIONS[geneId].color;
    } else{
        return "#000000"
    }
}
function annotationManagerGetGeneName(geneId) {
    if (GENE_ANNOTATIONS[geneId]) {
        return GENE_ANNOTATIONS[geneId].gene;
    } else{
        return "undefined"
    }
}
function annotationManagerIsGeneVisible(geneId) {
    if (GENE_ANNOTATIONS[geneId]) {
        return GENE_ANNOTATIONS[geneId].is_visible;
    } else{
        return false;
    }
}

function annotationManagerGetNodeAnnotations(node) {
    const genes = NODE_ANNOTATION_DATA[node.__nodeid];
    return genes ? genes : [] 
}
function annotationManagerGetLinkAnnotations(link) {
    const source = NODE_ANNOTATION_DATA[link.source.__nodeid];
    const target = NODE_ANNOTATION_DATA[link.target.__nodeid];

    if (source && target){
        const sourceSet = new Set(source);
        return target.filter(item => sourceSet.has(item));
    }
    return [];
}


function annotationOverlap(annotation, node) {
    // TODO: check for chromosome name??
    if (node.start == null){ return false }

    if (node.start <= annotation.end && node.end >= annotation.start){
        let pointPosition = calculateEffectiveNodePosition(node);
        return pointPosition >= annotation.start && pointPosition <= annotation.end;
    }
}

function annotationManagerUpdateGeneTable() {
    
    const tableData = [];
    Object.values(GENE_ANNOTATIONS).forEach(gene => {

        const hasTranscripts = gene.transcripts && gene.transcripts.length > 0;
        const hasExons = hasTranscripts && gene.transcripts[0].exons && gene.transcripts[0].exons.length > 0;        
        
        tableData.push({
            id: gene.id,
            name: gene.gene,
            hasExon: hasExons,
            color: gene.color,
            visible: gene.is_visible });
    });

    populateGeneAnnotationsTable(tableData);
}

function annotationManagerUpdatedSelectionFromTable(geneId, status) {
    if (GENE_ANNOTATIONS[geneId]) {
        GENE_ANNOTATIONS[geneId].is_visible = status;
    }
}

function annotationManagerUpdatedColorFromTable(geneId, newColor) {
    if (GENE_ANNOTATIONS[geneId]) {
        GENE_ANNOTATIONS[geneId].color = newColor;
    }
}

function annotationManagerUpdatedExonFromTable(geneId, status) {
    console.log(GENE_ANNOTATIONS);

}


//possible todo:
//speed up by sorting nodes and genes
function annotationManagerAnnotateGraph(graphData) {
    const nodeGroup = {};

    graphData.nodes.forEach(node => {
        NODE_ANNOTATION_DATA[node.__nodeid] = []

        Object.values(GENE_ANNOTATIONS).forEach(gene => {

            const transcript = gene.transcripts[0];

            if(annotationOverlap(transcript, node)){
                NODE_ANNOTATION_DATA[node.__nodeid].push(gene.id)
                
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

    Object.values(GENE_ANNOTATIONS).forEach(gene => {
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

    annotationManagerUpdateGeneTable();
};


function annotationManagerFetch(genome, chromosome, start, end) {
    const url = buildUrl('/genes', { genome, chromosome, start, end });

    Object.keys(GENE_ANNOTATIONS).forEach(key => delete GENE_ANNOTATIONS[key]);

    fetchData(url, 'genes').then(fetchedData => {
        fetchedData.genes.forEach(gene => {

            gene.is_visible = GENE_VISIBLE_BY_DEFAULT;
            gene.color = rgbStringToHex(stringToColor(gene.gene));

            GENE_ANNOTATIONS[gene.id] = gene;
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