document.getElementById('color-option-button-container').addEventListener('click', function(event) {
  if (event.target.classList.contains('option-button') || event.target.parentNode.classList.contains('option-button')) {
    // Remove 'selected' class from all buttons in the container
    document.querySelectorAll('#color-option-button-container .option-button').forEach(button => {
      button.classList.remove('option-button-selected');
      button.classList.add('option-button-unselected');

    });
    // Add 'selected' class to clicked button
    let targetButton = event.target.classList.contains('option-button') ? event.target : event.target.parentNode;
    targetButton.classList.add('option-button-selected');
    targetButton.classList.remove('option-button-unselected');

  }
});