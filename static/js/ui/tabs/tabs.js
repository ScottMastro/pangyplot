function switchTab(tabId) {
    console.log(tabId)
    var contentDivs = document.getElementsByClassName("tab-content");
    for (var i = 0; i < contentDivs.length; i++) {
        contentDivs[i].classList.remove("active-tab-content"); 
    }

    var activeDiv = document.getElementById(tabId);
    activeDiv.classList.add("active-tab-content");
}
