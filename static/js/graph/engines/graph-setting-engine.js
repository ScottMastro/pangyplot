function graphSettingEngineSetup(forceGraph){

    document.getElementById('friction-slider').addEventListener('input', function() {
        const newValue = parseFloat(this.value); 
        forceGraph.d3VelocityDecay(newValue);
        forceGraph.d3ReheatSimulation()
        console.log("friction", newValue)

    });

    document.getElementById('alpha-slider').addEventListener('input', function() {
        const newValue = parseFloat(this.value); 
        forceGraph.d3AlphaDecay(newValue);
        forceGraph.d3ReheatSimulation()
        console.log("alpha", newValue)
    });



    document.getElementById('attraction-slider').addEventListener('input', function() {
                
        const newValue = parseFloat(this.value);
        
        const dist = 1000 - newValue

        forceGraph.d3Force('charge').strength(newValue).distanceMax(dist);
        forceGraph.d3ReheatSimulation()
        console.log("attraction", newValue)

    });

    document.getElementById('collision-slider').addEventListener('input', function() {
                
        const newValue = parseFloat(this.value);
        forceGraph.d3Force('collide', d3.forceCollide(newValue).radius(newValue));
        forceGraph.d3ReheatSimulation()
        console.log("collision", newValue)

    });


    document.getElementById('spread-slider').addEventListener('input', function() {
                
        const newValue = parseFloat(this.value);
        forceGraph.d3Force('spreadX', d3.forceX().strength(newValue).x((d, i) => (i / forceGraph.graphData().nodes.length)));
        forceGraph.d3ReheatSimulation()
        console.log("spread", newValue)

    });


    document.getElementById('pull-slider').addEventListener('input', function() {
                
        const newValue = parseFloat(this.value);
        forceGraph.d3Force('link').distance(newValue).strength(0.9)
        forceGraph.d3ReheatSimulation()
        console.log("pull", newValue)

    });
}