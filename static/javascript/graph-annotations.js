var GENE_INFO = {};

function calculate_effective_position(node){
    if (!node.hasOwnProperty("start")){
        return null;
    }
    var start = node.start;
    var end = node.end;
    var n = NODEIDS[node.nodeid].length;
    var i = node.__nodeidx;

    if (n === 1){
        return (start+end)/2;
    }
    if (i === n-1){
        return end;
    }

    return (start + i*(end-start)/(n-1));
}

function is_overlap(annotation, node) {
    // TODO: check for chromosome name??
    if (node.start == null){ return false }

    if (node.start <= annotation.end && node.end >= annotation.start){
        var pointPosition = calculate_effective_position(node);
        return pointPosition >= annotation.start && pointPosition <= annotation.end;
    }
}

function update_genes(graph) {

    var geneSet, gid;
    Object.values(GENE_INFO).forEach(gene => {
        geneSet = new Set();
        gid = gene.id;
        graph.nodes.forEach(node => {
            node["genes"] = []
            if(is_overlap(gene, node)){
                geneSet.add(node.__nodeid);
                node.genes.push(gid);
            }
        });

        var source, target;
        graph.links.forEach(link => {
            link["genes"] = [];

            //link could be a link object or simple dictionary
            source = (typeof link.source === 'string') ? link.source : link.source.__nodeid;
            target = (typeof link.target === 'string') ? link.target : link.target.__nodeid;

            // TODO: partial annotation on link?
            if (geneSet.has(source) && geneSet.has(target)){
                link.genes.push(gid);
            }

        });

    });
    return graph;
}

function process_gene_data(data){

    data.genes.forEach(gene => {
        GENE_INFO[gene.id] = gene;
    });

}

function fetch_genes(chromosome, start, end) {

    let url = `/genes?chromosome=${chromosome}&start=${start}&end=${end}`;

    fetch(url)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log("genes", data);
        process_gene_data(data);
    })
    .catch(error => {
        console.error('There was a problem fetching genes:', error);
    });
    
}