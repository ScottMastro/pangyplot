GRAPH_GENOME=null;
GRAPH_CHROM=null;
GRAPH_START_POS=null;
GRAPH_END_POS=null;

function fetch_genes(genome, chromosome, start, end) {

    let url = `/genes?genome=${genome}&chromosome=${chromosome}&start=${start}&end=${end}`;

    return fetch(url)
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

function fetch_graph(genome, chromosome, start, end) {

    let url = `/select?genome=${genome}&chromosome=${chromosome}&start=${start}&end=${end}`;

    return fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok: during graph fetch');
            }
            return response.json();
        })
        .then(data => {
            console.log("graph", data);
            // TODO
            // update_path_selector(data.paths)
    
            return process_graph_data(data);
        })
        .catch(error => {
            console.error('There was a problem fetching the graph data:', error);
        });
}


function fetch_haps(genome, chromosome, start, end) {

    let url = `/haplotypes?genome=${genome}&chromosome=${chromosome}&start=${start}&end=${end}`;

    return fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
        })
        .catch(error => {
            console.error('There was a problem fetching haplotypes:', error);
        });
    
}

function fetch_subgraph(originNode){
    //showLoader()
    GETTING_SUBGRAPH.add(originNode.nodeid)

    let url = `/subgraph?nodeid=${originNode.nodeid}&genome=${GRAPH_GENOME}&chromosome=${GRAPH_CHROM}&start=${GRAPH_START_POS}&end=${GRAPH_END_POS}`;
    console.log(url)
    return fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(subgraph => {
            graph = FORCE_GRAPH.graphData();
            graph = process_subgraph(subgraph, originNode, graph);
            updateGraphData(graph);
            graph = update_genes(graph);

            GETTING_SUBGRAPH.delete(originNode.nodeid);
            if (GETTING_SUBGRAPH.size === 0) {
                hideLoader();
            }
            HIGHLIGHT_NODE = null;
        })
        .catch(error => {
            GETTING_SUBGRAPH.delete(originNode.nodeid);
            console.error('There was a problem fetching the subgraph:', error);
        });
}


function construct_graph_from_coordinates(genome, chrom, start, end){

    if (genome == GRAPH_GENOME && chrom == GRAPH_CHROM && start == GRAPH_START_POS && end == GRAPH_END_POS){
        return;
    }

    //todo: accomodate other genomes
    GRAPH_GENOME = genome;
    GRAPH_CHROM = chrom;
    GRAPH_START_POS = start;
    GRAPH_END_POS = end;

    console.log("CONSTRUCTING:", genome,chrom,start,end);
    
    let genePromise = fetch_genes(genome, chrom, start, end);
    let graphPromise = fetch_graph(genome, chrom, start, end);


    genePromise.then(() => {
        graphPromise.then(graph => {
            console.log("Received graph data:", graph);
            graph = update_genes(graph);
            draw_graph(graph);

        })
    })
}

document.addEventListener('constructGraph', function(event) {
    const graphElement = document.getElementById('graph-container')    
    graphElement.classList.remove("graph-container-empty");
    graphElement.scrollIntoView({ behavior: 'smooth' });

    //todo: accomodate other genomes
    construct_graph_from_coordinates("CHM13", event.detail.chrom, event.detail.start, event.detail.end);
});


document.addEventListener('DOMContentLoaded', function () {

    //PRSS region
    //const data = { chrom: "chr7", start: "144084904", end: "144140209", source: "testing"  };
    // chr18 region
    const data = { chrom: "chr18", start: "47506000", end: "47600000",  source: "testing" };

    //document.dispatchEvent( new CustomEvent('selectedCoordinatesChanged', { detail: data }));
    document.dispatchEvent(new CustomEvent("constructGraph", { detail: data }));

});