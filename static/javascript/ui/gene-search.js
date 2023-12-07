const GENE_SEARCH_BAR = "gene-search-bar"
const GENE_SUGGESTIONS = "gene-suggestions"

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
    let chrom = gene.chrom.split("#");
    chrom = chrom[chrom.length - 1];
    let type = gene.gene_type.split("_").join(" ");
    div = `<div class="suggestion-item" tabindex="${index}">
            <div class="suggestion-item-line">
                <div class="suggestion-item-chrom">${chrom}</div>
                <div class="suggestion-item-name">${gene.name}</div>
            </div>
                <div class="suggestion-item-line">
                    <div class="suggestion-item-geneid">${gene.id}</div>
                    <div class="suggestion-item-type">${type}</div>
                </div>
            </div>`;
    return(div);
}

function fetchSuggestions(input) {
    fetch(`/search?type=gene&query=${input}`)
        .then(response => response.json())
        .then(data => {
            const suggestionsElement = document.getElementById(GENE_SUGGESTIONS);
            suggestionsElement.innerHTML = data.map((gene, index) => geneToSearchItem(gene,index)).join('');
            suggestionsElement.classList.add('active');
        })
        .catch(error => console.error('Error:', error));
}

function onSuggestionClick(event) {
    selectSuggestionItem(event.target);
}

function selectSuggestionItem(item) {
    let currentItem = item;
    while (currentItem && !currentItem.classList.contains('suggestion-item')) {
        currentItem = currentItem.parentElement;
    }
    
    if (currentItem) {
        const searchBar = document.getElementById(GENE_SEARCH_BAR);
        const itemName = currentItem.querySelector('.suggestion-item-name');
        console.log(itemName)
        searchBar.value = itemName.textContent;
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
            if (firstItem) firstItem.focus();
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

const searchBar = document.getElementById(GENE_SEARCH_BAR);
searchBar.addEventListener('input', debounce(function() {
    const input = this.value;
    if (input.length > 0) {
        fetchSuggestions(input);
    } else {
        document.getElementById(GENE_SUGGESTIONS).classList.remove('active');
    }
}, 250));

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

const updateSuggestionItemsFocusable = () => {
    document.querySelectorAll('.suggestion-item').forEach(item => {
        item.setAttribute('tabindex', '-1');
    });
};

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


