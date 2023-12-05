function search() {
    var query = document.getElementById('gene-search-box').value;
    if (query.length > 0) {
        fetch(`/search?query=${query}`)
            .then(response => response.json())
            .then(data => {
                var datalist = document.getElementById('gene-list');
                datalist.innerHTML = '';  // Clear existing options
                data.forEach(function(item) {
                    var option = document.createElement('option');
                    option.value = item.name;
                    datalist.appendChild(option);
                });
            });
    }
}