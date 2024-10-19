function switchTab(tabId) {

    var buttonDivs = document.getElementsByClassName("tab-button");
    for (var i = 0; i < buttonDivs.length; i++) {
        buttonDivs[i].classList.remove("active-tab-button"); 
    }
    var contentDivs = document.getElementsByClassName("tab-content");
    for (var i = 0; i < contentDivs.length; i++) {
        contentDivs[i].classList.remove("active-tab-content"); 
    }

    var activeContentDiv = document.getElementById(tabId +"-content");
    activeContentDiv.classList.add("active-tab-content");
    var activeTabDiv = document.getElementById(tabId +"-button");
    activeTabDiv.classList.add("active-tab-button");

}
