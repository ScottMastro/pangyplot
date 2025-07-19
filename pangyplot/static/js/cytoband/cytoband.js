function fetchAndDrawGenome(initialChrom) {
    let url = "/cytoband";

    return fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok for genome cytoband fetch: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {

            const chromOrder = data.order;
            if (initialChrom == null && data.order.length > 0){
                initialChrom = data.order[0];
            }
            delete data.order;

            updateGenomeCytoband(data.chromosome, chromOrder, initialChrom, data.organism);

            if (initialChrom != null){
                fetchAndDrawChromosomeData(initialChrom);
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });
}

let CACHED_CHROMOSOME_DATA={}

function fetchAndDrawChromosomeData(chromName, chromStart, chromEnd) {
    if (chromName in CACHED_CHROMOSOME_DATA){
        updateChromosomeCytoband(CACHED_CHROMOSOME_DATA[chromName], chromName, chromStart, chromEnd);
        return;
    }

    let url = `/cytoband?chromosome=${chromName}`;
    return fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok for chr fetch: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            CACHED_CHROMOSOME_DATA[chromName] = data.chromosome;
            updateChromosomeCytoband(data.chromosome, chromName, chromStart, chromEnd);
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });
}


fetchAndDrawGenome(null);
