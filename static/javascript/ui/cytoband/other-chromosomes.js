document.addEventListener('DOMContentLoaded', function() {
    fetch('/chromosomes?noncanonical=true')
        .then(response => response.json())
        .then(data => {
            populateDropdown(data);
        })
        .catch(error => console.error('Error:', error));
});

function populateDropdown(chromosomes) {
    const selector = document.getElementById('other-chr-selector');

    chromosomes.forEach(chromosome => {
        const option = document.createElement('option');
        option.value = chromosome;
        option.textContent = chromosome;
        selector.appendChild(option);
    });
}

document.getElementById('other-chr-selector').addEventListener('change', function(event) {
    let chr = event.target.value;

    const data = {
        chr: chr,
        start: null,
        end: null
    };
    
    const selectedEvent = new CustomEvent('selectedCoordinatesChanged', { detail: data });
    document.dispatchEvent(selectedEvent);
});

document.addEventListener('selectedCoordinatesChanged', function(event) {
    const chrValue = event.detail.chr;
    const selector = document.getElementById('other-chr-selector');
    let optionExists = false;

    // Check if the option exists in the dropdown
    for (let option of selector.options) {
        if (option.value === chrValue) {
            optionExists = true;
            break;
        }
    }

    const label = document.getElementById("other-chr-label");

    if (optionExists) {
        selector.value = chrValue;
        label.classList.add('text-highlight');
    } else {
        label.classList.remove('text-highlight');
    }
});
