function parseGenomicCoordinates() {
    const textBox = document.getElementById('coordinate-text-box');
    let input = textBox.value.replace(/\s+/g, '');
    
    const pattern = /^(chr)?[^:]+:\d+-\d+$/;
    
    function errorAnimationBadCoordinates() {
        textBox.classList.add('shake', 'error-input');
        textBox.addEventListener('animationend', function() {
            textBox.classList.remove('shake');
            textBox.classList.remove('error-input');
        }, {once: true});
    }

    if (!pattern.test(input)) {
        errorAnimationBadCoordinates();
        return;
    }
    
    let [chr, range] = input.split(':');
    let [start, end] = range.split('-').map(s => parseInt(s, 10));

    if (end < 0 || start < 0) {
        errorAnimationBadCoordinates();
        return;
    }

    if (end < start) {
        errorAnimationBadCoordinates();
        return;
    }

    textBox.value = "";

    const data = {
        chr: chr,
        start: start,
        end: end
    };
    
    const selectedEvent = new CustomEvent('selectedCoordinatesChanged', { detail: data });
    document.dispatchEvent(selectedEvent);
}

document.getElementById('coordinate-button').addEventListener('click', parseGenomicCoordinates);
document.getElementById('coordinate-text-box').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        parseGenomicCoordinates();
    }
});

document.addEventListener('selectedCoordinatesChanged', function(event) {
    const textBox = document.getElementById('coordinate-text-box');
    textBox.value = "";
});

