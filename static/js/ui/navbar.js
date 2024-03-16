document.getElementById('navbar-button-example').addEventListener('click', function() {

    const data = {
        genome: "CHM13",
        chrom: "chr18",
        start: 47506000,
        end: 47600000,
        source:"navbar-example"
    };
    document.dispatchEvent(new CustomEvent('selectedCoordinatesChanged', { detail: data }));
});

document.getElementById('navbar-button-example2').addEventListener('click', function() {

    const data = {
        genome: "CHM13",
        chrom: "chrM",
        start: 1000,
        end: 10000,
        source:"navbar-example"
    };

    document.dispatchEvent(new CustomEvent('selectedCoordinatesChanged', { detail: data }));

});

document.getElementById('navbar-button-example3').addEventListener('click', function() {

    const data = {
        genome: "CHM13",
        chrom: "XXX",
        start: -1000,
        end: 999999999999,
        source:"navbar-example"
    };
    
    document.dispatchEvent(new CustomEvent('selectedCoordinatesChanged', { detail: data }));

});