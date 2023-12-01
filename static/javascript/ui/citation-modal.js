var modal = document.getElementById("citationModal");
var btn = document.getElementById("citation-button");
var span = document.getElementsByClassName("close")[0];

btn.onclick = function(event) {
    event.preventDefault(); // Prevent default anchor behavior
    modal.style.display = "block";
}

span.onclick = function() {
    modal.style.display = "none";
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
