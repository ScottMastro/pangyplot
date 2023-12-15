const DEFAULT_CHR="chr1"

function fetchAndDrawGenome(initialChr) {
    let url = "/cytoband?include_order=true";

    return fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok for genome cytoband fetch: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            let order = data.order;
            if (initialChr == null && data.order.length > 0){
                initialChr = data.order[0];
            }
            delete data.order;

            drawGenome(data, order, initialChr);

            if (initialChr != null){
                fetchAndDrawChromosomeData(initialChr);
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });
}


function fetchAndDrawChromosomeData(chrName) {
    let url = `/cytoband?chromosome=${chrName}`;
    
    return fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok for chr fetch: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            drawChromosome(chrName, data[chrName]);
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });
}


fetchAndDrawGenome(null);
