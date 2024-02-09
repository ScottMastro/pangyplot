function graphSettingEngineSetup(forceGraph){

    document.getElementById('friction-slider').addEventListener('input', function() {
        const newAlphaDecay = parseFloat(this.value); 
        forceGraph.d3AlphaDecay(newAlphaDecay);
    });

    document.getElementById('velocity-slider').addEventListener('input', function() {
        const newVelocityDecay = parseFloat(this.value); 
        forceGraph.d3VelocityDecay(newVelocityDecay);
    });

}