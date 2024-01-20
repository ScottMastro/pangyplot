PATH_SELECTER="path-selector";
var selectedPath = null;
var pathData = null;

function update_path_selector(paths) {
    
    pathData = paths;
    var pathList = Object.keys(paths);
    var select = document.getElementById(PATH_SELECTER);

    pathList.forEach(function(option) {
        var opt = document.createElement("option");
        opt.value = option;
        opt.textContent = option;

        select.appendChild(opt);
    });

}

function should_highlight_link(link){
    if (selectedPath == null || pathData == null){
        return false;
    }

    for (let i = 0, n = link.pairs.length, pair=null; i < n; ++i) {
        pair = link.pairs[i];
        if (pair[0]=="80810285"){
            console.log(80810285);

        }

        if (selectedPath.hasOwnProperty(pair[0])) {
            if (pair[0]=="80810285"){
                console.log(pair,selectedPath[pair[0]])
            }
            if(selectedPath[pair[0]].includes(pair[1])){
                return true;
            }
        }
    }

    return false;    
}

document.getElementById(PATH_SELECTER).addEventListener('change', function() {
    var selectedOption = this.value;
    console.log("Path selected: ", selectedOption, pathData);
    selectedPath = pathData[selectedOption];
});

function fetchHaps(genome, chromosome, start, end) {
    const url = buildUrl('/haplotypes', { genome, chromosome, start, end });
    return fetchData(url, data => console.log(data), 'haplotypes');
}