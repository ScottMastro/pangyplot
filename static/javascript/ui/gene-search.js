const GENE_SEARCH_BAR = "gene-search-bar"
const GENE_SUGGESTIONS = "gene-suggestions"

const geneTemplate = `
<div class="gene-item-line gene-item-line1">
    <div class="gene-item-chrom">{{chrom}}</div>:
    <div class="gene-item-start">{{start}}</div> -
    <div class="gene-item-end">{{end}}</div>
</div>
<div class="gene-item-line gene-item-line2">
    <div class="gene-item-name">{{name}}</div>
    <div class="gene-item-geneid">{{id}}</div>
</div>
<div class="gene-item-line gene-item-line3">
    <div class="gene-item-type">{{type}}</div>
</div>`

const suggestionTemplate = `
<div class="suggestion-item" tabindex="{{index}}">
    ${geneTemplate}
</div>`;

const selectedTemplate = `
<div class="gene-selection-item">
    ${geneTemplate}
</div>`;


function processTemplate(template, data) {
    return template.replace(/{{\s*(\w+)\s*}}/g, (match, key) => {
        return data[key] || '';
    });
}

function transferAttributes(source, target) {
    if (source && target) {

        target.innerHTML = source.innerHTML;
        
        var attributesToCopy = Array.from(source.attributes).filter(attr => attr.name !== 'id');
        attributesToCopy.forEach(attr => {
            target.setAttribute(attr.name, attr.value);
        });
    }
}

function updateSelectedGenePlaceholders(searchItem){

    var gene1 = document.getElementById('gene-selected-1');
    var gene2 = document.getElementById('gene-selected-2');
    var gene3 = document.getElementById('gene-selected-3');
    var gene4 = document.getElementById('gene-selected-4');

    transferAttributes(gene3, gene4)
    transferAttributes(gene2, gene3)
    transferAttributes(gene1, gene2)
    
    function getTextContent(className){
        const subElement = searchItem.querySelector(className);
        return subElement.textContent;
    }

    let geneData = {
        chrom: getTextContent(".gene-item-chrom"),
        start: getTextContent(".gene-item-start"),
        end: getTextContent(".gene-item-end"),
        name: getTextContent(".gene-item-name"),
        id: getTextContent(".gene-item-geneid"),
        type: getTextContent(".gene-item-type")
    };
    
    gene1.innerHTML = processTemplate(selectedTemplate, geneData);

    gene1.classList.remove('placeholder-blank');
    gene1.classList.add('option-button-selected');
    gene1.classList.remove('option-button-unselected');

    gene2.classList.remove('option-button-selected');
    gene2.classList.add('option-button-unselected');

    gene3.classList.remove('option-button-selected');
    gene3.classList.add('option-button-unselected');
    
    gene4.classList.remove('option-button-selected');
    gene4.classList.add('option-button-unselected');

    
}

function debounce(func, delay) {
    let debounceTimer;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => func.apply(context, args), delay);
    };
}

function geneToSearchItem(gene, index){
    let chrom = gene.chrom.split("#").pop();
    let type = gene.gene_type.split("_").join(" ");

    let geneData = {
        index: index,
        chrom: chrom,
        start: gene.start,
        end: gene.end,
        name: gene.name,
        id: gene.id,
        type: type
    };

    return processTemplate(suggestionTemplate, geneData);
}

function fetchSuggestions(input) {
    fetch(`/search?type=gene&query=${input}`)
        .then(response => response.json())
        .then(data => {
            const suggestionsElement = document.getElementById(GENE_SUGGESTIONS);
            suggestionsElement.setAttribute('tabindex', '-1');
            suggestionsElement.innerHTML = data.map((gene, index) => geneToSearchItem(gene,index)).join('');
            suggestionsElement.classList.add('active');
        })
        .catch(error => console.error('Error:', error));
}

const searchBar = document.getElementById(GENE_SEARCH_BAR);
searchBar.addEventListener('input', debounce(function() {
    const input = this.value;
    if (input.length > 0) {
        fetchSuggestions(input);
    } else {
        document.getElementById(GENE_SUGGESTIONS).classList.remove('active');
    }
}, 250));

function onSuggestionClick(event) {
    selectSuggestionItem(event.target);
}


function selectSuggestionItem(item) {
    let currentItem = item;
    while (currentItem && !currentItem.classList.contains('suggestion-item')) {
        currentItem = currentItem.parentElement;
    }
    
    if (currentItem) {
        updateSelectedGenePlaceholders(currentItem);
        const searchBar = document.getElementById(GENE_SEARCH_BAR);
        searchBar.value = "";
        document.getElementById(GENE_SUGGESTIONS).classList.remove('active');
    }
}

var SWITCH_FOCUS = false;
function navigateSuggestions(key) {
    const active = document.activeElement;
    if (key === 'ArrowDown') {
        if (active.classList.contains('suggestion-item')) {
            const next = active.nextElementSibling || active;
            SWITCH_FOCUS=true;
            next.focus();
            SWITCH_FOCUS=false;
        } else {
            const firstItem = document.querySelector('.suggestion-item');
            if (firstItem) {
                firstItem.setAttribute('tabindex', '-1')
                firstItem.focus();
            }

            if (document.activeElement === firstItem) {
                console.log("firstItem is focused");
            } else {
                console.log("firstItem is not focused");
            }
        }
    } else if (key === 'ArrowUp') {
        if (active.classList.contains('suggestion-item')) {
            const prev = active.previousElementSibling || active;
            SWITCH_FOCUS=true;
            prev.focus();
            SWITCH_FOCUS=false;
        }
    }
}

document.addEventListener('keydown', function(event) {
    if (['ArrowUp', 'ArrowDown'].includes(event.key)) {
        navigateSuggestions(event.key);
        event.preventDefault();
    }
    if (event.key === 'Enter' && document.activeElement.classList.contains('suggestion-item')) {
        selectSuggestionItem(document.activeElement);
        event.preventDefault(); 
    }
});

const suggestionsElement = document.getElementById(GENE_SUGGESTIONS);
suggestionsElement.addEventListener('click', onSuggestionClick);

function isFocusWithinSuggestions() {
    return suggestionsElement.contains(document.activeElement);
}

searchBar.addEventListener('blur', function(event) {
    setTimeout(() => {
        if (!isFocusWithinSuggestions()) {
            suggestionsElement.classList.remove('active');
        }
    }, 0);
});

suggestionsElement.addEventListener('blur', function(event) {

    if (!SWITCH_FOCUS && !isFocusWithinSuggestions()) {
        if (document.activeElement !== searchBar) {
            suggestionsElement.classList.remove('active');
        }
    }
}, true);


suggestionsElement.addEventListener('keydown', function(event) {
    key = event.key;
    if (key === 'ArrowDown' || key === 'ArrowUp') {
        return;
    }

    if ((key.length === 1 && key.match(/\S/)) || key === 'Backspace') {
        const searchBar = document.getElementById(GENE_SEARCH_BAR);
        searchBar.focus();
        searchBar.dispatchEvent(new Event('input'));
    }
});

suggestionsElement.addEventListener('wheel', function(event) {
    const deltaY = event.deltaY;
    const contentHeight = this.scrollHeight;
    const visibleHeight = this.offsetHeight;
    const scrollPosition = this.scrollTop;

    if ((scrollPosition === 0 && deltaY < 0) || (scrollPosition + visibleHeight >= contentHeight && deltaY > 0)) {
        event.preventDefault(); // Prevent scrolling the page
    }
});

