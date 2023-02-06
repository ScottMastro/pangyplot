function fetch(chromosome=null) {

    let url = "/select?chromosome=" + chromosome;
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200){
            var data = JSON.parse(xmlHttp.response)
            console.log(data)
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send();
}

fetch()