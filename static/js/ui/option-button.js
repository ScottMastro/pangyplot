function unselectAllButtons(containerId){
    document.querySelectorAll('#' + containerId + ' .option-button').forEach(button => {
        button.classList.remove('option-button-selected');
        button.classList.add('option-button-unselected');
    });
}

function setupButtonSelectionLogic(containerId) {
  document.getElementById(containerId).addEventListener('click', function(event) {
      if (event.target.classList.contains('option-button') || event.target.parentNode.classList.contains('option-button')) {
          // Remove 'selected' class from all buttons in the container
          unselectAllButtons(containerId)

          // Add 'selected' class to clicked button
          let targetButton = event.target.classList.contains('option-button') ? event.target : event.target.parentNode;
          targetButton.classList.add('option-button-selected');
          targetButton.classList.remove('option-button-unselected');
      }
  });
}

setupButtonSelectionLogic('color-style-container-content');
setupButtonSelectionLogic('color-preset-container-content');
setupButtonSelectionLogic('gene-search-result-container');
