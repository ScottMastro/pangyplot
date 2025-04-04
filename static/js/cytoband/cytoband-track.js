function fetchGenesInRegion(genome, chrom, start, end) {
    const url = `/genes?genome=${genome}&chromosome=${chrom}&start=${start}&end=${end}`;
    return fetch(url)
        .then(res => res.json())
        .then(data => data.genes || [])
        .catch(err => {
            console.error("Gene fetch error:", err);
            return [];
        });
}

function renderCoordinateTrack(chrom, start, end) {
    const svg = d3.select("#cytoband-track-container");
    svg.selectAll("*").remove(); 
    console.log("THIS BE RUNING")
    const width = svg.node().clientWidth;
    const height = +svg.attr("height");
    const margin = { left: 40, right: 40 };
    const usableWidth = width - margin.left - margin.right;

    const xScale = d3.scaleLinear()
        .domain([start, end])
        .range([margin.left, width - margin.right]);

    const intervalSize = 100_000;
    const intervalCount = Math.ceil((end - start) / intervalSize);

    // Draw coordinate intervals
    const intervals = d3.range(start, end, intervalSize);

    const trackGroup = svg.append("g");

    trackGroup.selectAll("rect.interval")
        .data(intervals)
        .enter()
        .append("rect")
        .attr("class", "interval")
        .attr("x", d => xScale(d))
        .attr("y", 0)
        .attr("width", d => Math.max(1, xScale(d + intervalSize) - xScale(d)))
        .attr("height", 20)
        .attr("fill", "#e0e0e0")
        .attr("stroke", "#aaa")
        .style("cursor", "pointer")
        .on("click", d => {
            console.log("Clicked interval:", chrom, d, d + intervalSize);
            // You can trigger a zoom/graph update/etc. here
        });

    // Draw coordinate labels
    trackGroup.selectAll("text.interval-label")
        .data(intervals)
        .enter()
        .append("text")
        .attr("x", d => xScale(d + intervalSize / 2))
        .attr("y", 35)
        .attr("text-anchor", "middle")
        .attr("font-size", "10px")
        .text(d => `${(d / 1e6).toFixed(1)} Mb`);

    // Draw genes
    if (genes.length > 0) {
        const geneTrackY = 45;
        trackGroup.selectAll("rect.gene")
            .data(genes)
            .enter()
            .append("rect")
            .attr("class", "gene")
            .attr("x", d => xScale(d.start))
            .attr("y", geneTrackY)
            .attr("width", d => Math.max(1, xScale(d.end) - xScale(d.start)))
            .attr("height", 10)
            .attr("fill", "#69b3a2");

        // Optional gene labels
        trackGroup.selectAll("text.gene-label")
            .data(genes)
            .enter()
            .append("text")
            .attr("x", d => xScale((d.start + d.end) / 2))
            .attr("y", geneTrackY + 20)
            .attr("text-anchor", "middle")
            .attr("font-size", "10px")
            .text(d => d.name);
    }
}

document.addEventListener('selectedCoordinatesChanged', function(event) {
    console.log("EVENT:",event.detail)
    renderCoordinateTrack(event.detail.chrom, event.detail.start, event.detail.end);    
});
