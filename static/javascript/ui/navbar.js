document.getElementById('example-button').addEventListener('click', function() {

    const data = {
        chr: "chr18",
        start: 47506000,
        end: 47600000
    };
    const selectedEvent = new CustomEvent('selectedCoordinatesChanged', { detail: data });
    document.dispatchEvent(selectedEvent);

});

document.getElementById('example-button2').addEventListener('click', function() {

    const data = {
        chr: "chrM",
        start: 1000,
        end: 10000
    };

    const selectedEvent = new CustomEvent('selectedCoordinatesChanged', { detail: data });
    document.dispatchEvent(selectedEvent);

});

document.getElementById('example-button3').addEventListener('click', function() {

    const data = {
        chr: "XXX",
        start: -1000,
        end: 999999999999
    };

    const selectedEvent = new CustomEvent('selectedCoordinatesChanged', { detail: data });
    document.dispatchEvent(selectedEvent);

});