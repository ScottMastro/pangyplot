function debounce(func, delay) {
    let debounceTimer;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => func.apply(context, args), delay);
    };
}

function fetchSuggestions(input) {
    fetch(`/search?type=gene&query=${input}`)
        .then(response => response.json())
        .then(data => {
            const suggestionsElement = document.getElementById('suggestions');
            suggestionsElement.innerHTML = data.map((item, index) => `<div class="suggestion-item" tabindex="${index}">${item.name}</div>`).join('');
            suggestionsElement.classList.add('active');
        })
        .catch(error => console.error('Error:', error));
}

function onSuggestionClick(event) {
    selectSuggestionItem(event.target);
}

function selectSuggestionItem(item) {
    if (item.classList.contains('suggestion-item')) {
        const searchBar = document.getElementById('searchBar');
        searchBar.value = item.textContent;
        document.getElementById('suggestions').classList.remove('active');
    }
}

function navigateSuggestions(key) {
    const active = document.activeElement;
    if (key === 'ArrowDown') {
        if (active.classList.contains('suggestion-item')) {
            const next = active.nextElementSibling || active;
            next.focus();
        } else {
            const firstItem = document.querySelector('.suggestion-item');
            if (firstItem) firstItem.focus();
        }
    } else if (key === 'ArrowUp') {
        if (active.classList.contains('suggestion-item')) {
            const prev = active.previousElementSibling || active;
            prev.focus();
        }
    }
}

const searchBar = document.getElementById('searchBar');
searchBar.addEventListener('input', debounce(function() {
    const input = this.value;
    if (input.length > 0) {
        fetchSuggestions(input);
    } else {
        document.getElementById('suggestions').classList.remove('active');
    }
}, 250));

const suggestionsElement = document.getElementById('suggestions');
suggestionsElement.addEventListener('click', onSuggestionClick);

suggestionsElement.addEventListener('keydown', function(event) {
    // Check if the key is alphanumeric (or any other keys you want to include)
    if ((event.key.length === 1 && event.key.match(/\S/)) || event.key === 'Backspace') {
        const searchBar = document.getElementById('searchBar');

        // Focus the search bar
        searchBar.focus();

        // Trigger the input event manually to fetch suggestions based on the updated value
        searchBar.dispatchEvent(new Event('input'));
    }
});

suggestionsElement.addEventListener('wheel', function(event) {
    const deltaY = event.deltaY;
    const contentHeight = this.scrollHeight;
    const visibleHeight = this.offsetHeight;
    const scrollPosition = this.scrollTop;

    // Check if the scroll is at the top or the bottom
    if ((scrollPosition === 0 && deltaY < 0) || (scrollPosition + visibleHeight >= contentHeight && deltaY > 0)) {
        event.preventDefault(); // Prevent scrolling the page
    }
});

document.addEventListener('keydown', function(event) {
    if (['ArrowUp', 'ArrowDown'].includes(event.key)) {
        navigateSuggestions(event.key);
        event.preventDefault(); // Prevent the default scrolling behavior
    }
    if (event.key === 'Enter' && document.activeElement.classList.contains('suggestion-item')) {
        selectSuggestionItem(document.activeElement);
        event.preventDefault(); // Prevent form submission or any other default Enter key behavior
    }
});


