let NUMBER_CHROMOSOMES = null;

function genomeCytobandDimensions() {
    const chrHeight = 180;
    const chrWidth = 10;
    const borderPad = 8;
    const widthPad = 4;
    const topPad = 4;
    const bottomPad = 30;
    const radius = 5;
    const annotationHeight = 20;
    const chrFullHeight = chrHeight + borderPad*2;
    const chrFullWidth = chrWidth + borderPad*2;

    return {
        chrHeight: chrHeight,
        chrWidth: chrWidth,
        borderPad: borderPad,
        widthPad: widthPad,
        topPad: topPad,
        bottomPad: bottomPad,
        chrFullHeight: chrFullHeight,
        chrFullWidth: chrFullWidth,
        radius: radius,
        annotationHeight: annotationHeight,
        bottomPad: bottomPad,
        width: (chrWidth + borderPad * 2 + widthPad) * NUMBER_CHROMOSOMES + widthPad*2,
        height: topPad + chrFullHeight + annotationHeight*2 + bottomPad
    };
}

function updateGenomeCytoband(genomeData, chromOrder, initialChrom) {

    NUMBER_CHROMOSOMES = Object.keys(genomeData).length;
    const svg = drawGenomeCytoband(genomeData, chromOrder)

    if (initialChrom != null){
        highlightGenomeCytoband(initialChrom);
    }
}

function clearHighlightGenomeCytoband(){
    let rectangles = document.getElementsByClassName("cytoband-genome-chromosome");
    for (let i = 0; i < rectangles.length; i++) {
        rectangles[i].classList.remove("cytoband-genome-highlighted");
    }

    let annotations = document.getElementsByClassName("cytoband-genome-annotation")[0].firstElementChild.childNodes;
    for (let i = 0; i < annotations.length; i++) {
        let content = annotations[i].childNodes[2].childNodes[0];
        let bg = content.childNodes[0];

        bg.classList.remove("cytoband-genome-highlighted");
    }
}

function highlightGenomeCytoband(chromName) {
    clearHighlightGenomeCytoband();

    let rectangles = document.getElementsByClassName("cytoband-genome-chromosome");
    let annotations = document.getElementsByClassName("cytoband-genome-annotation")[0].firstElementChild.childNodes;
    for (let i = 0; i < annotations.length; i++) {
        let content = annotations[i].childNodes[2].childNodes[0];
        let bg = content.childNodes[0];
        let label = content.childNodes[1].childNodes[0];

        if (label.textContent === chromName) {
            bg.classList.add("cytoband-genome-highlighted");
            rectangles[i].classList.add("cytoband-genome-highlighted");
        }
    }
}

document.addEventListener('selectedCoordinatesChanged', function(event) {
    highlightGenomeCytoband(event.detail.chrom);
});