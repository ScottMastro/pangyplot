const DEFAULT_CHR="chr1"

function fetchAndDrawGenome(initialChr) {
    let url = "/cytoband?include_order=true";
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState === 4 && xmlHttp.status === 200) {
            var data = JSON.parse(xmlHttp.responseText);
            let order = data.order;
            delete data.order;
            drawGenome(data, order, initialChr);
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send();
}

function fetchAndDrawChromosomeData(chromosome) {
    let url = "/cytoband?chromosome=" + chromosome;
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState === 4 && xmlHttp.status === 200) {
            var data = JSON.parse(xmlHttp.responseText);
            drawChromosome(data[chromosome]);
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send();
}

fetchAndDrawGenome(DEFAULT_CHR);
fetchAndDrawChromosomeData(DEFAULT_CHR);
