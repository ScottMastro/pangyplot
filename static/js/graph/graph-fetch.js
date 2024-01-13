GRAPH_GENOME=null;
GRAPH_CHROM=null;
GRAPH_START_POS=null;
GRAPH_END_POS=null;

function buildUrl(base, params) {
    return `${base}?${Object.entries(params).map(([key, value]) => `${key}=${value}`).join('&')}`;
}

function fetchData(url, logLabel = '') {
    return fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Network response was not ok: during ${logLabel}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(logLabel, data);
            return data;
        })
        .catch(error => {
            console.error(`There was a problem with ${logLabel}:`, error);
        });
}

function fetchGraph(genome, chromosome, start, end) {
    const url = buildUrl('/select', { genome, chromosome, start, end });

    fetchData(url, 'graph').then(fetchedData => {
        //graph-manager
        processGraphData(fetchedData);
    });
}

function fetchGenes(genome, chromosome, start, end) {
    const url = buildUrl('/genes', { genome, chromosome, start, end });

    fetchData(url, 'genes').then(fetchedData => {
        //annotation-manager
        processAnnotationData(fetchedData.genes);
    });
}


function fetchSubgraph(originNode, ) {
    const nodeid = originNode.nodeid;
    const genome = GRAPH_GENOME;
    const chromosome = GRAPH_CHROM;
    const start = GRAPH_START_POS;
    const end = GRAPH_END_POS;

    const url = buildUrl('/subgraph', {nodeid, genome, chromosome, start, end });

    fetchData(url, 'subgraph').then(fetchedData => {
        processSubgraphData(fetchedData, originNode)    
    });

}


function fetchHaps(genome, chromosome, start, end) {
    const url = buildUrl('/haplotypes', { genome, chromosome, start, end });
    return fetchData(url, data => console.log(data), 'haplotypes');
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
        })
        .catch(error => {
            GETTING_SUBGRAPH.delete(originNode.nodeid);
            console.error('There was a problem fetching the subgraph:', error);
        });
}


function fetchAndConstructGraph(genome, chrom, start, end){

    if (genome == GRAPH_GENOME && chrom == GRAPH_CHROM && start == GRAPH_START_POS && end == GRAPH_END_POS){
        return;
    }

    //todo: accomodate other genomes
    GRAPH_GENOME = genome;
    GRAPH_CHROM = chrom;
    GRAPH_START_POS = start;
    GRAPH_END_POS = end;

    console.log("CONSTRUCTING:", genome,chrom,start,end);
    
    fetchGenes(genome, chrom, start, end);
    fetchGraph(genome, chrom, start, end);

}

document.addEventListener('constructGraph', function(event) {
    const graphElement = document.getElementById('graph-container')    
    graphElement.classList.remove("graph-container-empty");
    graphElement.scrollIntoView({ behavior: 'smooth' });

    //todo: accomodate other genomes
    fetchAndConstructGraph("CHM13", event.detail.chrom, event.detail.start, event.detail.end);
});


document.addEventListener('DOMContentLoaded', function () {

    //PRSS region
    //const data = { chrom: "chr7", start: "144084904", end: "144140209", source: "testing"  };
    // chr18 region
    const data = { chrom: "chr18", start: "47506000", end: "47600000",  source: "testing" };

    //document.dispatchEvent( new CustomEvent('selectedCoordinatesChanged', { detail: data }));
    document.dispatchEvent(new CustomEvent("constructGraph", { detail: data }));

});