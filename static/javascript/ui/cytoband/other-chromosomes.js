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

function clearAllChrHighlightsOther(){
    let label = document.getElementById("other-chr-label");
    label.classList.remove('text-highlight');
}

document.getElementById('other-chr-selector').addEventListener('change', function() {
    console.log('Selected chromosome:', this.value);
    clearAllChrHighlightsMain();
    clearAllChrHighlightsOther();

    let label = document.getElementById("other-chr-label");
    label.classList.add('text-highlight');
});

