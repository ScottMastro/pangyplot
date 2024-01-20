var GRAPH_GENOME=null;
var GRAPH_CHROM=null;
var GRAPH_START_POS=null;
var GRAPH_END_POS=null;
var GETTING_SUBGRAPH = new Set();

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

function fetchSubgraph(originNode) {
    const nodeid = originNode.nodeid;

    if (! queueSubgraph(nodeid)){
        return;
    }

    const genome = GRAPH_GENOME;
    const chromosome = GRAPH_CHROM;
    const start = GRAPH_START_POS;
    const end = GRAPH_END_POS;

    const url = buildUrl('/subgraph', {nodeid, genome, chromosome, start, end });

    fetchData(url, 'subgraph').then(fetchedData => {
        dequeueSubgraph(nodeid);

        //graph-manager
        processSubgraphData(fetchedData, originNode)    
    });

}

function fetchGenes(genome, chromosome, start, end) {
    const url = buildUrl('/genes', { genome, chromosome, start, end });

    fetchData(url, 'genes').then(fetchedData => {
        //annotation-manager
        processAnnotationData(fetchedData.genes);
    });
}

function fetchHaps(genome, chromosome, start, end) {
    const url = buildUrl('/haplotypes', { genome, chromosome, start, end });
    return fetchData(url, data => console.log(data), 'haplotypes');
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

function queueSubgraph(nodeid) {
    if (GETTING_SUBGRAPH.has(nodeid)){
        return false;
    }
    GETTING_SUBGRAPH.add(nodeid);
    showLoader();
    return true;
}
function dequeueSubgraph(nodeid) {
    GETTING_SUBGRAPH.delete(nodeid);
    if (GETTING_SUBGRAPH.size === 0) {
        hideLoader();
    }
}

function showLoader() {
    document.querySelector('.loader').style.display = 'block';
    //document.querySelector('.loader-filter').style.display = 'block';
}

function hideLoader() {
    document.querySelector('.loader').style.display = 'none';
    document.querySelector('.loader-filter').style.display = 'none';
}
hideLoader()

